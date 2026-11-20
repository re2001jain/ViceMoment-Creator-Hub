# ViceMoment Automation — Setup Guide

Goal: prepare up to 3 original GTA Shorts per day and upload/schedule them to your own YouTube channel.

## Important reality check
- This starter kit does NOT magically find viral moments. Automated scene/action scoring is only a first-pass filter; you must test it against your own gameplay.
- Use your own gameplay or footage with explicit reuse permission. Do not download/repost other creators' videos without rights. Add original commentary/storytelling and meaningful editing; repetitive or reused clips may not be monetizable.
- The video-processing computer must be ON, connected to the internet, and signed in when the local schedule runs. GitHub stores code and the idea tracker; it is not a free video-rendering server.
- Do not upload copyrighted music or other creators' footage.
- Start with PRIVATE uploads for testing. Turn on PUBLIC scheduling only after checking several outputs.

## Recommended architecture
1. Put your own raw gameplay MP4 files in `input/`.
2. Run the local Windows automation on your laptop. FFmpeg makes vertical 1080x1920 clips and writes them to `output/`.
3. The uploader uses YouTube Data API OAuth. It uploads as private and can set `publishAt` for a scheduled release.
4. Keep an archive of source files and generated clips; don't reprocess the same source twice.
5. GitHub `ideas.csv` remains your planning tracker. Never store video files, OAuth tokens, client secrets, or API keys in this public repo.

## Phase 1 — Install free software (Windows 10/11)
1. Install Python 3.11+ from https://www.python.org/downloads/ and tick **Add Python to PATH**.
2. Install FFmpeg from https://ffmpeg.org/download.html and add its `bin` folder to Windows PATH.
3. Open Command Prompt and verify:
   ```bat
   python --version
   ffmpeg -version
   ```
4. Clone this repo:
   ```bat
   git clone https://github.com/re2001jain/ViceMoment-Creator-Hub.git
   cd ViceMoment-Creator-Hub
   ```
5. Install Python packages:
   ```bat
   py -m venv .venv
   .venv\\Scripts\\activate
   pip install -r automation/requirements.txt
   ```

## Phase 2 — Prepare folders
Create these folders beside README:
- `input` — your original gameplay MP4s
- `output` — rendered Shorts
- `archive` — source files already processed
- `logs` — processing/upload logs

Copy your own gameplay MP4 files into `input`. Keep each source at least 60 seconds long. This starter processor selects three evenly spaced candidate windows from a source video; it is NOT an AI viral-moment detector. Review results and adjust the timestamps/selection logic before relying on it.

## Phase 3 — YouTube upload authorization (one-time setup)
1. Open https://console.cloud.google.com/.
2. Create a Google Cloud project and enable **YouTube Data API v3**.
3. Configure the OAuth consent screen for your use.
4. Create an OAuth Client ID of type **Desktop app** and download the JSON file.
5. Rename it to `client_secrets.json` and put it in the repository root on your own computer only.
6. Run the uploader once interactively to authorize your own YouTube channel:
   ```bat
   python automation/uploader.py --auth
   ```
7. A `token.json` file is created. Keep it private. Never commit `client_secrets.json` or `token.json`.

Google may require app verification for some publishing scenarios. If uploads remain private or authorization is blocked, follow the exact notice in Google Cloud/YouTube API Console; do not try to bypass restrictions.

## Phase 4 — Test rendering only
Run:
```bat
python automation/prepare_shorts.py --input input --output output --count 3 --duration 25
``
Inspect every MP4. This starter renderer takes three evenly spaced 25-second windows and adds simple text overlays/vertical blurred background. It does not identify stunts, crashes, missions, or story beats. If the source is 144p, output resolution will be 1080x1920 but visual detail will remain low.

## Phase 5 — Test private upload
After you have checked the rendered clips:
```bat
python automation/uploader.py --folder output --privacy private
``
Only after successful private tests and your review should you use scheduled publishing. For public release, the uploader needs a future publish time and a public privacy status; confirm the YouTube API behavior in your channel before enabling unattended public posting.

## Phase 6 — Schedule on your laptop
Use Windows Task Scheduler:
1. Create Basic Task → Daily.
2. Action: Start a program → Program: path to your Python executable inside `.venv\\Scripts\\python.exe`.
3. Arguments: `automation\\daily_pipeline.py`
4. Start in: the repository folder.
5. Ensure the laptop is plugged in and allow the task to wake the computer if supported.
6. Do not run 3 separate copies at the same time. The script should finish before the next run.

Three uploads/day is a target, not a guarantee. If no suitable original footage is available, the safe behavior is to publish fewer rather than repeat or steal clips.

## Costs and limitations
- Python and FFmpeg are free.
- YouTube Data API upload uses OAuth and has quota/verification rules. See https://developers.google.com/youtube/data/guides/uploading_a_video and https://developers.google.com/youtube/data/guides/authentication.
- This public GitHub repo is for code and planning only. Keep secrets and large video files off GitHub.
- Free services can change limits. This guide does not promise zero cost for every future feature (especially cloud hosting, paid AI voice services, or always-on processing).

## Troubleshooting
- `ffmpeg not found`: fix PATH and reopen Command Prompt.
- OAuth error: check consent screen, OAuth client type, and YouTube Data API v3 enablement.
- Upload fails: check network, quota, channel upload restrictions, and API error details.
- Bad crop: use a higher-resolution source or change the crop settings.
- No good moments: record more original gameplay; don't force low-quality or unrelated clips.
