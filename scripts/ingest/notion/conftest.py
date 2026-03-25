import sys
from pathlib import Path

# normalize.py を tests/ から import できるように親ディレクトリを追加
sys.path.insert(0, str(Path(__file__).parent))
