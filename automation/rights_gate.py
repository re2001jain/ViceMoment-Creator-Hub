import csv, sys
from pathlib import Path

ROOT = Path(".")
INPUT = ROOT / "input"
RIGHTS = ROOT / "rights.csv"
REQUIRED = [
    "source_file", "creator", "source_url", "permission_evidence",
    "commercial_use", "editing_allowed", "youtube_allowed", "permission_status"
]
YES = {"YES", "TRUE", "1"}


def main():
    if not RIGHTS.exists():
        print("BLOCKED: rights.csv missing. Copy rights_template.csv to rights.csv and complete it.")
        return 2

    INPUT.mkdir(exist_ok=True)
    available = {
        p.name for p in INPUT.iterdir()
        if p.is_file() and p.suffix.lower() in {".mp4", ".mov", ".mkv"}
    }
    approved = []

    with RIGHTS.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            print("BLOCKED: rights.csv missing columns:", ", ".join(missing))
            return 2

        for row in reader:
            name = (row.get("source_file") or "").strip()
            if not name or name not in available:
                continue

            evidence_name = (row.get("permission_evidence") or "").strip()
            evidence = (ROOT / evidence_name).resolve()
            try:
                evidence.relative_to((ROOT / "permissions").resolve())
            except ValueError:
                print(f"BLOCKED {name}: evidence must be inside permissions/")
                continue

            # Source audio is always removed by prepare_shorts.py (-an).
            # Therefore audio clearance is not required for this muted output.
            flags = [
                row.get(k, "").strip().upper() in YES
                for k in ["commercial_use", "editing_allowed", "youtube_allowed"]
            ]
            approved_status = (row.get("permission_status") or "").strip().upper() == "APPROVED"

            if (
                all(flags) and approved_status and evidence.is_file()
                and row.get("creator", "").strip()
                and row.get("source_url", "").strip()
            ):
                approved.append(name)
            else:
                print(
                    f"NOT APPROVED: {name} "
                    "(check commercial use, editing, YouTube permission, creator/source, "
                    "APPROVED status, and evidence file)"
                )

    (ROOT / "authorized_sources.txt").write_text("\n".join(approved), encoding="utf-8")
    print(f"Rights gate: {len(approved)} approved source(s) out of {len(available)} input file(s).")
    return 0 if approved else 3


if __name__ == "__main__":
    sys.exit(main())
