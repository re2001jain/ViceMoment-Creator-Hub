from pathlib import Path
import subprocess, sys

PY = sys.executable
subprocess.run([PY, "automation/prepare_shorts.py", "--input", "input", "--output", "output", "--count", "3", "--duration", "25"], check=True)
# Safe default: upload as PRIVATE. Public/scheduled publishing should be enabled only
# after you have tested OAuth and verified every generated clip.
subprocess.run([PY, "automation/uploader.py", "--folder", "output", "--privacy", "private"], check=True)
