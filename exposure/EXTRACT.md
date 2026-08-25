# Extract this pack to a public GitHub repo

This folder is Apache-2.0 and has no dependency on the private Netie estate.
The GitHub App token on `Netie-AI/Netie` cannot create `Netie-AI/exposure`.
A founder with org-create rights:

```bash
cd /path/to/Netie
git subtree split -P exposure -b exposure-public
git push git@github.com:Netie-AI/exposure.git exposure-public:main
```

Create the empty public repo first (Apache-2.0, description: "Cortex-crew marketing pack. Organic LinkedIn/Reddit/GitHub drafts. No fake followers.").

After the push, CI is `/.github/workflows/ci.yml` in this folder (repo root after split).

Stars land on that public repo, not on private `Netie-AI/Netie`.
