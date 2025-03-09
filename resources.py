##  Begin Standard Imports
# import sys
from pathlib import Path

CONST_ROOT_DIR:Path = Path(__file__).parent.parent
CONST_FRONTEND_DIR:Path = Path.absolute(Path.joinpath(CONST_ROOT_DIR, f"frontend"))
CONST_DATA_DIR:Path = Path.absolute(Path.joinpath(CONST_ROOT_DIR, f"data"))

CONST_DATA_DIR.mkdir(exist_ok=True, parents=True)

FRONTEND_INDEX_PATH = Path.absolute(Path.joinpath(CONST_FRONTEND_DIR, f"index.html"))