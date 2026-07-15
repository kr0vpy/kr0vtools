from tools.base import *
import concurrent.futures
import subprocess
import platform

IS_WIN = platform.system() == "Windows"

def osint_ip():
    limpiar(); barra_menu("OSINT - IP INFO")
    ip = input(f"  {R2}IP Address{RS} > ").strip()
    if not ip: return pausa()
    print()
    try:
        req = urllib.request.Request(f"http://ip-api.com/json/{ip}?fields=66846719", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as r: d = json.loads(r.read().decode())
        if d.get("status") == "fail": print(f"  {D}[!] Invalid or not found IP{RS}")
        else:
            for nombre, key in [("IP","query"),("ISP","isp"),("Org","org"),("AS","as"),
                ("Country","country"),("Region","regionName"),("City","city"),("Zip","zip"),
                ("Lat","lat"),("Lon","lon"),("Timezone","timezone")]:
                print(f"  {R2}{nombre+':':<15}{RS} {W}{d.get(key, 'N/A')}{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def osint_ip_logger():
    limpiar(); barra_menu("OSINT - IP LOGGER")
    print(f"  {D}Creates a link to track the visitor's IP.{RS}\n")
    url_destino = input(f"  {R2}Destination URL{RS} > ").strip()
    if not url_destino: return pausa()
    print(f"\n  {R2}Services:{RS}")
    print(f"    {W}[1] grabify.link{RS}")
    print(f"    {W}[2] iplogger.org{RS}")
    serv = input(f"\n  {R2}Select{RS} > ").strip()
    if serv == "1":
        link = f"https://grabify.link/{base64.urlsafe_b64encode(url_destino.encode()).decode().rstrip('=')[:8]}"
    elif serv == "2":
        link = f"https://iplogger.org/2b{base64.urlsafe_b64encode(url_destino.encode()).decode().rstrip('=')[:6]}"
    else: print(f"  {D}[!] Invalid option{RS}"); return pausa()
    print(f"\n  {R1}[+] Generated link:{RS}")
    print(f"  {W}{link}{RS}")
    pausa()

def osint_email():
    limpiar(); barra_menu("OSINT - EMAIL LOOKUP")
    email = input(f"  {R2}Email{RS} > ").strip()
    if not email or "@" not in email: return pausa()
    print(f"\n  {D}[+] Looking up info...{RS}\n")
    dominio = email.split("@")[1]
    print(f"  {R2}Email:{RS}    {W}{email}{RS}")
    print(f"  {R2}Domain:{RS}   {W}{dominio}{RS}")
    print(f"  {R2}User:{RS}   {W}{email.split('@')[0]}{RS}")
    try:
        req = urllib.request.Request(f"https://isitarealemail.com/api/email/validate?email={email}", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read().decode())
            print(f"  {R2}Estado:{RS}    {W}{d.get('status', 'unknown')}{RS}")
    except: print(f"  {D}[!] Could not validate{RS}")
    try:
        req2 = urllib.request.Request(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", headers={"User-Agent": UA})
        with urllib.request.urlopen(req2, timeout=10) as r:
            breaches = json.loads(r.read().decode())
            if breaches:
                print(f"  {D}Breaches: {len(breaches)}{RS}")
                for b in breaches[:5]: print(f"    - {b.get('Name', '?')} ({b.get('BreachDate', '?')})")
    except: pass
    pausa()

def osint_phone():
    limpiar(); barra_menu("OSINT - PHONE LOOKUP")
    numero = input(f"  {R2}Number (+code, eg: +521234567890){RS} > ").strip()
    if not numero: return pausa()
    print()
    try:
        import phonenumbers
        from phonenumbers import carrier, geocoder, timezone
        num = phonenumbers.parse(numero)
        valido = phonenumbers.is_valid_number(num)
        print(f"  {R2}Number:{RS}  {W}{numero}{RS}")
        print(f"  {R2}Valid:{RS}  {W}{valido}{RS}")
        if valido:
            print(f"  {R2}Country:{RS}     {W}{geocoder.description_for_number(num, 'es')}{RS}")
            print(f"  {R2}Region:{RS}   {W}{geocoder.description_for_valid_number(num, 'es')}{RS}")
            print(f"  {R2}Carrier:{RS} {W}{carrier.name_for_number(num, 'es')}{RS}")
            print(f"  {R2}Timezone:{RS}     {W}{', '.join(timezone.time_zones_for_number(num))}{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def osint_whois():
    limpiar(); barra_menu("OSINT - WHOIS")
    dominio = input(f"  {R2}Domain (eg: google.com){RS} > ").strip()
    if not dominio: return pausa()
    print(f"\n  {D}[+] Looking up WHOIS...{RS}\n")
    if IS_WIN:
        try:
            req = urllib.request.Request(f"https://who.is/whois/{dominio}", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as r:
                html = r.read().decode("utf-8", errors="ignore")
                match = re.search(r'(?i)<pre[^>]*id=["\']df-raw["\'][^>]*>(.*?)</pre>', html, re.DOTALL)
                if match:
                    print(f"  {W}{match.group(1).strip()[:1500]}{RS}")
                else:
                    lines = re.findall(r'(?i)(Domain Name|Registrar|Creation Date|Expir|Name Server):[^<]+', html)
                    if lines:
                        for l in lines[:30]:
                            print(f"  {W}{l.strip()}{RS}")
                    else:
                        print(f"  {D}[!] Could not get WHOIS data via web{RS}")
        except Exception as e:
            print(f"  {D}[!] Error: {e}{RS}")
            print(f"  {D}Tip: Install whois via 'choco install whois' or use who.is in your browser{RS}")
    else:
        try:
            import subprocess
            res = subprocess.run(["whois", dominio], capture_output=True, text=True, timeout=15)
            if res.returncode == 0 and res.stdout.strip(): print(f"  {W}{res.stdout[:1500]}{RS}")
            else: print(f"  {D}[!] No data found{RS}")
        except FileNotFoundError: print(f"  {D}[!] whois not installed. Install: sudo apt install whois{RS}")
        except subprocess.TimeoutExpired: print(f"  {D}[!] Timeout{RS}")
        except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

PLATAFORMAS = [
    ("Instagram",  "https://instagram.com/{}"),
    ("X / Twitter","https://twitter.com/{}"),
    ("GitHub",     "https://github.com/{}"),
    ("Reddit",     "https://reddit.com/u/{}"),
    ("TikTok",     "https://tiktok.com/@{}"),
    ("YouTube",    "https://youtube.com/@{}"),
    ("Telegram",   "https://t.me/{}"),
    ("Pinterest",  "https://pinterest.com/{}"),
    ("Twitch",     "https://twitch.tv/{}"),
    ("Medium",     "https://medium.com/@{}"),
    ("Dev.to",     "https://dev.to/{}"),
    ("Flickr",     "https://flickr.com/people/{}"),
    ("Tumblr",     "https://{}.tumblr.com"),
    ("Steam",      "https://steamcommunity.com/id/{}"),
    ("Keybase",    "https://keybase.io/{}"),
    ("Mastodon",   "https://mastodon.social/@{}"),
    ("Replit",     "https://replit.com/@{}"),
    ("SoundCloud", "https://soundcloud.com/{}"),
    ("Behance",    "https://behance.net/{}"),
    ("Dribbble",   "https://dribbble.com/{}"),
]

def osint_username():
    limpiar(); barra_menu("OSINT - USERNAME CHECK")
    username = input(f"  {R2}Username{RS} > ").strip()
    if not username: return pausa()
    print(f"\n  {D}[+] Searching '{username}' across {len(PLATAFORMAS)} platforms...{RS}\n")

    def check(plataforma, url_tpl):
        url = url_tpl.format(username)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=8) as r:
                if r.getcode() == 200:
                    return (plataforma, url, True)
        except urllib.error.HTTPError as e:
            if e.code == 404: return (plataforma, url, False)
        except: pass
        return (plataforma, url, None)

    resultados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        futuros = [pool.submit(check, p, u) for p, u in PLATAFORMAS]
        for f in concurrent.futures.as_completed(futuros):
            resultados.append(f.result())

    encontrados = [r for r in resultados if r[2] is True]
    no_encontrados = [r for r in resultados if r[2] is False]
    errores = sum(1 for r in resultados if r[2] is None)

    print(f"  {R2}{'─' * 46}{RS}")
    print(f"  {R1}[+] FOUND ({len(encontrados)}){RS}")
    print(f"  {R2}{'─' * 46}{RS}")
    for p, url, _ in encontrados:
        print(f"  {W}{p:<14}{RS} {D}{url}{RS}")

    if no_encontrados:
        print(f"\n  {R2}{'─' * 46}{RS}")
        print(f"  {D}[-] NOT FOUND ({len(no_encontrados)}){RS}")
        print(f"  {R2}{'─' * 46}{RS}")
        for p, _, _ in no_encontrados:
            print(f"  {D}  {p}{RS}")

    if errores:
        print(f"\n  {D}[!] {errores} platform(s) could not be verified{RS}")
    pausa()

def osint_metadata():
    limpiar(); barra_menu("OSINT - METADATA EXTRACTOR")
    ruta = input(f"  {R2}File path{RS} > ").strip().strip('"').strip("'")
    if not ruta or not os.path.exists(ruta):
        print(f"  {D}[!] File not found{RS}")
        return pausa()

    ext = os.path.splitext(ruta)[1].lower()
    print(f"\n  {D}[+] Extracting metadata...{RS}\n")

    meta = {"File": os.path.basename(ruta), "Size": f"{os.path.getsize(ruta):,} bytes"}

    if ext in (".jpg", ".jpeg", ".tiff", ".tif"):
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            img = Image.open(ruta)
            meta["Dimensions"] = f"{img.size[0]}x{img.size[1]}"
            meta["Format"] = img.format
            meta["Mode"] = img.mode
            exif = img._getexif()
            if exif:
                for tag_id, valor in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if isinstance(valor, bytes):
                        try: valor = valor.decode("utf-8", errors="replace")
                        except: valor = repr(valor)
                    meta[tag] = str(valor)[:200]
        except Exception as e:
            meta["Error EXIF"] = str(e)

    elif ext == ".png":
        try:
            from PIL import Image
            img = Image.open(ruta)
            meta["Dimensions"] = f"{img.size[0]}x{img.size[1]}"
            meta["Format"] = img.format
            meta["Mode"] = img.mode
            for k, v in img.info.items():
                if isinstance(v, bytes):
                    try: v = v.decode("utf-8", errors="replace")
                    except: v = repr(v)
                meta[str(k)] = str(v)[:200]
        except Exception as e:
            meta["Error"] = str(e)

    elif ext == ".pdf":
        try:
            import fitz
            doc = fitz.open(ruta)
            meta["Pages"] = str(len(doc))
            md = doc.metadata
            for k, v in md.items():
                if v: meta[f"PDF:{k.capitalize()}"] = v
            doc.close()
        except ImportError:
            try:
                import PyPDF2
                with open(ruta, "rb") as f:
                    r = PyPDF2.PdfReader(f)
                    meta["Pages"] = str(len(r.pages))
                    md = r.metadata
                    if md:
                        for k, v in md.items():
                            if v: meta[f"PDF:{k[1:].capitalize()}"] = v
            except Exception as e:
                meta["Error PDF"] = str(e)
        except Exception as e:
            meta["Error PDF"] = str(e)

    elif ext in (".mp3", ".flac", ".ogg", ".wav", ".m4a"):
        try:
            import mutagen
            from mutagen.mp3 import MP3
            from mutagen.flac import FLAC
            from mutagen.oggvorbis import OggVorbis
            from mutagen.wave import WAVE
            from mutagen.mp4 import MP4
            tipos = {".mp3": MP3, ".flac": FLAC, ".ogg": OggVorbis, ".wav": WAVE, ".m4a": MP4}
            audio = tipos[ext](ruta)
            meta["Duration"] = f"{audio.info.length:.1f}s"
            meta["Bitrate"] = f"{getattr(audio.info, 'bitrate', 0) // 1000} kbps"
            meta["Frequency"] = f"{getattr(audio.info, 'sample_rate', 0)} Hz"
            for k, v in audio.items():
                meta[f"Audio:{k.capitalize()}"] = str(v)[:200]
        except Exception as e:
            meta["Error Audio"] = str(e)

    elif ext in (".mp4", ".avi", ".mkv", ".mov"):
        try:
            import mutagen
            from mutagen.mp4 import MP4
            if ext == ".m4a" or ext == ".mp4":
                try:
                    mp4 = MP4(ruta)
                    meta["Duration"] = f"{mp4.info.length:.1f}s"
                    meta["Bitrate"] = f"{getattr(mp4.info, 'bitrate', 0) // 1000} kbps"
                    for k, v in mp4.items():
                        meta[f"Video:{k.capitalize()}"] = str(v)[:200]
                except: pass
        except: pass

    else:
        print(f"  {D}[!] Unsupported format: {ext}{RS}")
        print(f"  {D}    Supported: jpg, png, tiff, pdf, mp3, flac, ogg, wav, m4a, mp4{RS}")
        return pausa()

    print(f"  {R2}{'─' * 46}{RS}")
    for k, v in meta.items():
        print(f"  {W}{k+':':<25}{RS} {D}{v}{RS}")
    print(f"  {R2}{'─' * 46}{RS}")

    guardar = input(f"\n  {R2}Export JSON? (y/N){RS} > ").strip().lower()
    if guardar == "y":
        path = exportar_json(f"metadata_{int(time.time())}.json", meta)
        print(f"  {R1}[+] Saved to {path}{RS}")
    pausa()

def menu_osint():
    while True:
        try:
            limpiar(); print_banner()
            barra_menu("OSINT TOOLS")
            print()
            menu_en_columnas([("1","IP Info"),("2","IP Logger"),("3","Email Lookup"),("4","Phone Lookup"),("5","WHOIS"),("6","Username Check"),("7","Metadata Extractor"),("",""),("0","Back")])
            print()
            op = input(f"  {R2}>>{RS} ").strip().lower()
            if op == "1": osint_ip()
            elif op == "2": osint_ip_logger()
            elif op == "3": osint_email()
            elif op == "4": osint_phone()
            elif op == "5": osint_whois()
            elif op == "6": osint_username()
            elif op == "7": osint_metadata()
            elif op == "h": show_help()
            elif op == "0": return
            elif op == "x": sys.exit(0)
        except KeyboardInterrupt: return
