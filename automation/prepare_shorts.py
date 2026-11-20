import argparse, subprocess
from pathlib import Path


def duration(path):
    raw = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        text=True
    ).strip()
    return float(raw)


def render(src, dst, start, length, index):
    # Audio is deliberately omitted: no source audio or music is copied to the Short.
    vf = (
        "[0:v]split=2[bg][fg];"
        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=28:12[blur];"
        "[fg]scale=1020:-2:flags=lanczos[front];"
        "[blur][front]overlay=(W-w)/2:(H-h)/2,"
        f"drawtext=text='VICEMOMENT  |  GTA SHORT #{index}':"
        "fontcolor=white:fontsize=46:borderw=4:bordercolor=black:"
        "x=(w-text_w)/2:y=110[outv]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-i", str(src), "-t", str(length),
        "-filter_complex", vf, "-map", "[outv]", "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst)
    ], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="input")
    ap.add_argument("--output", default="output")
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--duration", type=int, default=25)
    args = ap.parse_args()

    inp, out = Path(args.input), Path(args.output)
    inp.mkdir(exist_ok=True, parents=True)
    out.mkdir(exist_ok=True, parents=True)

    allow = Path("authorized_sources.txt")
    if not allow.exists():
        raise SystemExit(
            "BLOCKED: run automation/rights_gate.py first; no approved source list."
        )

    approved = {
        line.strip()
        for line in allow.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    sources = sorted(
        p for p in inp.iterdir()
        if p.is_file() and p.name in approved
        and p.suffix.lower() in {".mp4", ".mov", ".mkv"}
    )

    if not sources:
        print("No rights-approved source videos found. Nothing rendered or uploaded.")
        return

    made = 0
    for src in sources:
        total = duration(src)
        if total < args.duration:
            continue
        count = min(args.count, max(1, int(total // args.duration)))
        starts = [
            max(0, int((total - args.duration) * (i + 1) / (count + 1)))
            for i in range(count)
        ]
        for start in starts:
            if made >= args.count:
                break
            dst = out / f"{src.stem}_short_{made + 1}.mp4"
            if dst.exists():
                continue
            render(src, dst, start, args.duration, made + 1)
            made += 1
        if made >= args.count:
            break

    print(
        f"Rendered {made} candidate Short(s) from rights-approved footage only. "
        "Original source audio was removed."
    )


if __name__ == "__main__":
    main()
