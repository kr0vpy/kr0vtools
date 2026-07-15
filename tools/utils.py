from tools.base import *

CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_B62_LEN = len(CHARSET)

def _b62_encode(n):
    if n == 0: return CHARSET[0]
    res = []
    while n > 0:
        res.append(CHARSET[n % _B62_LEN])
        n //= _B62_LEN
    return "".join(reversed(res))

def _b62_decode(s):
    n = 0
    for c in s:
        n = n * _B62_LEN + CHARSET.index(c)
    return n

def _obfuscate_id(raw, key=0xA5B3C):
    xored = raw ^ key
    return _b62_encode(xored)

def _rand_id(longitud=7):
    return "".join(random.choice(CHARSET) for _ in range(longitud))

def util_id_gen():
    limpiar(); barra_menu("UTILITIES - ID GENERATOR")
    print(f"  {D}Generates short random IDs with letters and numbers{RS}\n")
    try:
        cant = int(input(f"  {R2}How many IDs?{RS} > ").strip())
        if cant < 1 or cant > 100: cant = 10
    except: cant = 10
    try:
        lon = int(input(f"  {R2}Length (4-16) [7]{RS} > ").strip())
        if lon < 4: lon = 4
        elif lon > 16: lon = 16
    except: lon = 7
    ids = set()
    while len(ids) < cant:
        ids.add(_rand_id(lon))
    ids = list(ids)
    for i, oid in enumerate(ids):
        print(f"  [{i+1:>3}] {W}{oid}{RS}")
    guardar = input(f"\n  {R2}Save to ids.txt? (y/N){RS} > ").strip().lower()
    if guardar == "y":
        with open("ids.txt", "w") as f:
            f.write("\n".join(ids))
        print(f"  {R1}[+] Saved{RS}")
    pausa()

def util_hasher():
    limpiar(); barra_menu("UTILITIES - HASHER")
    texto = input(f"  {R2}Text to hash{RS} > ")
    if not texto: return pausa()
    print()
    print(f"  {R2}MD5:{RS}    {W}{hashlib.md5(texto.encode()).hexdigest()}{RS}")
    print(f"  {R2}SHA1:{RS}   {W}{hashlib.sha1(texto.encode()).hexdigest()}{RS}")
    print(f"  {R2}SHA256:{RS} {W}{hashlib.sha256(texto.encode()).hexdigest()}{RS}")
    pausa()

def util_b64():
    limpiar(); barra_menu("UTILITIES - BASE64 TOOL")
    print(f"  {R2}[1]{RS} {W}Encode{RS}")
    print(f"  {R2}[2]{RS} {W}Decode{RS}")
    op = input(f"\n  {R2}>>{RS} ").strip()
    texto = input(f"  {R2}Text{RS} > ")
    if not texto: return pausa()
    try:
        if op == "1": res = base64.b64encode(texto.encode()).decode()
        elif op == "2": res = base64.b64decode(texto).decode()
        else: print(f"  {D}[!] Invalid option{RS}"); return pausa()
        print(f"\n  {R2}Result:{RS} {W}{res}{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def menu_utilities():
    while True:
        try:
            limpiar(); print_banner()
            barra_menu("UTILITIES")
            print()
            menu_en_columnas([("1","ID Generator"),("2","Hasher"),("3","Base64 Tool"),("4","Token Decode"),("",""),("0","Back")])
            print()
            op = input(f"  {R2}>>{RS} ").strip().lower()
            if op == "1": util_id_gen()
            elif op == "2": util_hasher()
            elif op == "3": util_b64()
            elif op == "4": util_token_decode()
            elif op == "h": show_help()
            elif op == "0": return
            elif op == "x": sys.exit(0)
        except KeyboardInterrupt: return

def util_token_decode():
    limpiar(); barra_menu("UTILITIES - TOKEN DECODE")
    token = input(f"  {R2}Token{RS} > ").strip()
    if not token: return pausa()
    partes = token.split(".")
    if len(partes) != 3: print(f"  {D}[!] Not a valid token (must have 3 parts){RS}"); return pausa()
    try:
        uid = base64.b64decode(partes[0] + "==").decode()
        ts_ms = int(partes[1], 16)
        ts_dt = datetime.fromtimestamp(ts_ms / 1000)
        print(f"\n  {R2}User ID:{RS}      {W}{uid}{RS}")
        print(f"  {R2}Created:{RS}        {W}{ts_dt.strftime('%Y-%m-%d %H:%M:%S')}{RS}")
        print(f"  {R2}Age:{RS}     {W}{relatime(ts_ms)}{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()
