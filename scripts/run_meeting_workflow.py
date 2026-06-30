#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
WORKSPACE = SKILL_DIR.parents[2]
PYTHON = sys.executable


REQUIRED_META = [
    "会议主题",
    "会议日期",
    "会议类型",
    "行业/领域",
    "参会角色",
    "音频文件",
    "是否允许本次外部 API 处理",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full meeting audio -> transcript -> minutes workflow.")
    parser.add_argument("--meta", required=True, help="Meeting metadata markdown path")
    parser.add_argument("--output-dir", help="Output directory. Defaults to metadata 输出目录 or workspace.")
    parser.add_argument("--yes", action="store_true", help="User has approved external API processing for this specific run")
    parser.add_argument("--dry-run", action="store_true", help="Validate metadata and print planned outputs without calling APIs")
    parser.add_argument("--skip-asr", action="store_true", help="Skip ASR and use existing transcript from --transcript")
    parser.add_argument("--transcript", help="Existing transcript Markdown path when --skip-asr is used")
    args = parser.parse_args()

    meta = parse_meta(Path(args.meta))
    validate_meta(meta)
    if not args.yes and meta.get("是否允许本次外部 API 处理", "").strip() != "是":
        raise SystemExit("External API processing is not approved. Set metadata to 是 and pass --yes after confirming data path.")

    output_dir = Path(args.output_dir or meta.get("输出目录") or default_output_dir(meta)).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = safe_name(meta.get("会议主题") or Path(meta["音频文件"]).stem)

    env = os.environ.copy()
    load_env_file(WORKSPACE / "doubaoyuyin.env", env)
    load_env_file(WORKSPACE / "豆包TOS配置.env", env)
    load_env_file(WORKSPACE / "deepseek_meeting.env", env)
    load_tos_from_bucket_csv_if_needed(WORKSPACE / "桶信息.csv", env)

    transcript_path = output_dir / f"{stem}_逐字稿.md"
    asr_json_path = output_dir / f"{stem}_asr.json"
    minutes_md_path = output_dir / f"{stem}_会议纪要.md"
    minutes_docx_path = output_dir / f"{stem}_会议纪要.docx"

    if args.dry_run:
        print("OUTPUT_DIR=" + str(output_dir))
        print("TRANSCRIPT=" + str(transcript_path))
        print("ASR_JSON=" + str(asr_json_path))
        print("MINUTES_MD=" + str(minutes_md_path))
        print("MINUTES_DOCX=" + str(minutes_docx_path))
        return 0

    if args.skip_asr:
        if not args.transcript:
            raise SystemExit("--transcript is required with --skip-asr")
        transcript_path = Path(args.transcript)
    else:
        audio = Path(meta["音频文件"]).expanduser()
        if not audio.exists():
            raise SystemExit(f"Audio file not found: {audio}")
        run([
            PYTHON,
            str(SKILL_DIR / "scripts" / "doubao_tos_asr.py"),
            "--audio", str(audio),
            "--out", str(asr_json_path),
            "--markdown-out", str(transcript_path),
        ], env)

    run([
        PYTHON,
        str(SKILL_DIR / "scripts" / "deepseek_minutes.py"),
        "--transcript", str(transcript_path),
        "--minutes-md", str(minutes_md_path),
        "--minutes-docx", str(minutes_docx_path),
        "--topic", meta.get("会议主题", ""),
        "--date", meta.get("会议日期", ""),
        "--participants", meta.get("参会角色", ""),
    ], env)

    print("TRANSCRIPT=" + str(transcript_path))
    print("MINUTES_MD=" + str(minutes_md_path))
    print("MINUTES_DOCX=" + str(minutes_docx_path))
    return 0


def parse_meta(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    meta = {}
    for line in text.splitlines():
        if "：" in line:
            key, value = line.split("：", 1)
        elif ":" in line:
            key, value = line.split(":", 1)
        else:
            continue
        key = key.strip().lstrip("#").strip()
        if key:
            meta[key] = value.strip()
    return meta


def validate_meta(meta: dict) -> None:
    missing = [key for key in REQUIRED_META if not meta.get(key)]
    if missing:
        raise SystemExit("Missing meeting metadata fields: " + ", ".join(missing))


def load_env_file(path: Path, env: dict) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            env[key] = value.strip().strip('"').strip("'")


def load_tos_from_bucket_csv_if_needed(path: Path, env: dict) -> None:
    if env.get("VOLC_ACCESS_KEY_ID") and env.get("VOLC_SECRET_ACCESS_KEY"):
        return
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if len(lines) < 2:
        return
    header = [h.strip() for h in lines[0].split(",")]
    row = lines[1].split(",")
    data = {header[i]: row[i].strip() for i in range(min(len(header), len(row)))}
    if data.get("Access Key ID"):
        env["VOLC_ACCESS_KEY_ID"] = data["Access Key ID"]
    if data.get("Secret Access Key"):
        env["VOLC_SECRET_ACCESS_KEY"] = data["Secret Access Key"]


def safe_name(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "_", value.strip())
    return value or "meeting"


def default_output_dir(meta: dict) -> Path:
    topic = safe_name(meta.get("会议主题", "meeting"))
    date = safe_name(meta.get("会议日期", "unknown-date"))
    return WORKSPACE / f"{topic}-{date}"


def run(cmd, env):
    proc = subprocess.run(cmd, env=env, text=True)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
