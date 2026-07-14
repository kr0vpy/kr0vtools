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
    class Fore: LIGHTRED_EX=RED=LIGHTBLACK_EX=LIGHTWHITE_EX=RESET=""
    class Style: RESET_ALL=""

R1 = Fore.LIGHTRED_EX
R2 = Fore.RED
D = Fore.LIGHTBLACK_EX
W = Fore.LIGHTWHITE_EX
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
    def __init__(self, msg="Procesando"):
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
    input(f"\n  {D}Presiona Enter para continuar...{RS}")

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

ART = f"""{R2}    ____  ____ _  __    __________  ____  __   _____
{R2}   / __ )/ __ \\ |/ /   /_  __/ __ \\/ __ \\/ /  / ___/
{R2}  / __  / / / /   /     / / / / / / / / / /   \\__ \\
{R2} / /_/ / /_/ /   |     / / / /_/ / /_/ / /______/ /
{R2}/_____/\\____/_/|_|    /_/  \\____/\\____/_____/____/
"""

ANCHO = 52

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
    bw = ANCHO + 4
    if tw <= bw: return ""
    return " " * ((tw - bw) // 2)

def print_banner():
    p = pad_centro()
    if not MODO_COMPACTO[0]:
        for li in ART.rstrip("\n").split("\n"):
            print(p + li)
        print()
    print(f"{p}{R1}┌{'─' * ANCHO}┐{RS}")
    print(f"{p}{R1}│{RS} {R2}Tool Panel v2.0{RS}  {D}[H] Help  [X] Exit  [C] Compact{RS}  {R1}│{RS}")
    print(f"{p}{R1}└{'─' * ANCHO}┘{RS}")

def barra_menu(titulo):
    p = pad_centro()
    vis = re.sub(r'\033\[[0-9;]*m', '', titulo)
    resto = ANCHO - len(vis) - 9
    print(f"\n{p}{R1}┌{'─' * ANCHO}┐{RS}")
    print(f"{p}{R1}├{RS}{R2}─── {W}{titulo}{RS} {R2}───{RS}{R1}{'─' * max(0, resto)}┤{RS}")
    print(f"{p}{R1}└{'─' * ANCHO}┘{RS}")

def area_header(nombre):
    p = pad_centro()
    vis = re.sub(r'\033\[[0-9;]*m', '', nombre)
    print(f"{p}{R1}├{'─' * ANCHO}┤{RS}")
    print(f"{p}{R1}├{RS}{R2}── {W}{nombre}{RS} {R2}──{RS}{R1}{'─' * max(0, ANCHO - len(vis) - 7)}┤{RS}")

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
    col_w = ANCHO // ncols
    partes = []
    for nombre, _, _ in columnas:
        txt = centrar(f"{W}{nombre}{RS}", col_w)
        partes.append(f"{R2}{txt}{RS}")
    print(f"{p}{R1}│{RS}{''.join(partes)}{R1}│{RS}")
    tiene_sub = any(sub for _, sub, _ in columnas)
    if tiene_sub:
        partes = []
        for _, sub, _ in columnas:
            vis = len(sub) if sub else 0
            left = (col_w - vis) // 2
            right = col_w - vis - left
            lbl = f"{D}{sub or ''}{RS}" if sub else ""
            partes.append(f"{' ' * left}{lbl}{' ' * right}")
        print(f"{p}{R1}│{RS}{''.join(partes)}{R1}│{RS}")
    max_filas = max(len(items) for _, _, items in columnas)
    for r in range(max_filas):
        partes = []
        for _, _, items in columnas:
            if r < len(items):
                k, t = items[r]
                name_w = col_w - 4
                nt = t if len(t) <= name_w else t[:name_w-1] + "."
                item = f"{R2}[{k}]{RS} {W}{nt:<{name_w}}{RS}"
                partes.append(item)
            else:
                partes.append(" " * col_w)
        print(f"{p}{R1}│{RS}{''.join(partes)}{R1}│{RS}")

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
    barra_menu("AYUDA - Como usar el panel")
    for li in f"""
{W}BIENVENIDO A 0XYTOOL PANEL v2.0{RS}
{D}Panel integral de pentesting, OSINT, redes y utilidades.{RS}

{R2}[1]{RS} {W}DISCORD - WEBHOOK TOOLS{RS}
{D}  Spammer, Info, Deleter, Embed, Spoof (multi-hilo){RS}

{R2}[2]{RS} {W}DISCORD - TOKEN TOOLS{RS}
{D}  Generator, Verifier, Mass Checker (concurrente), Nitro, Decoder{RS}

{R2}[N]{RS} {W}DISCORD - SERVER NUKER{RS}
{D}  Spam multi-canal, Delete canales, Ban All, Create canales{RS}

{R2}[3]{RS} {W}PORT SCANNER{RS}
{D}  TCP/UDP scan, deteccion de servicios, banners, exportar JSON/HTML{RS}

{R2}[4]{RS} {W}OSINT TOOLS{RS}
{D}  IP Info, IP Logger, Email/Phone Lookup, WHOIS, filtraciones{RS}

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

{R2}TECLAS:{RS}
{W}  H{RS} {D}- Ayuda  {W}N{RS} {D}- Nuker  {W}0{RS} {D}- Volver  {W}X{RS} {D}- Salir  {W}C{RS} {D}- Compact mode  {W}Tab{RS} {D}- Autocompletar{RS}

{D}NOTA: Solo para uso educativo en entornos autorizados. Logs en ~/.config/0xytool/{RS}
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
