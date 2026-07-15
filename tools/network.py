from tools.base import *
import subprocess
import platform

def _run_cmd(cmd, timeout=10, shell=False):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=shell)
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return None

IS_WIN = platform.system() == "Windows"

def net_wifi():
    limpiar(); barra_menu("NETWORK - WIFI SCANNER")
    print(f"  {D}[+] Scanning WiFi networks...{RS}\n")
    if IS_WIN:
        res = _run_cmd(["netsh", "wlan", "show", "networks", "mode=Bssid"], timeout=10)
        if res and res.returncode == 0 and res.stdout.strip():
            print(f"  {W}{res.stdout}{RS}")
        else:
            print(f"  {D}[!] Could not scan WiFi networks on Windows{RS}")
            print(f"  {D}Check that the WiFi adapter is active{RS}")
    else:
        res = _run_cmd(["nmcli", "-f", "SSID,SIGNAL,SECURITY,CHAN", "dev", "wifi", "list"], timeout=10)
        if res and res.returncode == 0 and res.stdout.strip():
            print(f"  {W}{res.stdout}{RS}")
        else:
            res2 = _run_cmd(["iw", "dev"], timeout=5)
            if res2 and res2.stdout.strip():
                print(f"  {W}{res2.stdout[:1000]}{RS}")
            else:
                print(f"  {D}[!] nmcli/iw not available (install networkmanager or iw){RS}")
    pausa()

def net_dns():
    limpiar(); barra_menu("NETWORK - DNS LOOKUP")
    dominio = input(f"  {R2}Domain{RS} > ").strip()
    if not dominio: return pausa()
    tipos = input(f"  {R2}Types (A,MX,NS,TXT,ALL) [ALL]{RS} > ").strip().upper() or "ALL"
    print()
    tipos_lista = ["A","AAAA","MX","NS","TXT","CNAME"] if tipos == "ALL" else [tipos]
    for t in tipos_lista:
        if not IS_WIN:
            res = _run_cmd(["dig", "+short", dominio, t], timeout=5)
            if res and res.stdout.strip():
                print(f"  {R2}{t}:{RS}")
                for line in res.stdout.strip().split("\n"):
                    print(f"    {W}{line}{RS}")
                continue
        if t in ("A", "AAAA"):
            familia = socket.AF_INET6 if t == "AAAA" else socket.AF_INET
            try:
                ai = socket.getaddrinfo(dominio, 0, familia, socket.SOCK_STREAM)
                print(f"  {R2}{t}:{RS}")
                for a in ai:
                    print(f"    {W}{a[4][0]}{RS}")
            except:
                pass
        elif t == "MX" and IS_WIN:
            res = _run_cmd(["nslookup", "-type=MX", dominio], timeout=5)
            if res:
                for line in res.stdout.split("\n"):
                    if "mail exchanger" in line.lower():
                        print(f"  {R2}MX:{RS}")
                        print(f"    {W}{line.strip()}{RS}")
    pausa()

def net_traceroute():
    limpiar(); barra_menu("NETWORK - TRACEROUTE")
    host = input(f"  {R2}Host{RS} > ").strip()
    if not host: return pausa()
    print(f"\n  {D}[+] Tracing route...{RS}\n")
    cmd = ["tracert", "-h", "15", host] if IS_WIN else ["traceroute", "-m", "15", host]
    res = _run_cmd(cmd, timeout=30)
    if res and res.stdout.strip():
        for line in res.stdout.split("\n")[:30]:
            print(f"  {W}{line}{RS}")
    elif res and res.stderr.strip():
        print(f"  {D}[!] {res.stderr.strip()}{RS}")
    else:
        if IS_WIN:
            print(f"  {D}[!] tracert failed. Try: 'tracert {host}' in CMD as admin{RS}")
        else:
            print(f"  {D}[!] traceroute not installed. Install: sudo apt install traceroute{RS}")
    pausa()

