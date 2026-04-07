"""Root test conftest — ensures OMERODIR is set for tests that need omeroweb."""

import os
from pathlib import Path

# Set OMERODIR before any test imports omeroweb.settings.
# The local omerodir/ directory has the minimal structure needed.
os.environ.setdefault(
    "OMERODIR", str(Path(__file__).resolve().parent.parent / "omerodir")
)
