## Begin Standard Imports
# import sys
from pathlib import Path

CONST_ROOT_DIR:Path = Path(__file__).parent
CONST_DATA_DIR:Path = Path.joinpath(CONST_ROOT_DIR, f".\data")