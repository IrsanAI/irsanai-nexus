import os
import re
import shutil
import stat
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

from backend.config import settings


class ClonerError(Exception):
    pass


def _is_writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / '.write_probe'
        probe.write_text('ok', encoding='utf-8')
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def _resolve_work_dir() -> Path:
    configured = settings.work_dir
    candidates = [
        configured,
        Path(tempfile.gettempdir()) / 'irsanai-nexus-work',
        Path.cwd() / '.irsanai-nexus-work',
    ]

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if _is_writable_dir(candidate):
            return candidate

    raise ClonerError(
        'Kein schreibbares Arbeitsverzeichnis gefunden. '
        f'Geprüft: {", ".join(str(c) for c in candidates)}'
    )


def validate_github_url(url: str) -> str:
    pattern = r'^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?$'
    if not re.match(pattern, url):
        raise ClonerError(f'Ungültige oder unsichere GitHub URL: {url}')
    return url.rstrip('/')


def _on_rm_error(func, path, _exc_info):
    """Windows-friendly rmtree handler: make files writable and retry."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def _safe_rmtree(path: Path, attempts: int = 5, delay_seconds: float = 0.2) -> None:
    for attempt in range(1, attempts + 1):
        try:
            shutil.rmtree(path, onerror=_on_rm_error)
            return
        except PermissionError as exc:
            if attempt == attempts:
                raise ClonerError(f'cleanup fehlgeschlagen nach {attempts} Versuchen: {exc}') from exc
            time.sleep(delay_seconds * attempt)


def clone_repo(url: str, job_id: str | None = None) -> Path:
    url = validate_github_url(url)
    job_id = job_id or str(uuid.uuid4())[:8]
    work_dir = _resolve_work_dir()
    target = work_dir / job_id
    if target.exists():
        _safe_rmtree(target)

    try:
        result = subprocess.run(
            ['git', 'clone', '--depth=50', url, str(target)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        if target.exists():
            _safe_rmtree(target)
        raise ClonerError(f'git clone Timeout (120s): {url}') from exc

    if result.returncode != 0:
        raise ClonerError(f'git clone fehlgeschlagen: {result.stderr}')
    return target


def cleanup_repo(path: Path) -> None:
    if path.exists():
        _safe_rmtree(path)
