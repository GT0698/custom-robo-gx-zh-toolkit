from pathlib import Path
import sys,unittest
REPO=Path(__file__).resolve().parents[1];sys.path[:0]=[str(REPO/'src/tools'),str(REPO/'scripts')]
from verify_public import public_files
public_files()
suite=unittest.defaultTestLoader.discover(str(REPO/'tests'),pattern='test_*.py');result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
