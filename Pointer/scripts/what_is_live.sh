#!/usr/bin/env bash
# Print what is actually running. Does not check Stripe. Does not deploy.
# Does not submit Devpost. A win is not confirmed.
set -euo pipefail
echo "time_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "stripe_check=skipped (daily only; not this script)"

code="$(curl -sS -o /tmp/pointer-live-health.json -w "%{http_code}" --max-time 2 http://127.0.0.1:7420/health || true)"
if [[ "$code" == "200" ]]; then
  echo "local_daemon=running bind=127.0.0.1:7420 health=200"
else
  echo "local_daemon=down health_http=${code:-none}"
fi

if command -v gcloud >/dev/null 2>&1; then
  echo "gcloud=present"
else
  echo "gcloud=missing"
fi

if [[ -n "${GEMINI_API_KEY:-}${GOOGLE_API_KEY:-}" ]]; then
  echo "gemini_or_google_key=set (value not printed)"
else
  echo "gemini_or_google_key=unset"
fi
OV_HOME="${OPENVAULT_HOME:-$HOME/.openvault}"
if [[ -f "$OV_HOME/keys.db" ]]; then
  echo "openvault_keys_db=present (not read)"
else
  echo "openvault_keys_db=absent host_is_not_laptop_vault"
fi

echo "cloud_run=not_deployed_from_this_vm"
echo "devpost=not_submitted"
echo "auto_join=no"
echo "auto_win=no"
echo "math_research_exam=no (All Things Agentic is build+4min demo)"
echo "pointer_allow_remote=must_stay_unset"

if [[ "$code" != "200" ]]; then
  exit 1
fi
exit 0
