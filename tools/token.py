from tools.base import *

DISCORD_API = "https://discord.com/api/v10"

def generar_token_discord():
    uid = str(random.randint(10**17, 10**18 - 1))
    uid_b64 = base64.b64encode(uid.encode()).decode().rstrip("=")
    ts = hex(int(time.time() * 1000))[2:]
    rnd = base64.urlsafe_b64encode(random.randbytes(18)).decode().rstrip("=")
    return f"{uid_b64}.{ts}.{rnd}"

def token_generator():
    limpiar(); barra_menu("DISCORD TOKEN GENERATOR")
    print(f"  {D}Creates Discord-format tokens (non-functional - just for fun){RS}\n")
    try:
        cant = int(input(f"  {R2}How many{RS} > ").strip())
        if cant < 1: raise ValueError
    except: print(f"  {D}[!] Invalid amount{RS}"); return pausa()
    tokens = []
    for i in range(cant):
        tok = generar_token_discord()
        tokens.append(tok)
        print(f"  [{i+1:>3}] {W}{tok}{RS}")
    guardar = input(f"\n  {R2}Save to tokens.txt? (y/N){RS} > ").strip().lower()
    if guardar == "s":
        with open("tokens.txt", "w") as f: f.write("\n".join(tokens))
        print(f"  {R1}[+] Saved to tokens.txt{RS}")
    pausa()

def verificar_token(token):
    headers = {"Authorization": token, "User-Agent": UA}
    try:
        req = urllib.request.Request(f"{DISCORD_API}/users/@me", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode()), resp.status
    except urllib.error.HTTPError as e: return None, e.code
    except: return None, 0

def token_verifier():
    limpiar(); barra_menu("DISCORD TOKEN VERIFIER")
    token = input(f"  {R2}Token{RS} > ").strip()
    if not token: return pausa()
    print(f"\n  {D}[+] Verifying...{RS}\n")
    data, status = verificar_token(token)
    if data and status == 200:
        print(f"  {R1}STATUS: VALID TOKEN{RS}")
        print(f"  {'─' * 40}")
        for label, key in [("ID","id"),("Username","username"),("Display","global_name"),
            ("Email","email"),("Phone","phone"),("Verified","verified"),
            ("MFA","mfa_enabled"),("Flags","flags")]:
            val = data.get(key, "N/A")
            print(f"  {R2}{label}:{RS}{' '*(12-len(label))}{W}{val}{RS}")
        premium = data.get('premium_type', 0)
        print(f"  {R2}Premium:{RS}       {W}{'Si' if premium > 0 else 'No'}{RS}")
        try:
            req2 = urllib.request.Request(f"{DISCORD_API}/users/@me/billing/payment-sources", headers={"Authorization": token, "User-Agent": UA})
            with urllib.request.urlopen(req2, timeout=5) as r:
                billing = json.loads(r.read().decode())
            if billing:
                print(f"\n  {R1}PAYMENT METHODS: {len(billing)}{RS}")
                for b in billing:
                    t = {1: "Credit Card", 2: "PayPal"}.get(b.get('type', 0), "?")
                    print(f"    - {t}")
        except: pass
    elif status == 401: print(f"  {D}STATUS: INVALID TOKEN (HTTP 401){RS}")
    elif status == 403: print(f"  {D}STATUS: BANNED TOKEN (HTTP 403){RS}")
    else: print(f"  {D}STATUS: ERROR ({status}){RS}")
    pausa()

