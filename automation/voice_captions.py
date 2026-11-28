import argparse
import re
import shutil
import subprocess
from pathlib import Path


def probe_duration(path):
    raw = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        text=True
    ).strip()
    return float(raw)


def stamp(seconds):
    millis = max(0, int(round(seconds * 1000)))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def caption_chunks(text, max_words=6):
    words = text.split()
    chunks = []
    current = []
    for word in words:
        current.append(word)
        end_sentence = bool(re.search(r"[.!?]$", word))
        if len(current) >= max_words or (end_sentence and len(current) >= 3):
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def write_srt(text, audio_seconds, path):
    chunks = caption_chunks(text)
    if not chunks:
        raise ValueError("Narration text is empty.")
    weights = [max(1, len(chunk)) for chunk in chunks]
    total_weight = sum(weights)
    cursor = 0.0
    lines = []
    for index, (chunk, weight) in enumerate(zip(chunks, weights), start=1):
        end = audio_seconds if index == len(chunks) else cursor + audio_seconds * weight / total_weight
        lines.extend([
            str(index),
            f"{stamp(cursor)} --> {stamp(end)}",
            chunk,
            ""
        ])
        cursor = end
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def escape_filter_path(path):
    return str(path.resolve()).replace("\\", "/").replace(":", r"\\:").replace("'", r"\\'")


def main():
    parser = argparse.ArgumentParser(
        description="Add free local Piper narration and burned-in captions to rendered Shorts."
    )
    parser.add_argument("--input", default="output")
    parser.add_argument("--output", default="output/final")
    parser.add_argument("--scripts", default="voice_scripts")
    parser.add_argument("--model", default="voices/en_US-lessac-medium.onnx")
    args = parser.parse_args()

    piper = shutil.which("piper")
    if not piper:
        raise SystemExit("Piper command not found. Install it with: pip install piper-tts")
    model = Path(args.model)
    if not model.is_file():
        raise SystemExit(
            f"Voice model not found: {model}. Follow VOICE_CAPTIONS_SETUP.md."
        )

    source_dir = Path(args.input)
    output_dir = Path(args.output)
    scripts_dir = Path(args.scripts)
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir = source_dir / "_voice_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    videos = sorted(p for p in source_dir.glob("*.mp4") if p.is_file())
    if not videos:
        print("No rendered MP4 files found. Nothing to voice or caption.")
        return

    missing = [video.stem + ".txt" for video in videos
               if not (scripts_dir / (video.stem + ".txt")).is_file()]
    if missing:
        raise SystemExit(
            "Missing narration script(s) in voice_scripts/: " + ", ".join(missing)
            + ". Create one .txt file for each rendered MP4 before uploading."
        )

    for video in videos:
        narration = (scripts_dir / (video.stem + ".txt")).read_text(
            encoding="utf-8-sig"
        ).strip()
        if not narration:
            raise SystemExit(f"Narration is empty: {scripts_dir / (video.stem + '.txt')}")

        wav = work_dir / f"{video.stem}.wav"
        srt = work_dir / f"{video.stem}.srt"
        final = output_dir / video.name

        subprocess.run(
            [piper, "--model", str(model), "--output_file", str(wav)],
            input=narration, text=True, check=True
        )

        video_seconds = probe_duration(video)
        voice_seconds = probe_duration(wav)
        if voice_seconds > video_seconds:
            raise SystemExit(
                f"Voice for {video.name} is {voice_seconds:.1f}s but the video is "
                f"{video_seconds:.1f}s. Shorten its narration and run again."
            )

        write_srt(narration, voice_seconds, srt)
        subtitle_filter = (
            "subtitles=filename='" + escape_filter_path(srt) +
            "':force_style='FontName=Arial,FontSize=22,Bold=1,"
            "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
            "BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=170'"
        )

        subprocess.run([
            "ffmpeg", "-y", "-i", str(video), "-i", str(wav),
            "-vf", subtitle_filter,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
            "-t", str(video_seconds), "-movflags", "+faststart", str(final)
        ], check=True)

        print(f"Created voice + captions: {final}")

    print(f"Done. Final Shorts are in: {output_dir}")


if __name__ == "__main__":
    main()
