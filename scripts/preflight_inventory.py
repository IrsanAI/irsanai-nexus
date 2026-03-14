#!/usr/bin/env python3
"""Create a JSON inventory of files/folders for local-vs-remote preflight comparison.

Usage examples:
  python scripts/preflight_inventory.py > preflight.json
  python scripts/preflight_inventory.py --root . --output preflight.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_IGNORES = {
    '.git',
    '.idea',
    '.venv',
    '__pycache__',
    '.mypy_cache',
    '.pytest_cache',
    '.ruff_cache',
    'node_modules',
}


@dataclass
class FileEntry:
    path: str
    size_bytes: int
    mtime_utc: str
    sha256_16: str


@dataclass
class DirEntry:
    path: str


def sha256_16(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def should_skip(path: Path, root: Path, ignore_names: set[str]) -> bool:
    rel_parts = path.relative_to(root).parts
    return any(part in ignore_names for part in rel_parts)


def build_inventory(root: Path, ignore_names: set[str]) -> dict:
    dirs: list[DirEntry] = []
    files: list[FileEntry] = []
    total_size = 0

    for p in sorted(root.rglob('*')):
        if should_skip(p, root, ignore_names):
            continue
        rel = p.relative_to(root).as_posix()
        if p.is_dir():
            dirs.append(DirEntry(path=rel))
            continue
        if p.is_file():
            stat = p.stat()
            total_size += stat.st_size
            files.append(
                FileEntry(
                    path=rel,
                    size_bytes=stat.st_size,
                    mtime_utc=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    sha256_16=sha256_16(p),
                )
            )

    return {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'root': str(root.resolve()),
        'summary': {
            'dir_count': len(dirs),
            'file_count': len(files),
            'total_size_bytes': total_size,
        },
        'dirs': [asdict(d) for d in dirs],
        'files': [asdict(f) for f in files],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.', help='Root folder to scan (default: current directory)')
    parser.add_argument('--output', default='-', help='Output JSON file path or - for stdout')
    parser.add_argument(
        '--ignore',
        action='append',
        default=[],
        help='Additional folder/file names to ignore. Can be passed multiple times.',
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    ignores = set(DEFAULT_IGNORES).union(args.ignore)

    payload = build_inventory(root, ignores)
    content = json.dumps(payload, indent=2, ensure_ascii=False)

    if args.output == '-':
        print(content)
    else:
        Path(args.output).write_text(content, encoding='utf-8')


if __name__ == '__main__':
    main()