def token_mass_checker():
    limpiar(); barra_menu("DISCORD MASS TOKEN CHECKER")
    path = input(f"  {R2}Path to token file (1 per line){RS} > ").strip()
    try:
        with open(path) as f: tokens = [l.strip() for l in f if l.strip()]
    except: print(f"  {D}[!] Could not read file{RS}"); return pausa()
    print(f"  {D}[!] Checking {len(tokens)} tokens...{RS}\n")
    validos = []
    for i, tok in enumerate(tokens):
        data, status = verificar_token(tok)
        if status == 200:
            estado = f"{R1}VALID{RS}"
            user = f" | {data['username']}#{data.get('discriminator', '0')}" if data else ""
            validos.append((tok, data))
        elif status == 401: estado = f"{D}INVALID{RS}"; user = ""
        else: estado = f"{D}ERROR ({status}){RS}"; user = ""
        print(f"  [{i+1:>4}] {estado} {W}{tok[:50]}...{RS}{user}")
        barra_progreso(i+1, len(tokens), prefijo="Checking")
    print(f"\n  {R1}[+] {len(validos)}/{len(tokens)} valid tokens{RS}")
    if validos:
        guardar = input(f"  {R2}Save valid tokens? (y/N){RS} > ").strip().lower()
        if guardar == "y":
            with open("valid_tokens.txt", "w") as f:
                for t, d in validos: f.write(f"{t} | {d['username']}#{d.get('discriminator', '0')}\n")
            print(f"  {R1}[+] Saved to valid_tokens.txt{RS}")
    pausa()

def token_nitro_checker():
    limpiar(); barra_menu("DISCORD NITRO CHECKER")
    token = input(f"  {R2}Token{RS} > ").strip()
    if not token: return pausa()
    print()
    data, status = verificar_token(token)
    if not data: print(f"  {D}[!] Invalid token{RS}"); return pausa()
    headers = {"Authorization": token, "User-Agent": UA}
    try:
        req = urllib.request.Request(f"{DISCORD_API}/users/@me/billing/subscriptions", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r: subs = json.loads(r.read().decode())
        if subs:
            for s in subs:
                tipo = s.get('type', 0)
                nombre = {1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}.get(tipo, f"Tipo {tipo}")
                est = f"{R1}{nombre}{RS}" if s.get('status') == "active" else f"{D}{nombre} ({s.get('status')}){RS}"
                print(f"  {est}")
                if s.get('current_period_end'):
                    fin = datetime.fromtimestamp(s['current_period_end']).strftime("%Y-%m-%d %H:%M")
                    print(f"  {R2}Expires:{RS} {fin}")
        else: print(f"  {D}[!] No active subscriptions{RS}")
    except urllib.error.HTTPError as e: print(f"  {D}[!] HTTP {e.code}{RS}" if e.code != 403 else f"  {D}[!] No permissions{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def token_decoder():
    limpiar(); barra_menu("DISCORD TOKEN DECODER")
    token = input(f"  {R2}Token{RS} > ").strip()
    if not token: return pausa()
    partes = token.split(".")
    if len(partes) != 3: print(f"  {D}[!] Invalid token format{RS}"); return pausa()
    try:
        uid = base64.b64decode(partes[0] + "==").decode()
        ts_ms = int(partes[1], 16)
        ts_dt = datetime.fromtimestamp(ts_ms / 1000)
        print(f"\n  {R2}User ID:{RS}      {W}{uid}{RS}")
        print(f"  {R2}Created:{RS}        {W}{ts_dt.strftime('%Y-%m-%d %H:%M:%S')}{RS}")
        print(f"  {R2}Timestamp:{RS}      {W}{partes[1]}{RS}")
        print(f"  {R2}Age:{RS}     {W}{relatime(ts_ms)}{RS}")
    except Exception as e: print(f"  {D}[!] Error decoding: {e}{RS}")
    pausa()

def menu_token():
    while True:
        try:
            limpiar(); print_banner()
            barra_menu("DISCORD - TOKEN TOOLS")
            print()
            menu_en_columnas([("1","Generator"),("2","Verifier"),("3","Mass Checker"),("4","Nitro Checker"),("5","Decoder"),("0","Back")])
            print()
            op = input(f"  {R2}>>{RS} ").strip().lower()
            if op == "1": token_generator()
            elif op == "2": token_verifier()
            elif op == "3": token_mass_checker()
            elif op == "4": token_nitro_checker()
            elif op == "5": token_decoder()
            elif op == "h": show_help()
            elif op == "0": return
            elif op == "x": sys.exit(0)
        except KeyboardInterrupt: return
