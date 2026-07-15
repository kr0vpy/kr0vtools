#!/usr/bin/env python3
import sys, os, json, urllib.request, urllib.error, urllib.parse, socket, base64, random, string, time, threading, hashlib, ipaddress, re, importlib.util
from datetime import datetime

IS_WINDOWS = os.name == "nt"

try:
    import termios, tty
    _HAVE_TERMIOS = True
except ImportError:
    _HAVE_TERMIOS = False

try:
    import readline
except ImportError:
    readline = None

if IS_WINDOWS:
    import msvcrt

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except:
    class Fore: LIGHTRED_EX=RED=LIGHTBLACK_EX=LIGHTWHITE_EX=WHITE=RESET=""
    class Style: RESET_ALL=""

R1 = Fore.LIGHTRED_EX
R2 = Fore.LIGHTRED_EX
D = Fore.WHITE
W = Fore.LIGHTRED_EX
RS = Fore.RESET

if IS_WINDOWS:
    os.system("title Tool Panel v2.0")

CONFIG_DIR = os.path.expanduser("~/.config/0xytool")
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
LOG_PATH = os.path.join(CONFIG_DIR, "session.log")

def cargar_config():
    default = {"modo_compacto": False, "timeout": 10, "hilos": 5, "ultimo_menu": "", "api_keys": {}}
    try:
        with open(CONFIG_PATH) as f: return {**default, **json.load(f)}
    except: return default

def guardar_config(**kw):
    cfg = cargar_config()
    cfg.update(kw)
    with open(CONFIG_PATH, "w") as f: json.dump(cfg, f, indent=2)

