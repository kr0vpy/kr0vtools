from tools.base import *

def web_links():
    limpiar(); barra_menu("WEB - LINK EXTRACTOR")
    url = input(f"  {R2}URL{RS} > ").strip()
    if not url: return pausa()
    if not url.startswith("http"): url = "https://" + url
    print(f"\n  {D}[+] Extracting links...{RS}\n")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
        links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
        internos, externos = [], []
        dominio_base = re.search(r'https?://([^/]+)', url).group(1)
        for link in sorted(set(links)):
            if dominio_base in link: internos.append(link)
            else: externos.append(link)
        print(f"  {R2}Internal ({len(internos)}):{RS}")
        for l in internos[:15]: print(f"    {W}{l[:80]}{RS}")
        print(f"\n  {R2}External ({len(externos)}):{RS}")
        for l in externos[:15]: print(f"    {W}{l[:80]}{RS}")
        if len(internos) + len(externos) > 30:
            print(f"  {D}[+] ... and {len(internos)+len(externos)-30} more{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def web_emails():
    limpiar(); barra_menu("WEB - EMAIL SCRAPER")
    url = input(f"  {R2}URL{RS} > ").strip()
    if not url: return pausa()
    if not url.startswith("http"): url = "https://" + url
    print(f"\n  {D}[+] Searching emails...{RS}\n")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
        emails = sorted(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)))
        if emails:
            print(f"  {R1}[+] {len(emails)} emails found:{RS}")
            for e in emails: print(f"    {W}{e}{RS}")
        else: print(f"  {D}[!] No emails found{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def web_meta():
    limpiar(); barra_menu("WEB - META TAG EXTRACTOR")
    url = input(f"  {R2}URL{RS} > ").strip()
    if not url: return pausa()
    if not url.startswith("http"): url = "https://" + url
    print(f"\n  {D}[+] Extracting meta tags...{RS}\n")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
        metas = re.findall(r'<meta[^>]+>', html, re.I)
        for m in metas[:25]:
            name = re.search(r'name=["\']([^"\']+)["\']', m, re.I)
            prop = re.search(r'property=["\']([^"\']+)["\']', m, re.I)
            content = re.search(r'content=["\']([^"\']+)["\']', m, re.I)
            key = (name or prop).group(1) if (name or prop) else "?"
            val = content.group(1) if content else "?"
            if val and val != "?": print(f"  {R2}{key}:{RS} {W}{val[:80]}{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def web_images():
    limpiar(); barra_menu("WEB - IMAGE DOWNLOADER")
    url = input(f"  {R2}Page URL with images{RS} > ").strip()
    if not url: return pausa()
    if not url.startswith("http"): url = "https://" + url
    print(f"\n  {D}[+] Searching images...{RS}\n")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
        imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.I)
        if not imgs: print(f"  {D}[!] No images found{RS}"); return pausa()
        print(f"  {R1}[+] {len(imgs)} images found:{RS}")
        for img in imgs[:20]: print(f"    {W}{img[:90]}{RS}")
        desc = input(f"\n  {R2}Download? (y/N){RS} > ").strip().lower()
        if desc == "y":
            os.makedirs("downloads", exist_ok=True)
            sp = Spinner("Downloading"); sp.start()
            for i, img in enumerate(imgs[:20]):
                try:
                    if img.startswith("//"): img = "https:" + img
                    elif img.startswith("/"): img = url.rstrip("/") + img
                    elif not img.startswith("http"): img = url.rstrip("/") + "/" + img
                    img_req = urllib.request.Request(img, headers={"User-Agent": UA})
                    with urllib.request.urlopen(img_req, timeout=10) as ir:
                        ext = os.path.splitext(img.split("?")[0])[1] or ".jpg"
                        path = f"downloads/img_{i+1}{ext}"
                        with open(path, "wb") as f: f.write(ir.read())
                except: pass
            sp.stop()
            print(f"  {R1}[+] Downloaded to downloads/{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def menu_web():
    while True:
        try:
            limpiar(); print_banner()
            barra_menu("WEB SCRAPING TOOLS")
            print()
            menu_en_columnas([("1","Link Extractor"),("2","Email Scraper"),
                             ("3","Meta Tags"),("4","Image Downloader"),("",""),("0","Back")])
            print()
            op = input(f"  {R2}>>{RS} ").strip().lower()
            if op == "1": web_links()
            elif op == "2": web_emails()
            elif op == "3": web_meta()
            elif op == "4": web_images()
            elif op == "h": show_help()
            elif op == "0": return
            elif op == "x": sys.exit(0)
        except KeyboardInterrupt: return
