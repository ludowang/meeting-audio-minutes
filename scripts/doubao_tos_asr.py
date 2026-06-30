#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import sys
import time
import uuid
import urllib.error
import urllib.request


SUBMIT_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit"
QUERY_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query"
DEFAULT_RESOURCE_ID = "volc.seedasr.auc"


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload local audio to TOS, submit to Doubao ASR, and save transcript.")
    parser.add_argument("--audio", required=True, help="Local audio file path")
    parser.add_argument("--out", required=True, help="Output transcript JSON/text path")
    parser.add_argument("--markdown-out", help="Optional output Markdown transcript path")
    parser.add_argument("--keep-object", action="store_true", help="Do not delete temporary TOS object")
    parser.add_argument("--poll-interval", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()

    cfg = load_config()
    object_key = make_object_key(args.audio)
    uploaded = False

    try:
        audio_url = upload_and_presign(args.audio, object_key, cfg)
        uploaded = True
        task_id, submit_headers = submit_asr(audio_url, cfg)
        result = poll_result(task_id, cfg, args.poll_interval, args.timeout, submit_headers.get("X-Tt-Logid"))
        output = {
            "task_id": task_id,
            "submit_headers": submit_headers,
            "result": result,
        }
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            f.write("\n")
        if args.markdown_out:
            write_markdown(args.markdown_out, result)
        print(args.out)
        return 0
    finally:
        if uploaded and not args.keep_object:
            try:
                delete_object(object_key, cfg)
            except Exception as e:
                print(f"Warning: failed to delete TOS object: {e}", file=sys.stderr)


def load_config() -> dict:
    cfg = {
        "doubao_api_key": env_first("DOUBAO_API_KEY", "X_API_KEY"),
        "doubao_app_key": env_first("DOUBAO_APP_KEY", "VOLC_APP_ID", "X_API_APP_KEY"),
        "doubao_access_key": env_first("DOUBAO_ACCESS_KEY", "VOLC_ACCESS_TOKEN", "X_API_ACCESS_KEY"),
        "doubao_resource_id": os.environ.get("DOUBAO_RESOURCE_ID", DEFAULT_RESOURCE_ID),
        "tos_ak": env_first("VOLC_ACCESS_KEY_ID", "TOS_ACCESS_KEY_ID"),
        "tos_sk": env_first("VOLC_SECRET_ACCESS_KEY", "TOS_SECRET_ACCESS_KEY"),
        "tos_endpoint": env_first("VOLC_TOS_ENDPOINT", "TOS_ENDPOINT"),
        "tos_region": env_first("VOLC_TOS_REGION", "TOS_REGION"),
        "tos_bucket": env_first("VOLC_TOS_BUCKET", "TOS_BUCKET"),
        "expires": int(os.environ.get("TOS_PRESIGN_EXPIRES_SECONDS", "7200")),
    }
    missing = [k for k, v in cfg.items() if v in (None, "") and k not in {"doubao_api_key", "doubao_app_key", "doubao_access_key"}]
    if not cfg["doubao_api_key"] and not (cfg["doubao_app_key"] and cfg["doubao_access_key"]):
        missing.append("doubao_api_key or doubao_app_key+doubao_access_key")
    if missing:
        raise SystemExit("Missing required env variables: " + ", ".join(missing))
    return cfg


def env_first(*names):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def upload_and_presign(audio_path: str, object_key: str, cfg: dict) -> str:
    try:
        import tos
    except ImportError:
        raise SystemExit("Missing Python package 'tos'. Install volcengine TOS Python SDK before running.")

    client = tos.TosClientV2(cfg["tos_ak"], cfg["tos_sk"], cfg["tos_endpoint"], cfg["tos_region"])
    content_type = mimetypes.guess_type(audio_path)[0] or "application/octet-stream"
    with open(audio_path, "rb") as f:
        client.put_object(cfg["tos_bucket"], object_key, content=f, content_type=content_type)

    # The official TOS SDK exposes presign helpers across versions with slightly different names.
    if hasattr(client, "pre_signed_url"):
        return client.pre_signed_url(tos.HttpMethodType.Http_Method_Get, cfg["tos_bucket"], object_key, expires=cfg["expires"]).signed_url
    if hasattr(client, "preSignedURL"):
        return client.preSignedURL("GET", cfg["tos_bucket"], object_key, cfg["expires"]).signed_url
    raise SystemExit("Installed 'tos' package does not expose a known presigned URL method.")


def delete_object(object_key: str, cfg: dict) -> None:
    import tos

    client = tos.TosClientV2(cfg["tos_ak"], cfg["tos_sk"], cfg["tos_endpoint"], cfg["tos_region"])
    client.delete_object(cfg["tos_bucket"], object_key)


def submit_asr(audio_url: str, cfg: dict):
    request_id = str(uuid.uuid4())
    payload = {
        "user": {"uid": "meeting-audio-minutes"},
        "audio": {
            "url": audio_url,
            "format": "mp3",
        },
        "request": {
            "model_name": "bigmodel",
            "enable_itn": False,
            "enable_punc": True,
            "enable_ddc": False,
            "enable_speaker_info": True,
            "ssd_version": "200",
        },
    }
    headers, body = post_json(SUBMIT_URL, payload, volc_headers(cfg, request_id, sequence="-1"))
    status = headers.get("X-Api-Status-Code")
    if status != "20000000":
        raise SystemExit(f"Doubao submit failed: {redact_headers(headers)} {body[:1000]}")
    return request_id, redact_headers(headers)


def poll_result(task_id: str, cfg: dict, interval: int, timeout: int, log_id: str = None):
    deadline = time.time() + timeout
    while time.time() < deadline:
        headers, body = post_json(QUERY_URL, {}, volc_headers(cfg, task_id, log_id=log_id))
        status = headers.get("X-Api-Status-Code")
        if status == "20000000":
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {"raw": body}
        if status and status not in {"20000001", "20000002"}:
            raise SystemExit(f"Doubao query failed: {redact_headers(headers)} {body[:1000]}")
        time.sleep(interval)
    raise SystemExit("Timed out waiting for Doubao ASR result.")


def volc_headers(cfg: dict, request_id: str, sequence: str = None, log_id: str = None) -> dict:
    headers = {
        "X-Api-Resource-Id": cfg["doubao_resource_id"],
        "X-Api-Request-Id": request_id,
        "Content-Type": "application/json",
    }
    if sequence is not None:
        headers["X-Api-Sequence"] = sequence
    if log_id:
        headers["X-Tt-Logid"] = log_id
    if cfg.get("doubao_api_key"):
        headers["X-Api-Key"] = cfg["doubao_api_key"]
    else:
        headers["X-Api-App-Key"] = cfg["doubao_app_key"]
        headers["X-Api-Access-Key"] = cfg["doubao_access_key"]
    return headers


def post_json(url: str, payload: dict, headers: dict):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return dict(resp.headers.items()), body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code}: {body[:1000]}")


