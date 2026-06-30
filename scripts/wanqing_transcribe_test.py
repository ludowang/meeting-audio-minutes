#!/usr/bin/env python3
import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request


API_URL = "https://wanqing-api.corp.kuaishou.com/api/gateway/v1/endpoints/chat/completions"


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Wanqing Qwen3-Omni-Flash audio transcription.")
    parser.add_argument("--audio", required=True, help="Audio file path")
    parser.add_argument("--out", required=True, help="Output text path")
    args = parser.parse_args()

    api_key = os.environ.get("WQ_API_KEY") or os.environ.get("WANQING_API_KEY")
    endpoint_id = os.environ.get("WANQING_ENDPOINT_ID")
    if not api_key or not endpoint_id:
        print("Missing WQ_API_KEY/WANQING_API_KEY or WANQING_ENDPOINT_ID in environment.", file=sys.stderr)
        return 2

    mime_type = mimetypes.guess_type(args.audio)[0] or "audio/mpeg"
    with open(args.audio, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode("ascii")

    payload = {
        "model": endpoint_id,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_b64,
                            "format": "mp3" if mime_type == "audio/mpeg" else mime_type.split("/")[-1],
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "请将这段中文录音转写为忠实逐字稿。"
                            "保留原话措辞，不补全中断，不做数字归一化。"
                            "如果听不清请标注【听不清】。"
                        ),
                    },
                ],
            }
        ],
        "temperature": 0,
    }

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}", file=sys.stderr)
        print(redact(e.read().decode("utf-8", errors="replace")), file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 1

    text = extract_text(result)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")
    print(args.out)
    return 0


def extract_text(result: dict) -> str:
    choices = result.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text") or item.get("content")
                    if isinstance(text, str):
                        parts.append(text)
            if parts:
                return "\n".join(parts)
    return json.dumps(result, ensure_ascii=False, indent=2)


def redact(text: str) -> str:
    for name in ("WANQING_API_KEY", "Authorization", "AccessKey"):
        text = text.replace(name, f"{name}")
    # Wanqing error messages may echo an access key value after "AccessKey:".
    marker = "AccessKey:"
    if marker in text:
        start = text.find(marker) + len(marker)
        end = start
        while end < len(text) and text[end] not in " \t\r\n,.;'\"}":
            end += 1
        text = text[:start] + "[REDACTED]" + text[end:]
    return text


if __name__ == "__main__":
    raise SystemExit(main())
