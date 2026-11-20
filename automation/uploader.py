import argparse, os, sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT = Path("client_secrets.json")
TOKEN = Path("token.json")

def service(auth_only=False):
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not CLIENT.exists():
            raise SystemExit("Missing client_secrets.json. Follow automation/AUTOMATION_SETUP.md.")
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT), SCOPES)
        creds = flow.run_local_server(port=0)
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--auth", action="store_true")
    ap.add_argument("--folder", default="output")
    ap.add_argument("--privacy", choices=["private","unlisted"], default="private")
    args = ap.parse_args()
    yt = service()
    if args.auth:
        print("OAuth authorization saved locally.")
        return
    files = sorted(Path(args.folder).glob("*.mp4"))
    if not files:
        print("No MP4 files to upload.")
        return
    for f in files:
        title = f.stem.replace("_", " ")[:95] + " | GTA Shorts #Shorts"
        body = ("Original GTA gameplay edited for ViceMoment.\n"
                "Comment below: would you try this?\n"
                "#GTA #GTAGameplay #GamingShorts #Shorts")
        metadata = {
            "snippet": {"title": title, "description": body,
                        "tags": ["GTA", "GTA gameplay", "gaming shorts"],
                        "categoryId": "20"},
            "status": {"privacyStatus": args.privacy, "selfDeclaredMadeForKids": False}
        }
        media = MediaFileUpload(str(f), mimetype="video/mp4", resumable=True)
        response = yt.videos().insert(part="snippet,status", body=metadata, media_body=media).execute()
        print(f"Uploaded {f.name}: https://youtu.be/{response['id']} (privacy={args.privacy})")
        # Move only after successful upload; keeps a local record and prevents duplicate upload.
        done = Path("archive"); done.mkdir(exist_ok=True)
        f.rename(done / f.name)

if __name__ == "__main__":
    main()
