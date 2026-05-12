import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
SPRINT3_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[3]

for path in (REPO_ROOT, SPRINT3_DIR, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
