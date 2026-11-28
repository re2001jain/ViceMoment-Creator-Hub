from pathlib import Path
import subprocess, sys

PY = sys.executable

# Fail closed: if there is no valid written permission evidence, stop here.
subprocess.run([PY, "automation/rights_gate.py"], check=True)

# Render muted vertical gameplay clips.
subprocess.run([
    PY, "automation/prepare_shorts.py",
    "--input", "input", "--output", "output",
    "--count", "3", "--duration", "25"
], check=True)

# Add offline Piper narration and captions. This step fails closed if scripts/model are missing.
subprocess.run([
    PY, "automation/voice_captions.py",
    "--input", "output", "--output", "output/final",
    "--scripts", "voice_scripts",
    "--model", "voices/en_US-lessac-medium.onnx"
], check=True)

# Upload only the finished videos. Safe default remains PRIVATE.
subprocess.run([
    PY, "automation/uploader.py",
    "--folder", "output/final", "--privacy", "private"
], check=True)
