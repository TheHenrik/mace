from pathlib import Path
from pymace.utils.file_path import root

def test_root_returns_path_object():
    r = root()
    assert isinstance(r, Path), "root() should return a Path object"

def test_root_points_to_existing_directory():
    r = root()
    assert r.exists(), "The path returned by root() must exist"
    assert r.is_dir(), "The path returned by root() must be a directory"

def test_root_contains_expected_project_files():
    r = root()
    # At least one of these files should be present in the project root.
    expected_files = ['setup.py', 'pyproject.toml', 'README.md']
    assert any((r / file).exists() for file in expected_files), (
        "The project root should contain at least one of: "
        "setup.py, pyproject.toml, or README.md"
    )

def test_root_with_monkeypatch_chdir(monkeypatch):
    # Test that changing the current working directory doesn't affect root() output.
    original_cwd = Path.cwd()
    try:
        # Change working directory to the parent of the original cwd.
        monkeypatch.chdir(original_cwd.parent)
        r = root()
        assert r.exists() and r.is_dir(), "After changing cwd, root() should still return a valid directory"
    finally:
        monkeypatch.chdir(original_cwd)
