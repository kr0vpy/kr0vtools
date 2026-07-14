# KR0VTOOLS — Panel Multi-Tools

Panel integral de pentesting, OSINT, redes, scraping y utilidades con interfaz TUI coloreada. Compatible con **Linux** y **Windows**.

---

## Características ↓

### Discord
| Herramienta | Descripción |
|-------------|-------------|
| Webhook Spammer | Envía mensajes masivos a webhooks con delay configurable |
| Webhook Info | Obtiene información detallada de un webhook |
| Webhook Deleter | Elimina webhooks remotos |
| Webhook Embed | Envía embeds personalizados con color, footer e imagen |
| Webhook Spoof | Modifica nombre y avatar de un webhook |
| Token Generator | Genera tokens con formato Discord (solo broma) |
| Token Verifier | Verifica validez de tokens y muestra datos del usuario |
| Token Mass Checker | Verifica cientos de tokens desde archivo |
| Token Nitro Checker | Revisa suscripciones Nitro activas |
| Token Decoder | Decodifica user ID, timestamp y antigüedad |
| Server Nuker | Spam multi-canal, delete canales, ban all, create canales |

### OSINT
- **IP Info** — Geolocalización, ISP, AS, organización vía ip-api.com
- **IP Logger** — Genera enlaces de rastreo (Grabify / IPLogger)
- **Email Lookup** — Validación y búsqueda de filtraciones (Have I Been Pwned)
- **Phone Lookup** — País, operador, zona horaria vía phonenumbers
- **WHOIS** — Consulta WHOIS de dominios
- **Username Check** — Busca un username en 20+ plataformas (Instagram, GitHub, Reddit, TikTok, etc.)
- **Metadata Extractor** — Extrae metadatos de imágenes, PDFs, audios y videos

###  Network
- **WiFi Scanner** — Escanea redes inalámbricas (nmcli/iw en Linux, netsh en Windows)
- **DNS Lookup** — Consulta A, AAAA, MX, NS, TXT, CNAME
- **Traceroute** — Traza rutas de red (traceroute/tracert según SO)
- **HTTP Headers** — Muestra cabeceras de respuesta HTTP
- **SSL Checker** — Información del certificado SSL (emisor, vigencia, SAN, cipher)
- **MAC Lookup** — Identifica fabricante por dirección MAC
- **Subdomain Finder** — Descubre subdominios por fuerza bruta (wordlist 40+)
- **Directory Brute** — Fuerza bruta de directorios y archivos comunes

### Scanners
- **Port Scanner** — TCP/UDP con detección de servicios y banners
- **Vulnerability Scanner** — SQLi, XSS, Open Redirect, SSTI, Path Traversal, Command Injection, seguridad en cabeceras y paths expuestos

### Utilidades
- **ID Generator** — Genera IDs ofuscados cortos y únicos
- **Hasher** — MD5, SHA1, SHA256
- **Base64 Tool** — Codificar/decodificar
- **Token Decode** — Decodifica tokens Discord sin verificar

### Web Scraping
- Link Extractor, Email Scraper, Meta Tags, Image Downloader

### Social Engineering
- Fake Identity Generator, QR Generator, Link Obfuscator, User-Agent Generator

### Sistema de Plugins
Carga dinámicamente scripts `.py` desde `~/.config/0xytool/plugins/`. Cada plugin necesita `PLUGIN_NAME`, `PLUGIN_DESC` y función `menu()` o `run()`.

---

## Instalación

```bash
git clone https://github.com/kr0vpy/kr0vtools.git
cd kr0vtools
pip install -r requirements.txt
python skeez.py
```

### Windows
Ejecutar `ejecutar.bat` o `python skeez.py`

### Linux
Ejecutar `./ejecutar.sh` o `python3 skeez.py`

### Dependencias opcionales
- `Pillow` — metadatos de imágenes
- `phonenumbers` — lookup telefónico
- `qrcode` — generación de QR
- `mutagen` — metadatos de audio
- `PyPDF2` — metadatos de PDF

---

## 🖥️ Compatibilidad

| Función | Linux | Windows |
|---------|-------|---------|
| Discord tools | ✅ | ✅ |
| OSINT vía HTTP | ✅ | ✅ |
| Port Scanner | ✅ | ✅ |
| Vulnerability Scanner | ✅ | ✅ |
| Web Scraping | ✅ | ✅ |
| Social Engineering | ✅ | ✅ |
| Plugins | ✅ | ✅ |
| WiFi Scanner | ✅ nmcli/iw | ✅ netsh |
| DNS Lookup | ✅ dig | ✅ nslookup + socket |
| Traceroute | ✅ traceroute | ✅ tracert |
| WHOIS | ✅ whois | ✅ vía web |
| Metadata Extractor | ✅ | ✅ |
| ID Generator / Hasher / Base64 | ✅ | ✅ |

---

## Estructura del proyecto

```
kr0vtools/
├── skeez.py                  # Entry point
├── ejecutar.bat              # Lanzador Windows
├── ejecutar.sh               # Lanzador Linux
├── requirements.txt          # Dependencias
├── .gitignore
├── README.md
│
├── tools/
│   ├── base.py               # UI, config, spinner, exportación
│   ├── webhook.py            # Discord webhook tools
│   ├── token.py              # Discord token tools
│   ├── scanner.py            # Port scanner TCP/UDP
│   ├── osint.py              # OSINT tools
│   ├── utils.py              # Utilidades varias
│   ├── network.py            # Network tools
│   ├── web.py                # Web scraping
│   ├── social.py             # Social engineering
│   ├── sqli.py               # Vulnerability scanner
│   ├── nuke.py               # Discord server nuker
│   └── plugins.py            # Sistema de plugins
│
└── tests/
    └── test_tools.py         # Tests unitarios
```

---

## Configuración

Los datos de sesión y configuración se guardan en `~/.config/0xytool/`:

| Archivo | Propósito |
|---------|-----------|
| `config.json` | Preferencias (modo compacto, timeouts, hilos, API keys) |
| `session.log` | Registro de actividad |
| `*.json` / `*.html` | Reportes exportados (scans, vulnerabilidades, subdominios) |

---

## Controles

| Tecla | Acción |
|-------|--------|
| `1-9` | Navegación por menús |
| `0` | Volver al menú anterior |
| `H` | Ayuda |
| `C` | Alternar modo compacto |
| `X` | Salir |
| `Tab` | Autocompletado (Linux) |

---

## Aviso Legal

Esta herramienta es solo para **uso educativo** y **pruebas de seguridad autorizadas**. El uso indebido de esta herramienta para atacar sistemas sin consentimiento es ilegal. El autor no se responsabiliza por el mal uso que se le pueda dar.

---

## Licencia

MIT