def net_http_headers():
    limpiar(); barra_menu("NETWORK - HTTP HEADERS")
    url = input(f"  {R2}URL{RS} > ").strip()
    if not url: return pausa()
    if not url.startswith("http"): url = "https://" + url
    print()
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"  {R2}Status:{RS} {W}{resp.status} {resp.reason}{RS}")
            print(f"  {R2}Version:{RS} {W}{resp.version}{RS}")
            for k, v in resp.headers.items(): print(f"  {R2}{k}:{RS} {W}{v}{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def net_ssl():
    limpiar(); barra_menu("NETWORK - SSL CHECKER")
    host = input(f"  {R2}Host (eg: google.com){RS} > ").strip()
    if not host: return pausa()
    print()
    try:
        import ssl
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ss:
                cert = ss.getpeercert()
                print(f"  {R2}Host:{RS}        {W}{host}{RS}")
                print(f"  {R2}Cipher:{RS}      {W}{ss.cipher()}{RS}")
                print(f"  {R2}SSL Version:{RS}  {W}{ss.version()}{RS}")
                if cert:
                    print(f"  {R2}Emisor:{RS}      {W}{dict(cert.get('issuer', [])).get('organizationName', 'N/A')}{RS}")
                    print(f"  {R2}Subject:{RS}     {W}{dict(cert.get('subject', [])).get('commonName', 'N/A')}{RS}")
                    print(f"  {R2}Valid from:{RS}{W}{cert.get('notBefore', 'N/A')}{RS}")
                    print(f"  {R2}Valid until:{RS}{W}{cert.get('notAfter', 'N/A')}{RS}")
                    print(f"  {R2}SAN:{RS}         {W}{', '.join([x[1] for x in cert.get('subjectAltName', [])])[:100]}{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def net_mac_lookup():
    limpiar(); barra_menu("NETWORK - MAC LOOKUP")
    mac = input(f"  {R2}MAC (eg: 00:1A:2B:3C:4D:5E){RS} > ").strip()
    if not mac: return pausa()
    print()
    try:
        req = urllib.request.Request(f"https://api.macvendors.com/{mac}", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as r:
            print(f"  {R2}MAC:{RS}      {W}{mac}{RS}")
            print(f"  {R2}Manufacturer:{RS}{W}{r.read().decode().strip()}{RS}")
    except urllib.error.HTTPError as e:
        if e.code == 404: print(f"  {D}[!] Manufacturer not found{RS}")
        else: print(f"  {D}[!] HTTP {e.code}{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def net_subdomain():
    limpiar(); barra_menu("NETWORK - SUBDOMAIN FINDER")
    dominio = input(f"  {R2}Domain{RS} > ").strip()
    if not dominio: return pausa()
    print()
    wordlist = ["www", "mail", "admin", "blog", "dev", "api", "test", "stage", "cdn",
                "ftp", "ssh", "webmail", "portal", "docs", "support", "shop", "app",
                "m", "mobile", "ns1", "ns2", "mx", "smtp", "pop", "vpn", "wiki",
                "demo", "beta", "status", "help", "forum", "community", "info",
                "remote", "intranet", "correo", "cpanel", "webdisk", "cpcalendars"]
    print(f"  {D}[+] Testing {len(wordlist)} subdomains...{RS}\n")
    encontrados = []
    sp = Spinner("Looking up subdomains"); sp.start()
    for sd in wordlist:
        try:
            ip = socket.gethostbyname(f"{sd}.{dominio}")
            encontrados.append((sd, ip))
        except: pass
    sp.stop()
    if encontrados:
        print(f"  {R2}{'SUBDOMAIN':<20} {'IP'}{RS}")
        print(f"  {'─' * 40}")
        for sd, ip in sorted(encontrados): print(f"  {W}{sd:<20} {ip}{RS}")
        print(f"\n  {R1}[+] {len(encontrados)} subdomains found{RS}")
    else: print(f"  {D}[!] No subdomains found{RS}")
    guardar = input(f"\n  {R2}Export? (J=JSON, H=HTML, N=no) [N]{RS} > ").strip().upper()
    if guardar == "J":
        path = exportar_json(f"subdomains_{dominio}.json", encontrados)
        print(f"  {R1}[+] Saved to {path}{RS}")
    elif guardar == "H":
        path = exportar_html(f"subdomains_{dominio}.html", f"Subdomains: {dominio}", ["Subdomain","IP"],
                             [[sd, ip] for sd, ip in sorted(encontrados)])
        print(f"  {R1}[+] HTML report at {path}{RS}")
    pausa()

def net_dir_brute():
    limpiar(); barra_menu("NETWORK - DIRECTORY BRUTE")
    url = input(f"  {R2}Base URL (eg: https://example.com){RS} > ").strip()
    if not url: return pausa()
    wordlist = ["admin", "login", "wp-admin", "wp-content", "backup", ".git", ".env",
                "config", "admin.php", "index.php", "robots.txt", "sitemap.xml", "css",
                "js", "images", "uploads", "download", "api", "v1", "v2", "graphql",
                "wp-json", "xmlrpc.php", "phpinfo.php", "info.php", "test", "debug",
                "panel", "cpanel", "server-status", "shell", "cmd", "includes",
                "classes", "modules", "assets", "static", "public", "private", "tmp"]
    print(f"\n  {D}[+] Testing {len(wordlist)} paths...{RS}\n")
    encontrados = []
    sp = Spinner("Fuzzing directories"); sp.start()
    for ruta in wordlist:
        target = f"{url.rstrip('/')}/{ruta}"
        try:
            req = urllib.request.Request(target, method="GET", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status in (200, 301, 302, 403):
                    encontrados.append((ruta, resp.status, len(resp.read())))
        except urllib.error.HTTPError as e:
            if e.code in (200, 301, 302, 403, 401): encontrados.append((ruta, e.code, 0))
        except: pass
    sp.stop()
    if encontrados:
        print(f"  {R2}{'PATH':<25} {'STATUS':<8} {'SIZE'}{RS}")
        print(f"  {'─' * 50}")
        for r, s, sz in sorted(encontrados, key=lambda x: x[1]):
            print(f"  {W}{r:<25} {s:<8} {sz if sz else '?'}{RS}")
        print(f"\n  {R1}[+] {len(encontrados)} paths found{RS}")
    else: print(f"  {D}[!] No accessible paths found{RS}")
    pausa()

def menu_network():
    while True:
        try:
            limpiar(); print_banner()
            barra_menu("NETWORK TOOLS")
            print()
            menu_en_columnas([("1","WiFi Scanner"),("2","DNS Lookup"),("3","Traceroute"),
                             ("4","HTTP Headers"),("5","SSL Checker"),("6","MAC Lookup"),
                             ("7","Subdomain Finder"),("8","Dir Brute"),("0","Back")])
            print()
            op = input(f"  {R2}>>{RS} ").strip().lower()
            if op == "1": net_wifi()
            elif op == "2": net_dns()
            elif op == "3": net_traceroute()
            elif op == "4": net_http_headers()
            elif op == "5": net_ssl()
            elif op == "6": net_mac_lookup()
            elif op == "7": net_subdomain()
            elif op == "8": net_dir_brute()
            elif op == "h": show_help()
            elif op == "0": return
            elif op == "x": sys.exit(0)
        except KeyboardInterrupt: return
