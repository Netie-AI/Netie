#!/usr/bin/env bash
# Publish this pack to public Netie-AI/exposure so it can take GitHub stars.
# Run from a clone of Netie-AI/Netie with a token that can create org repos.
# The cloud-agent GitHub App cannot do this (createRepository is denied).
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

if [[ ! -f exposure/pyproject.toml ]]; then
  echo "run from Netie-AI/Netie (exposure/pyproject.toml missing)" >&2
  exit 2
fi

DESC='Cortex-crew marketing pack. Organic LinkedIn/Reddit/GitHub drafts. No fake followers.'

if ! gh repo view Netie-AI/exposure >/dev/null 2>&1; then
  echo "creating public Netie-AI/exposure"
  gh repo create Netie-AI/exposure --public --description "$DESC" --disable-wiki || {
    echo "createRepository denied. Use a founder PAT with org repo-create, then:"
    echo "  git subtree split -P exposure -b exposure-public"
    echo "  git push git@github.com:Netie-AI/exposure.git exposure-public:main"
    exit 3
  }
fi

git subtree split -P exposure -b exposure-public
git push -u "https://github.com/Netie-AI/exposure.git" exposure-public:main
echo "public: https://github.com/Netie-AI/exposure"
