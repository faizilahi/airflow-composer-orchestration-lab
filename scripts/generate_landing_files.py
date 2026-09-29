"""Confirm landing extract exists for the local DAG runner."""
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "data" / "landing"
files = list(p.glob("*.csv"))
print(f"landing_files={len(files)}")
for f in files:
    print(" ", f.name)
