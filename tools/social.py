from tools.base import *

NOMBRES = ["Juan","Maria","Carlos","Ana","Luis","Sofia","Pedro","Elena","Diego","Laura",
           "Miguel","Isabel","Alex","Emma","David","Mia","Jose","Clara","Antonio","Valentina"]
APELLIDOS = ["Garcia","Rodriguez","Lopez","Martinez","Hernandez","Gonzalez","Perez",
             "Sanchez","Ramirez","Torres","Flores","Rivera","Gomez","Diaz","Cruz","Morales"]
CIUDADES = ["Madrid","Barcelona","CDMX","Bogota","Lima","Santiago","Bs As","Quito"]
DOMINIOS = ["gmail.com","hotmail.com","outlook.com","yahoo.com","proton.me"]

def soc_fake_id():
    limpiar(); barra_menu("SOCIAL - FAKE IDENTITY")
    nombre = random.choice(NOMBRES)
    apellido = random.choice(APELLIDOS)
    apellido2 = random.choice(APELLIDOS)
    ciudad = random.choice(CIUDADES)
    edad = random.randint(18, 80)
    dia = random.randint(1, 28)
    mes = random.randint(1, 12)
    anio = datetime.now().year - edad
    email = f"{nombre.lower()}.{apellido.lower()}{random.randint(1,99)}@{random.choice(DOMINIOS)}"
    cc_num = "".join([str(random.randint(0,9)) for _ in range(16)])
    cc_venc = f"{random.randint(1,12):02d}/{random.randint(25,30)}"
    cc_cvv = f"{random.randint(100,999)}"
    tel = f"+34{random.randint(600000000, 799999999)}"
    print(f"""
  {R2}Nombre:{RS}      {W}{nombre} {apellido} {apellido2}{RS}
  {R2}Edad:{RS}        {W}{edad}{RS}
  {R2}DOB:{RS}        {W}{dia:02d}/{mes:02d}/{anio}{RS}
  {R2}Ciudad:{RS}     {W}{ciudad}{RS}
  {R2}Email:{RS}      {W}{email}{RS}
  {R2}Telefono:{RS}   {W}{tel}{RS}
  {R2}Tarjeta:{RS}    {W}{cc_num} ({cc_venc} CVV:{cc_cvv}){RS}
""")
    guardar = input(f"  {R2}Guardar? (s/N){RS} > ").strip().lower()
    if guardar == "s":
        ident = {"nombre": f"{nombre} {apellido} {apellido2}", "edad": edad,
                 "email": email, "telefono": tel, "tarjeta": cc_num}
        path = exportar_json(f"fake_id_{int(time.time())}.json", ident)
        print(f"  {R1}[+] Guardado en {path}{RS}")
    pausa()

def soc_qr():
    limpiar(); barra_menu("SOCIAL - QR GENERATOR")
    try: import qrcode
    except ImportError:
        print(f"  {D}[!] qrcode no instalado. Instala: pip install qrcode{pillow}{RS}")
    data = input(f"  {R2}Texto o URL{RS} > ").strip()
    if not data: return pausa()
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=4, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        path = f"qr_{int(time.time())}.png"
        img.save(path)
        print(f"  {R1}[+] QR guardado en {path}{RS}")
        print(f"  {D}[!] Abrelo con cualquier visor de imagenes{RS}")
    except ImportError:
        print(f"\n  {R2}Texto codificado en QR:{RS}")
        print(f"  {W}{data}{RS}")
        print(f"  {D}Usa https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(data)}{RS}")
    pausa()

def soc_obfuscator():
    limpiar(); barra_menu("SOCIAL - LINK OBFUSCATOR")
    url = input(f"  {R2}URL a ofuscar{RS} > ").strip()
    if not url: return pausa()
    print(f"\n  {R2}Metodos:{RS}")
    print(f"  {W}[1] Base64 encode{RS}")
    print(f"  {W}[2] URL encoded{RS}")
    print(f"  {W}[3] TinyURL (acortador){RS}")
    op = input(f"\n  {R2}Selecciona{RS} > ").strip()
    if op == "1":
        enc = base64.b64encode(url.encode()).decode()
        print(f"\n  {R1}[+] Base64:{RS}\n  {W}{enc}{RS}")
    elif op == "2":
        enc = urllib.parse.quote(url)
        print(f"\n  {R1}[+] URL encoded:{RS}\n  {W}{enc}{RS}")
    elif op == "3":
        try:
            req = urllib.request.Request(f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=10) as r:
                print(f"\n  {R1}[+] Acortado:{RS}\n  {W}{r.read().decode().strip()}{RS}")
        except: print(f"  {D}[!] Error al acortar{RS}")
    else: print(f"  {D}[!] Opcion invalida{RS}")
    pausa()

def soc_ua():
    limpiar(); barra_menu("SOCIAL - USER AGENT GENERATOR")
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/125.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/125.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    ]
    print(f"  {D}User-Agent aleatorio generado:{RS}\n")
    for _ in range(5):
        print(f"  {W}{random.choice(uas)}{RS}\n")
    pausa()

def menu_social():
    while True:
        try:
            limpiar(); print_banner()
            barra_menu("SOCIAL ENGINEERING TOOLS")
            print()
            menu_en_columnas([("1","Fake Identity"),("2","QR Generator"),
                             ("3","Link Obfuscator"),("4","UA Generator"),("",""),("0","Volver")])
            print()
            op = input(f"  {R2}>>{RS} ").strip().lower()
            if op == "1": soc_fake_id()
            elif op == "2": soc_qr()
            elif op == "3": soc_obfuscator()
            elif op == "4": soc_ua()
            elif op == "h": show_help()
            elif op == "0": return
            elif op == "x": sys.exit(0)
        except KeyboardInterrupt: return
