from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.analyzer.unified_analyzer import get_top_files


def test_get_top_files_skips_binary_and_returns_text(tmp_path: Path):
    (tmp_path / 'binary.ico').write_bytes(b'\x00\x01\x02\x03\x04\x05' * 100)
    (tmp_path / 'README.md').write_text('# Hello\nThis is a text file for snippets.\n', encoding='utf-8')

    result = get_top_files(tmp_path, n=5)
    paths = [entry['path'] for entry in result]

    assert 'README.md' in paths
    assert 'binary.ico' not in paths


def test_get_top_files_handles_cp1252_text(tmp_path: Path):
    content = 'Resonanzfähig – Überblick mit Umlauten: äöüß'
    (tmp_path / 'legacy.txt').write_bytes(content.encode('cp1252'))

    result = get_top_files(tmp_path, n=5)
    assert any(item['path'] == 'legacy.txt' for item in result)
