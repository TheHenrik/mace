from pathlib import Path
import sys

def root() -> Path:
    if getattr(sys, 'frozen', False):
        application_path = Path(Path(sys.executable).resolve().parent, "_internal")
    elif __file__:
        application_path = Path(__file__).resolve().parents[3]
    return application_path


if __name__ == "__main__":
    print(root())