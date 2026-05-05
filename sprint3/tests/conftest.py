import sys
from pathlib import Path

SPRINT3_DIR = Path(__file__).resolve().parents[1]
if str(SPRINT3_DIR) not in sys.path:
    sys.path.insert(0, str(SPRINT3_DIR))
