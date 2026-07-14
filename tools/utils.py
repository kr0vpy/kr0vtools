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

def util_id_gen():
    limpiar(); barra_menu("UTILITIES - ID GENERATOR")
    print(f"  {D}Genera IDs ofuscados (cortos y unicos){RS}\n")
    try:
        cant = int(input(f"  {R2}Cuantos IDs?{RS} > ").strip())
        if cant < 1 or cant > 100: cant = 10
    except: cant = 10
    key = random.randint(0x10000, 0xFFFFFF)
    ids = []
    ts = int(time.time() * 1000)
    for i in range(cant):
        raw = (ts << 16) + (i << 8) + random.randint(0, 255)
        oid = _obfuscate_id(raw, key)
        ids.append(oid)
        print(f"  [{i+1:>3}] {W}{oid}{RS}")
    print(f"\n  {D}(clave de ofuscacion: {key:06X}){RS}")
    guardar = input(f"\n  {R2}Guardar en ids.txt? (s/N){RS} > ").strip().lower()
    if guardar == "s":
        with open("ids.txt", "w") as f:
            f.write(f"# key={key:06X}\n")
            f.write("\n".join(ids))
        print(f"  {R1}[+] Guardado{RS}")
    pausa()

def util_hasher():
    limpiar(); barra_menu("UTILITIES - HASHER")
    texto = input(f"  {R2}Texto a hashear{RS} > ")
    if not texto: return pausa()
    print()
    print(f"  {R2}MD5:{RS}    {W}{hashlib.md5(texto.encode()).hexdigest()}{RS}")
    print(f"  {R2}SHA1:{RS}   {W}{hashlib.sha1(texto.encode()).hexdigest()}{RS}")
    print(f"  {R2}SHA256:{RS} {W}{hashlib.sha256(texto.encode()).hexdigest()}{RS}")
    pausa()

def util_b64():
    limpiar(); barra_menu("UTILITIES - BASE64 TOOL")
    print(f"  {R2}[1]{RS} {W}Codificar{RS}")
    print(f"  {R2}[2]{RS} {W}Decodificar{RS}")
    op = input(f"\n  {R2}>>{RS} ").strip()
    texto = input(f"  {R2}Texto{RS} > ")
    if not texto: return pausa()
    try:
        if op == "1": res = base64.b64encode(texto.encode()).decode()
        elif op == "2": res = base64.b64decode(texto).decode()
        else: print(f"  {D}[!] Opcion invalida{RS}"); return pausa()
        print(f"\n  {R2}Resultado:{RS} {W}{res}{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def menu_utilities():
    while True:
        try:
            limpiar(); print_banner()
            barra_menu("UTILITIES")
            print()
            menu_en_columnas([("1","ID Generator"),("2","Hasher"),("3","Base64 Tool"),("4","Token Decode"),("",""),("0","Volver")])
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
    if len(partes) != 3: print(f"  {D}[!] No es un token valido (debe tener 3 partes){RS}"); return pausa()
    try:
        uid = base64.b64decode(partes[0] + "==").decode()
        ts_ms = int(partes[1], 16)
        ts_dt = datetime.fromtimestamp(ts_ms / 1000)
        print(f"\n  {R2}User ID:{RS}      {W}{uid}{RS}")
        print(f"  {R2}Creado:{RS}        {W}{ts_dt.strftime('%Y-%m-%d %H:%M:%S')}{RS}")
        print(f"  {R2}Antiguedad:{RS}     {W}{relatime(ts_ms)}{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()
