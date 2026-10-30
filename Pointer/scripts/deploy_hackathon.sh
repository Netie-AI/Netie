#!/usr/bin/env bash
# Fail-closed Cloud Run deploy for All Things Agentic (P-017).
# Does not set POINTER_ALLOW_REMOTE. Does not print the API key.
# Run from anywhere; uses this script's Pointer/ root.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "${POINTER_ALLOW_REMOTE:-}" == "1" ]]; then
  echo "refusing: POINTER_ALLOW_REMOTE=1 (loopback Pointer only)" >&2
  exit 1
fi

KEY="${GEMINI_API_KEY:-}"
ENVNAME="GEMINI_API_KEY"
if [[ -z "${KEY}" ]]; then
  KEY="${GOOGLE_API_KEY:-}"
  ENVNAME="GOOGLE_API_KEY"
fi
if [[ -z "${KEY}" ]]; then
  echo "refusing: set GEMINI_API_KEY or GOOGLE_API_KEY (OpenVault provider google). Not in git." >&2
  exit 1
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "refusing: gcloud not on PATH. Install Google Cloud SDK, then: gcloud auth login && gcloud config set project YOUR_PROJECT" >&2
  exit 1
fi

REGION="${REGION:-asia-southeast1}"
SERVICE="${SERVICE:-pointer-hackathon}"
SECRET="${SECRET:-pointer-gemini}"

echo "preflight OK. root=$ROOT region=$REGION service=$SERVICE env=$ENVNAME (value not printed)"
echo "GCP service for Devpost: Cloud Run. Pointer daemon stays on 127.0.0.1:7420."
if [[ "${DEPLOY:-}" != "1" ]]; then
  echo "Dry run. On the founder machine with billing enabled:"
  echo "  export DEPLOY=1"
  echo "  bash scripts/deploy_hackathon.sh"
  echo "This will create/update secret $SECRET and deploy $SERVICE with --no-allow-unauthenticated."
  echo "Not a \$1M claim. Individual/Hobbyist is USD 10k x2. Then submit on Devpost."
  exit 0
fi

TMP="$(mktemp)"
cleanup() { rm -f "$TMP"; }
trap cleanup EXIT
printf '%s' "$KEY" > "$TMP"
chmod 600 "$TMP"
if gcloud secrets describe "$SECRET" >/dev/null 2>&1; then
  gcloud secrets versions add "$SECRET" --data-file="$TMP"
else
  gcloud secrets create "$SECRET" --data-file="$TMP"
fi

gcloud run deploy "$SERVICE" \
  --source "$ROOT" \
  --dockerfile hackathon/Dockerfile \
  --region "$REGION" \
  --set-secrets "${ENVNAME}=${SECRET}:latest" \
  --no-allow-unauthenticated

echo "Next: open the .run.app URL, GET /health must be 200 with no missing_gemini_key, then submit https://allthingsagentichackathon.devpost.com/"
echo "Do not set POINTER_ALLOW_REMOTE=1. Demo loopback prove plus this Cloud Run planner."
