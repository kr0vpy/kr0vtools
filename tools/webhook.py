from tools.base import *

def pedir_webhook():
    url = input(f"  {R2}Webhook URL{RS} > ").strip()
    if not url.startswith("https://discord.com/api/webhooks/"):
        print(f"  {D}[!] Invalid webhook URL{RS}")
        return None
    return url

def webhook_spammer():
    try:
        limpiar(); barra_menu("DISCORD WEBHOOK SPAMMER")
        url = pedir_webhook()
        if not url: return pausa()
        mensaje = input(f"  {R2}Message{RS} > ").strip()
        if not mensaje: return
        try:
            cantidad = int(input(f"  {R2}Amount{RS} > ").strip())
            if cantidad < 1: raise ValueError
        except:
            print(f"  {D}[!] Invalid amount{RS}"); return pausa()
        try:
            delay = float(input(f"  {R2}Delay (sec){RS} > ").strip())
            if delay < 0: raise ValueError
        except: delay = 0.5
        print(f"\n  {D}[!] Sending {cantidad} messages...{RS}\n")
        data = json.dumps({"content": mensaje}).encode()
        headers = {"Content-Type": "application/json", "User-Agent": UA}
        enviados = errores = 0
        for i in range(1, cantidad + 1):
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    enviados += 1
                    print(f"  [{R2}{enviados+errores:>4}{RS}/{cantidad}] {R2}OK{RS} (HTTP {resp.status})")
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    retry = int(e.headers.get("Retry-After", 1))
                    if retry > 30:
                        errores += 1
                        print(f"  [{enviados+errores:>4}/{cantidad}] {D}Rate limit - saltando{RS}")
                    else:
                        print(f"  {D}[!] Rate limit - esperando {retry}s...{RS}")
                        time.sleep(retry + 0.5); continue
                else:
                    errores += 1
                    print(f"  [{enviados+errores:>4}/{cantidad}] {D}HTTP {e.code}{RS}")
            except Exception as e:
                errores += 1
                print(f"  [{enviados+errores:>4}/{cantidad}] {D}Error: {e}{RS}")
            barra_progreso(i, cantidad, prefijo="Spam")
            time.sleep(delay)
        print(f"\n  {R1}[+] Done: {enviados} sent, {errores} errors{RS}")
    except KeyboardInterrupt: print(f"\n  {D}[!] Cancelled{RS}")
    pausa()

def webhook_info():
    limpiar(); barra_menu("DISCORD WEBHOOK INFO")
    url = pedir_webhook()
    if not url: return pausa()
    print()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            d = json.loads(resp.read().decode())
        print(f"  {R2}ID:{RS}            {W}{d.get('id', 'N/A')}{RS}")
        print(f"  {R2}Nombre:{RS}         {W}{d.get('name', 'N/A')}{RS}")
        print(f"  {R2}Channel ID:{RS}      {W}{d.get('channel_id', 'N/A')}{RS}")
        print(f"  {R2}Guild ID:{RS}        {W}{d.get('guild_id', 'N/A')}{RS}")
        print(f"  {R2}Token:{RS}           {W}{d.get('token', 'N/A')}{RS}")
        print(f"  {R2}Created:{RS}          {W}{datetime.fromtimestamp(((int(d.get('id', '0')) >> 22) + 1420070400000) / 1000) if d.get('id') else 'N/A'}{RS}")
        user = d.get('user', {})
        if user:
            print(f"  {R2}Created by:{RS}     {W}{user.get('username', 'N/A')}#{user.get('discriminator', '0')}{RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def webhook_deleter():
    limpiar(); barra_menu("DISCORD WEBHOOK DELETER")
    url = pedir_webhook()
    if not url: return pausa()
    print()
    conf = input(f"  {D}Are you sure you want to delete this webhook? (y/N) > {RS}").strip().lower()
    if conf != "s": print(f"  {D}[!] Cancelled{RS}"); return pausa()
    try:
        req = urllib.request.Request(url, method="DELETE", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"  {R1}[+] Webhook deleted (HTTP {resp.status}){RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def webhook_embed():
    limpiar(); barra_menu("DISCORD WEBHOOK EMBED")
    url = pedir_webhook()
    if not url: return pausa()
    titulo = input(f"  {R2}Title{RS} > ").strip()
    desc = input(f"  {R2}Description{RS} > ").strip()
    color = input(f"  {R2}Color (hex, eg: 5865F2){RS} > ").strip() or "5865F2"
    footer = input(f"  {R2}Footer{RS} > ").strip()
    try: color_int = int(color, 16)
    except: color_int = 0x5865F2
    embed = {"title": titulo, "description": desc, "color": color_int, "timestamp": datetime.utcnow().isoformat()}
    if footer: embed["footer"] = {"text": footer}
    payload = json.dumps({"embeds": [embed]}).encode()
    headers = {"Content-Type": "application/json", "User-Agent": UA}
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"  {R1}[+] Embed sent (HTTP {resp.status}){RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def webhook_spoof():
    limpiar(); barra_menu("DISCORD WEBHOOK SPOOF")
    url = pedir_webhook()
    if not url: return pausa()
    nuevo_nombre = input(f"  {R2}New name{RS} > ").strip()
    avatar_url = input(f"  {R2}Avatar URL (optional){RS} > ").strip()
    payload = {}
    if nuevo_nombre: payload["name"] = nuevo_nombre
    if avatar_url: payload["avatar"] = avatar_url
    if not payload: print(f"  {D}[!] No data to change{RS}"); return pausa()
    headers = {"Content-Type": "application/json", "User-Agent": UA}
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="PATCH")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"  {R1}[+] Webhook modified (HTTP {resp.status}){RS}")
    except Exception as e: print(f"  {D}[!] Error: {e}{RS}")
    pausa()

def menu_webhook():
    while True:
        try:
            limpiar(); print_banner()
            barra_menu("DISCORD - WEBHOOK TOOLS")
            print()
            menu_en_columnas([("1","Spammer"),("2","Info"),("3","Deleter"),("4","Embed"),("5","Spoof"),("0","Back")])
            print()
            op = input(f"  {R2}>>{RS} ").strip().lower()
            if op == "1": webhook_spammer()
            elif op == "2": webhook_info()
            elif op == "3": webhook_deleter()
            elif op == "4": webhook_embed()
            elif op == "5": webhook_spoof()
            elif op == "h": show_help()
            elif op == "0": return
            elif op == "x": sys.exit(0)
        except KeyboardInterrupt: return
