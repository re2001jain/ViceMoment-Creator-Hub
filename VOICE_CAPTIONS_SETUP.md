# ViceMoment — Free AI Voice and Captions Setup

This adds offline neural narration and burned-in captions to the muted Shorts rendered by `automation/prepare_shorts.py`.

## 1. Install Piper TTS

Activate the project's virtual environment, then run:

```bat
.venv\Scripts\activate
pip install -r automation/requirements.txt
```

Piper runs locally after its voice model is downloaded. No paid API key is required.

## 2. Download one English voice model

Create a folder named `voices` in the repository root. Download both files below into that folder:

- [en_US-lessac-medium.onnx](https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx)
- [en_US-lessac-medium.onnx.json](https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json)

Keep the two filenames exactly as shown. The model is used locally by Piper.

## 3. Write narration for each Short

After rendering, check the MP4 filenames inside `output\`. For every file, create a matching text file inside `voice_scripts\`.

Example:
- Video: `output\my_gameplay_short_1.mp4`
- Script: `voice_scripts\my_gameplay_short_1.txt`

Keep narration short enough to fit the clip. For a 25-second Short, start with about 35–45 English words. The script must match the filename exactly, except for the `.txt` extension.

Example narration:

```text
This driver thought the road was clear. But watch what happens when the truck turns. One tiny mistake, and the whole situation gets out of control. Would you have reacted in time?
```

## 4. Render voice and captions

Run this after `prepare_shorts.py`:

```bat
python automation/voice_captions.py --input output --output output/final --scripts voice_scripts --model voices/en_US-lessac-medium.onnx
```

The finished videos appear in `output\final\`. Captions are burned into the video. Temporary WAV and SRT files are kept in `output\_voice_work\`.

## 5. Important notes

- This first version uses Piper's English `lessac-medium` voice. Hindi narration and voice selection can be added in a later step.
- Captions are timed from the narration text and generated speech duration. They are not word-level speech recognition, so review timing and spelling before publishing.
- If narration is longer than the Short, the script stops instead of cutting off the voice.
- The daily pipeline uploads only the final folder and keeps uploads PRIVATE.
- The rights gate remains mandatory. Never bypass it for footage, game content, music, or commercial use that has not been cleared.