def log_evento(msg):
    try:
        with open(LOG_PATH, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except: pass

CFG = cargar_config()
MODO_COMPACTO = [CFG.get("modo_compacto", False)]
API_KEYS = CFG.get("api_keys", {})

def guardar_api_key(servicio, key):
    API_KEYS[servicio] = key
    guardar_config(api_keys=API_KEYS)
    log_evento(f"API Key guardada: {servicio}")

def obtener_api_key(servicio):
    return API_KEYS.get(servicio, "")

class Spinner:
    def __init__(self, msg="Processing"):
        self.msg = msg; self.running = False; self.t = None
    def spin(self):
        for c in "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏":
            if not self.running: break
            sys.stdout.write(f"\r  {D}{c}{RS} {self.msg}...  ")
            sys.stdout.flush(); time.sleep(0.08)
    def start(self):
        self.running = True
        self.t = threading.Thread(target=self.spin, daemon=True)
        self.t.start()
    def stop(self, ok=True):
        self.running = False
        if self.t: self.t.join()
        sys.stdout.write(f"\r  {' ' * 30}\r"); sys.stdout.flush()

def exportar_json(nombre, datos):
    path = os.path.join(CONFIG_DIR, nombre)
    with open(path, "w") as f: json.dump(datos, f, indent=2, default=str)
    return path

def exportar_html(nombre, titulo, columnas, filas):
    path = os.path.join(CONFIG_DIR, nombre)
    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<title>{titulo}</title>
<style>
  body {{ background:#0a0a0f; color:#e0e0e0; font:14px/1.5 monospace; padding:20px; }}
  h1 {{ color:#ff3333; border-bottom:1px solid #333; padding-bottom:8px; }}
  table {{ border-collapse:collapse; width:100%; margin-top:12px; }}
  th {{ background:#1a1a2e; color:#ff4444; text-align:left; padding:8px 10px; border:1px solid #333; }}
  td {{ padding:6px 10px; border:1px solid #222; }}
  tr:nth-child(even) td {{ background:#0d0d1a; }}
  .ok {{ color:#4caf50; }} .warn {{ color:#ff9800; }} .err {{ color:#f44336; }}
</style></head><body>
<h1>{titulo}</h1>
<table><thead><tr>{"".join(f'<th>{c}</th>' for c in columnas)}</tr></thead><tbody>
{"".join(f'<tr>{"".join(f"<td>{v}</td>" for v in f)}</tr>' for f in filas)}</tbody></table>
<p style="color:#666;margin-top:20px">Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body></html>"""
    with open(path, "w") as f: f.write(html)
    return path

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

def pausa():
    input(f"\n  {D}Press Enter to continue...{RS}")

def barra_progreso(actual, total, ancho=30, prefijo=""):
    pct = actual / total if total > 0 else 0
    llenos = int(ancho * pct)
    bar = f"{R1}{'█' * llenos}{D}{'─' * (ancho - llenos)}{RS}"
    print(f"\r  {prefijo} [{bar}] {int(pct * 100):>3}%  ", end="", flush=True)
    if actual >= total: print()

def leer_mascarado(prompt):
    if IS_WINDOWS:
        return _leer_mascarado_win(prompt)
    return _leer_mascarado_unix(prompt)

def _leer_mascarado_unix(prompt):
    import termios, tty
    sys.stdout.write(prompt)
    sys.stdout.flush()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        valor = ""
        while True:
            ch = sys.stdin.read(1)
            if ch in ("\n", "\r"):
                sys.stdout.write("\n"); break
            elif ch in ("\x7f", "\b"):
                if len(valor) > 0:
                    valor = valor[:-1]
                    sys.stdout.write("\b \b")
            else:
                valor += ch
                sys.stdout.write("*")
            sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old)
    return valor

def _leer_mascarado_win(prompt):
    import msvcrt
    sys.stdout.write(prompt)
    sys.stdout.flush()
    valor = ""
    while True:
        ch = msvcrt.getch()
        if ch in (b"\r", b"\n"):
            sys.stdout.write("\n")
            break
        elif ch in (b"\x7f", b"\x08"):
            if len(valor) > 0:
                valor = valor[:-1]
                sys.stdout.write("\b \b")
        else:
            try:
                valor += ch.decode()
                sys.stdout.write("*")
            except:
                pass
        sys.stdout.flush()
    return valor

ART = """ ██╗  ██╗██████╗  ██████╗ ██╗   ██╗  ████████╗ ██████╗  ██████╗ ██╗     ███████╗
 ██║ ██╔╝██╔══██╗██╔═══██╗██║   ██║  ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
 █████╔╝ ██████╔╝██║   ██║██║   ██║     ██║   ██║   ██║██║   ██║██║     ███████╗
 ██╔═██╗ ██╔══██╗██║   ██║╚██╗ ██╔╝     ██║   ██║   ██║██║   ██║██║     ╚════██║
 ██║  ██╗██║  ██║╚██████╔╝ ╚████╔╝      ██║   ╚██████╔╝╚██████╔╝███████╗███████║
 ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═══╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝"""

ANCHO = 80

def centrar(texto, ancho):
    vis = re.sub(r'\033\[[0-9;]*m', '', texto)
    espacios = ancho - len(vis)
    if espacios <= 0: return texto
    izq = espacios // 2; der = espacios - izq
    return " " * izq + texto + " " * der

def ancho_terminal():
    try:
        return os.get_terminal_size().columns
    except:
        return 80

def pad_centro():
    tw = ancho_terminal()
    if tw <= ANCHO: return ""
    return " " * ((tw - ANCHO) // 2)

def print_banner():
    p = pad_centro()
    print()
    print()
    if not MODO_COMPACTO[0]:
        for li in ART.rstrip("\n").split("\n"):
            print(p + R1 + li + RS)
        print()

def barra_menu(titulo):
    p = pad_centro()
    print(f"\n{p}{R2}─── {W}{titulo}{RS} {D}{'─' * max(ANCHO - len(titulo) - 7, 1)}{RS}")

def area_header(nombre):
    p = pad_centro()
    print(f"{p}{D}{'─' * ANCHO}{RS}")
    print(f"{p}{R2}── {W}{nombre}{RS} {D}{'─' * max(ANCHO - len(nombre) - 6, 1)}{RS}")

def menu_en_columnas(items, cols=2):
    p = pad_centro()
    ancho_col = ANCHO // cols
    for i in range(0, len(items), cols):
        fila = items[i:i+cols]
        partes = []
        for key, txt in fila:
            if key and txt:
                item = f"{R2}[{key}]{RS} {W}{txt:<{ancho_col - 5}}{RS}"
                partes.append(item)
            else:
                partes.append(" " * ancho_col)
        while len(partes) < cols:
            partes.append(" " * ancho_col)
        linea = "".join(partes)
        fila_valida = all(k for k, _ in fila if k)
        if fila_valida and any(k for k, _ in fila):
            print(f"{p}{R1}│{RS}{linea}{R1}│{RS}")
        else:
            print(f"{p}{linea}")

def _padded(texto, ancho):
    vis = re.sub(r'\033\[[0-9;]*m', '', texto)
    diff = ancho - len(vis)
    if diff >= 0:
        der = diff // 2; izq = diff - der
        return " " * izq + texto + " " * der
    return texto[:ancho]

def menu_horizontal(columnas):
    p = pad_centro()
    ncols = len(columnas)
    espacios = ncols - 1
    anchos = []
    for nombre, _, items in columnas:
        vis = re.sub(r'\033\[[0-9;]*m', '', nombre)
        max_item = max((len(k) + len(t) + 4 for k, t in items), default=0)
        bw = max(len(vis) + 4, max_item + 2, 14)
        anchos.append(bw)

    total_base = sum(anchos) + espacios * 2
    if total_base != ANCHO:
        dif = ANCHO - total_base
        while dif != 0:
            for i in range(ncols):
                if dif == 0:
                    break
                if dif > 0:
                    anchos[i] += 1
                    dif -= 1
                elif dif < 0 and anchos[i] > 14:
                    anchos[i] -= 1
                    dif += 1

    def rama(i):
        return "├"

    def tubo(i, r, total):
        if ncols == 1:
            return "─"
        if r == total - 1:
            return "└"
        return "│"

    def sub_txt(nombre, sub):
        if sub:
            return f" {D}({sub}){RS}"
        return ""

    def sep(i):
        return " " if i < ncols - 1 else ""

    cabeceras = []
    for i, (nombre, sub, _) in enumerate(columnas):
        vis = re.sub(r'\033\[[0-9;]*m', '', nombre)
        extra = len(sub) + 3 if sub else 0
        relleno = anchos[i] - 1 - len(vis) - extra
        cabeceras.append(f"{R1}{rama(i)}{RS}{R2}{nombre}{RS}{sub_txt(nombre, sub)}{D}{'─' * max(relleno, 1)}{RS}{sep(i)}")

    print(p + "".join(cabeceras))

    max_filas = max(len(items) for _, _, items in columnas)
    for r in range(max_filas):
        linea = ""
        for i in range(ncols):
            _, _, items = columnas[i]
            nitems = len(items)
            offset = (max_filas - nitems) // 2
            idx = r - offset
            has_item = 0 <= idx < nitems
            if has_item:
                linea += tubo(i, idx, nitems)
                k, t = items[idx]
                vis = f"[{k}] {t}"
                relleno = anchos[i] - 1 - len(vis)
                linea += f"{R2}[{k}]{RS} {W}{t}{RS}{' ' * max(relleno, 0)}"
            else:
                linea += " " * anchos[i]
            linea += sep(i)
        print(p + linea)

def relatime(ts_ms):
    diff = int(time.time() * 1000) - ts_ms
    segs = diff // 1000
    if segs < 60: return f"{segs}s"
    mins = segs // 60
    if mins < 60: return f"{mins}m {segs % 60}s"
    hrs = mins // 60
    if hrs < 24: return f"{hrs}h {mins % 60}m"
    return f"{hrs // 24}d {hrs % 24}h"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def show_help():
    limpiar()
    p = pad_centro()
    barra_menu("HELP - How to use the panel")
    for li in f"""
{W}WELCOME TO KR0VTOOLS PANEL v2.0{RS}
{D}Comprehensive pentesting, OSINT, networking and utilities panel.{RS}

{R2}[1]{RS} {W}DISCORD - WEBHOOK TOOLS{RS}
{D}  Spammer, Info, Deleter, Embed, Spoof (multi-thread){RS}

{R2}[2]{RS} {W}DISCORD - TOKEN TOOLS{RS}
{D}  Generator, Verifier, Mass Checker (concurrent), Nitro, Decoder{RS}

{R2}[N]{RS} {W}DISCORD - SERVER NUKER{RS}
{D}  Multi-channel Spam, Delete Channels, Ban All, Create Channels{RS}

{R2}[3]{RS} {W}PORT SCANNER{RS}
{D}  TCP/UDP scan, service detection, banners, export JSON/HTML{RS}

{R2}[4]{RS} {W}OSINT TOOLS{RS}
{D}  IP Info, IP Logger, Email/Phone Lookup, WHOIS, breaches{RS}

{R2}[5]{RS} {W}UTILITIES{RS}
{D}  ID Generator, Hasher, Base64, Token Decode{RS}

{R2}[6]{RS} {W}NETWORK TOOLS{RS}
{D}  WiFi, DNS, Traceroute, HTTP Headers, SSL, MAC, Subdomain, Dir Brute{RS}

{R2}[7]{RS} {W}WEB SCRAPING{RS}
{D}  Link Extractor, Email Scraper, Meta Tags, Image Downloader{RS}

{R2}[8]{RS} {W}SOCIAL ENGINEERING{RS}
{D}  Fake Identity, QR Generator, Link Obfuscator, UA Generator{RS}

{R2}[9]{RS} {W}VULNERABILITY SCANNER{RS}
{D}  SQLi, XSS, Open Redirect, SSTI, Path Traversal{RS}

{R2}KEYS:{RS}
{W}  H{RS} {D}- Help  {W}N{RS} {D}- Nuker  {W}0{RS} {D}- Back  {W}X{RS} {D}- Exit  {W}C{RS} {D}- Compact mode  {W}Tab{RS} {D}- Autocomplete{RS}

{D}NOTE: For educational use only in authorized environments. Logs at ~/.config/0xytool/{RS}
""".strip("\n").split("\n"):
        print(p + "  " + li)
    pausa()

def setup_readline(commands):
    if readline is None:
        return
    def completer(text, state):
        options = [c for c in commands if c.startswith(text)]
        return options[state] if state < len(options) else None
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
