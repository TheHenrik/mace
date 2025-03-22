import sys
from pathlib import Path


def root() -> Path:
    """
    Determines the root path of the application.

    If the application is running in a frozen state (e.g., packaged by PyInstaller),
    it returns the path to the '_internal' directory within the executable's directory.
    Otherwise, it returns the path to the fourth parent directory of the current file.

    Returns:
        Path: The root path of the application.
    """
    if getattr(sys, "frozen", False):
        application_path = Path(Path(sys.executable).resolve().parent, "_internal")
    elif __file__:
        application_path = Path(__file__).resolve().parents[3]
    return application_path


if __name__ == "__main__":
    print(root())
