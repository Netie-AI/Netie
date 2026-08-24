# 2026-08-24 GitHub org /page/ hire pointer

- Keywords: Spaceship File Manager, netie.ai/page, GitHub org blog, hire redirect
- Main idea: GitHub org `blog` is https://netie.ai/page. That URL was a leftover JS stub. File Manager overwrite of `/page/index.html` now sends visitors to https://netie.ai/hire/. Do not replace the homepage.
- Traps: This token cannot PATCH the GitHub org `blog` field (403). Jupiter editor is still the wrong save path. Do not 302 `/` to `/hire/`. Do not overwrite `/hire/index.html` when fixing `/page/`. 2FA for Spaceship is `alert@spaceship.com`, not SMS.
