from pathlib import Path
import subprocess, sys

PY=sys.executable
# Fail closed: if there is no valid written permission evidence, stop here.
subprocess.run([PY,"automation/rights_gate.py"],check=True)
subprocess.run([PY,"automation/prepare_shorts.py","--input","input","--output","output","--count","3","--duration","25"],check=True)
# Safe default remains PRIVATE until you separately choose to enable public scheduling.
subprocess.run([PY,"automation/uploader.py","--folder","output","--privacy","private"],check=True)
