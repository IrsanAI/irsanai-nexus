from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.analyzer import cloner



def test_resolve_work_dir_prefers_configured_when_writable(monkeypatch, tmp_path):
    configured = tmp_path / 'configured'
    monkeypatch.setattr(cloner.settings, 'work_dir', configured)
    monkeypatch.setattr(cloner, '_is_writable_dir', lambda p: p == configured)

    resolved = cloner._resolve_work_dir()

    assert resolved == configured


def test_resolve_work_dir_falls_back_when_configured_not_writable(monkeypatch, tmp_path):
    configured = Path('/definitely-not-writable-path')
    monkeypatch.setattr(cloner.settings, 'work_dir', configured)
    monkeypatch.setattr(cloner.tempfile, 'gettempdir', lambda: str(tmp_path / 'tmp'))
    monkeypatch.chdir(tmp_path)

    fallback = tmp_path / '.irsanai-nexus-work'

    def fake_is_writable_dir(path: Path) -> bool:
        return path == fallback

    monkeypatch.setattr(cloner, '_is_writable_dir', fake_is_writable_dir)

    resolved = cloner._resolve_work_dir()

    assert resolved == fallback