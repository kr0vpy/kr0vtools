# KR0VTOOLS — Multi-Tools Panel

Integral pentesting, OSINT, networking, scraping and utilities panel with a colored TUI interface. Compatible with **Linux** and **Windows**.

---

## Features ↓

### Discord
| Tool | Description |
|-------------|-------------|
| Webhook Spammer | Sends mass messages to webhooks with configurable delay |
| Webhook Info | Gets detailed info from a webhook |
| Webhook Deleter | Deletes remote webhooks |
| Webhook Embed | Sends custom embeds with color, footer and image |
| Webhook Spoof | Changes webhook name and avatar |
| Token Generator | Generates Discord-format tokens (joke only) |
| Token Verifier | Checks token validity and shows user data |
| Token Mass Checker | Verifies hundreds of tokens from file |
| Token Nitro Checker | Checks active Nitro subscriptions |
| Token Decoder | Decodes user ID, timestamp and age |
| Server Nuker | Multi-channel spam, delete channels, ban all, create channels |

### OSINT
- **IP Info** — Geolocation, ISP, AS, organization via ip-api.com
- **IP Logger** — Generates tracking links (Grabify / IPLogger)
- **Email Lookup** — Validation and breach search (Have I Been Pwned)
- **Phone Lookup** — Country, carrier, timezone via phonenumbers
- **WHOIS** — Domain WHOIS lookup
- **Username Check** — Searches a username across 20+ platforms (Instagram, GitHub, Reddit, TikTok, etc.)
- **Metadata Extractor** — Extracts metadata from images, PDFs, audio and video files

### Network
- **WiFi Scanner** — Scans wireless networks (nmcli/iw on Linux, netsh on Windows)
- **DNS Lookup** — Queries A, AAAA, MX, NS, TXT, CNAME records
- **Traceroute** — Traces network routes (traceroute/tracert per OS)
- **HTTP Headers** — Displays HTTP response headers
- **SSL Checker** — SSL certificate info (issuer, validity, SAN, cipher)
- **MAC Lookup** — Identifies manufacturer by MAC address
- **Subdomain Finder** — Discovers subdomains via brute force (40+ wordlist)
- **Directory Brute** — Brute forces common directories and files

### Scanners
- **Port Scanner** — TCP/UDP with service detection and banners
- **Vulnerability Scanner** — SQLi, XSS, Open Redirect, SSTI, Path Traversal, Command Injection, header security and exposed paths

### Utilities
- **ID Generator** — Generates short unique obfuscated IDs
- **Hasher** — MD5, SHA1, SHA256
- **Base64 Tool** — Encode/decode
- **Token Decode** — Decodes Discord tokens without verifying

### Web Scraping
- Link Extractor, Email Scraper, Meta Tags, Image Downloader

### Social Engineering
- Fake Identity Generator, QR Generator, Link Obfuscator, User-Agent Generator

### Plugin System
Dynamically loads `.py` scripts from `~/.config/0xytool/plugins/`. Each plugin needs `PLUGIN_NAME`, `PLUGIN_DESC` and a `menu()` or `run()` function.

---

## Installation

```bash
git clone https://github.com/kr0vpy/kr0vtools.git
cd kr0vtools
pip install -r requirements.txt
python skeez.py
```

### Windows
Run `ejecutar.bat` or `python skeez.py`

### Linux
Run `./ejecutar.sh` or `python3 skeez.py`

### Optional dependencies
- `Pillow` — image metadata
- `phonenumbers` — phone lookup
- `qrcode` — QR generation
- `mutagen` — audio metadata
- `PyPDF2` — PDF metadata

---

## Compatibility

| Feature | Linux | Windows |
|---------|-------|---------|
| Discord tools | ✅ | ✅ |
| OSINT via HTTP | ✅ | ✅ |
| Port Scanner | ✅ | ✅ |
| Vulnerability Scanner | ✅ | ✅ |
| Web Scraping | ✅ | ✅ |
| Social Engineering | ✅ | ✅ |
| Plugins | ✅ | ✅ |
| WiFi Scanner | ✅ nmcli/iw | ✅ netsh |
| DNS Lookup | ✅ dig | ✅ nslookup + socket |
| Traceroute | ✅ traceroute | ✅ tracert |
| WHOIS | ✅ whois | ✅ via web |
| Metadata Extractor | ✅ | ✅ |
| ID Generator / Hasher / Base64 | ✅ | ✅ |

---

## Project structure

```
kr0vtools/
├── skeez.py                  # Entry point
├── ejecutar.bat              # Windows launcher
├── ejecutar.sh               # Linux launcher
├── requirements.txt          # Dependencies
├── .gitignore
├── README.md
│
├── tools/
│   ├── base.py               # UI, config, spinner, export
│   ├── webhook.py            # Discord webhook tools
│   ├── token.py              # Discord token tools
│   ├── scanner.py            # TCP/UDP port scanner
│   ├── osint.py              # OSINT tools
│   ├── utils.py              # Miscellaneous utilities
│   ├── network.py            # Network tools
│   ├── web.py                # Web scraping
│   ├── social.py             # Social engineering
│   ├── sqli.py               # Vulnerability scanner
│   ├── nuke.py               # Discord server nuker
│   └── plugins.py            # Plugin system
│
└── tests/
    └── test_tools.py         # Unit tests
```

---

## Configuration

Session data and config are stored in `~/.config/0xytool/`:

| File | Purpose |
|---------|-----------|
| `config.json` | Preferences (compact mode, timeouts, threads, API keys) |
| `session.log` | Activity log |
| `*.json` / `*.html` | Exported reports (scans, vulnerabilities, subdomains) |

---

## Controls

| Key | Action |
|-------|--------|
| `1-9` | Menu navigation |
| `0` | Go back to previous menu |
| `H` | Help |
| `C` | Toggle compact mode |
| `X` | Exit |
| `Tab` | Autocomplete (Linux) |

---

## Disclaimer

This tool is for **educational purposes** and **authorized security testing only**. Misuse of this tool to attack systems without consent is illegal. The author is not responsible for any misuse.

---

## License

MIT
