# Doubao ASR With TOS URL Flow

Use this flow when the user wants domestic low-cost multilingual transcription through Volcengine/Doubao and only has a local audio file.

## Required Data Path

1. Upload local audio to a private Volcengine TOS bucket.
2. Generate a short-lived presigned GET URL.
3. Submit the URL to Doubao recording recognition standard API.
4. Poll the query endpoint until completion.
5. Save transcript locally.
6. Delete the temporary TOS object.

Never use public file-sharing links for confidential recordings unless the user explicitly accepts that risk.

## Official API Shape

Doubao recording recognition standard API:

- Submit: `https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit`
- Query: `https://openspeech.bytedance.com/api/v3/auc/bigmodel/query`
- Resource ID for Doubao recording recognition model 2.0: `volc.seedasr.auc`
- Required headers:
  - `X-Api-App-Key`
  - `X-Api-Access-Key`
  - `X-Api-Resource-Id`
  - `Content-Type: application/json`

The submit call returns task information through response headers. Preserve `X-Api-Status-Code`, `X-Api-Message`, `X-Tt-Logid`, and task id headers for troubleshooting.

For speaker separation, set:

```json
{
  "request": {
    "enable_speaker_info": true,
    "ssd_version": "200"
  }
}
```

Use returned speaker labels such as `speaker: 1` directly. Do not infer human roles from speaker numbers unless metadata and turn-taking make it clear; otherwise keep `【说话人1】`, `【说话人2】`, etc.

## Env Contract

Use `doubaoyuyin.env` for Doubao ASR secrets and `豆包TOS配置.env` for non-secret TOS settings. TOS AK/SK may live in `桶信息.csv` temporarily or should be migrated into a private env file before production use. Do not print or expose secret values.

Required:

```env
DOUBAO_APP_KEY=
DOUBAO_ACCESS_KEY=
VOLC_ACCESS_KEY_ID=
VOLC_SECRET_ACCESS_KEY=
```

Required non-secret TOS settings:

```env
VOLC_TOS_ENDPOINT=
VOLC_TOS_REGION=
VOLC_TOS_BUCKET=
```

Optional:

```env
DOUBAO_RESOURCE_ID=volc.seedasr.auc
TOS_PRESIGN_EXPIRES_SECONDS=7200
```

## Execution Guard

Before running upload or ASR:

- Confirm the exact local file path.
- Confirm the target TOS bucket.
- Confirm presigned URL expiry.
- Confirm the user approves uploading this recording to Volcengine TOS and submitting its URL to Doubao ASR.