def make_object_key(path: str) -> str:
    ext = os.path.splitext(path)[1] or ".mp3"
    return f"meeting-audio-temp/{time.strftime('%Y%m%d')}/{uuid.uuid4().hex}{ext}"


def redact_headers(headers: dict) -> dict:
    redacted = {}
    for key, value in headers.items():
        if key.lower() in {"x-api-access-key", "authorization"}:
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted


def write_markdown(path: str, result: dict) -> None:
    inner = result.get("result", {}) if isinstance(result, dict) else {}
    text = inner.get("text", "") if isinstance(inner, dict) else ""
    utterances = inner.get("utterances", []) if isinstance(inner, dict) else []
    with open(path, "w", encoding="utf-8") as f:
        f.write("# 会议逐字稿\n\n")
        f.write("**转写说明**：由豆包录音文件识别模型生成；保留原始转写措辞，未做数字归一化，未补全中断发言。\n\n")
        if utterances:
            f.write("## 对话转写\n\n")
            for item in utterances:
                start = ms_to_time(item.get("start_time", 0))
                end = ms_to_time(item.get("end_time", 0))
                segment = item.get("text", "").strip()
                speaker = speaker_label(item)
                if segment:
                    f.write(f"【{speaker}】{segment}\n\n")
                    f.write(f"> 时间：{start}-{end}\n\n")
            f.write("\n")
        if text:
            f.write("## 全文\n\n")
            f.write(text.strip() + "\n")


def ms_to_time(value) -> str:
    try:
        ms = int(value)
    except (TypeError, ValueError):
        ms = 0
    seconds = ms // 1000
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def speaker_label(item: dict) -> str:
    for key in ("speaker", "speaker_id", "speaker_id_str", "spk_id", "spkid"):
        value = item.get(key)
        if value not in (None, ""):
            return f"说话人{value}"
    additions = item.get("additions")
    if isinstance(additions, dict):
        for key in ("speaker", "speaker_id", "spk_id"):
            value = additions.get(key)
            if value not in (None, ""):
                return f"说话人{value}"
    return "未知发言人"


if __name__ == "__main__":
    raise SystemExit(main())
