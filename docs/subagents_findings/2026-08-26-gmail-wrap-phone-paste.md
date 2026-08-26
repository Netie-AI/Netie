# 2026-08-26 Gmail wraps phone-paste URLs

- Date: 2026-08-26 09:57 MYT
- Keywords: google.com/url, Gmail MCP, phone paste, LokalGig, direct URL
- Main idea: Gmail MCP stores a typed `https://netie.ai/hire/` as `https://www.google.com/url?q=https://netie.ai/hire/`. Owner phone pastes must be copied from git or this chat, not from a Gmail HTML body. Source files already had direct URLs. Do not set htmlBody. Do not email pastes to the inbox if the owner will copy from that mail.
- Traps: Old Craigslist #7955885182 in the wrapped Gmail paste is flagged HTTP 410. Live posting is #7955900317. LokalGig still needs phone Turnstile. Do not invent a password.
