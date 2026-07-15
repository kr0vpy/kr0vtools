#!/usr/bin/env python3
from tools.base import *
from tools.webhook import menu_webhook
from tools.token import menu_token
from tools.scanner import port_scanner
from tools.osint import menu_osint
from tools.utils import menu_utilities
from tools.network import menu_network
from tools.web import menu_web
from tools.social import menu_social
from tools.sqli import menu_sqli
from tools.plugins import menu_plugins, listar_plugins, cargar_plugins
from tools.nuke import menu_nuke

PASSWORD = "tools"

def login():
    for intento in range(3):
        limpiar()
        p = pad_centro()
        print()
        print()
        for li in ART.rstrip("\n").split("\n"):
            print(p + R1 + li + RS)
        print()
        barra_menu("ACCESS")
        print()
        pwd = leer_mascarado(f"{p}{R2}Password{RS} > ")
        if pwd == PASSWORD:
            print(f"\n{p}{R1}[+] Access granted.{RS}\n")
            time.sleep(1)
            return True
        print(f"\n{p}{D}[!] Wrong password. Attempt {intento+1}/3{RS}")
        pausa()
    print(f"\n{p}{D}[!] Too many failed attempts. Exiting...{RS}")
    sys.exit(1)

def main():
    global CFG
    cfg_data = cargar_config()
    CFG.update(cfg_data)
    MODO_COMPACTO[0] = CFG.get("modo_compacto", False)
    cargar_plugins()
    login()
    log_evento("Session started")
    setup_readline(["1","2","4","5","6","7","8","9","u","p","n","h","c","x","0"])

    while True:
        try:
            limpiar()
            print_banner()
            p = pad_centro()
            barra_menu("TOOLS ↓")
            menu_horizontal([
                ("DISCORD", "",    [("1","Webhook"),("2","Tokens"),("N","Nuker")]),
                ("OSINT",   "",    [("4","Osint"),  ("5","Social")]),
                ("NETWORK", "",    [("6","Scanner"),("7","Network"),("8","Scraping")]),
                ("UTILITY", "",    [("U","Utils"),  ("9","VulnScan"),("P","Plugins")]),
            ])
            print(f"{p}{D}{'─' * ANCHO}{RS}")
            print(f"{p}   {W}→ Extras:{RS}  {R2}[H]{RS} {W}Help{RS}  {R2}[C]{RS} {W}Compact mode{RS}  {R2}[X]{RS} {W}Exit{RS}")
            print(f"{p}{D}{'─' * ANCHO}{RS}")
            op = input(f"{p}{R2}>>{RS} ").strip().lower()
            if op == "1": menu_webhook()
            elif op == "2": menu_token()
            elif op == "4": menu_osint()
            elif op == "5": menu_social()
            elif op == "6": port_scanner()
            elif op == "7": menu_network()
            elif op == "8": menu_web()
            elif op == "9": menu_sqli()
            elif op == "u": menu_utilities()
            elif op == "p": menu_plugins()
            elif op == "n": menu_nuke()
            elif op == "c":
                MODO_COMPACTO[0] = not MODO_COMPACTO[0]
                guardar_config(modo_compacto=MODO_COMPACTO[0])
                print(f"{p}{R1}[+] Compact mode: {'ON' if MODO_COMPACTO[0] else 'OFF'}{RS}")
                time.sleep(0.5)
            elif op == "h": show_help()
            elif op == "x":
                log_evento("Session ended")
                print(f"\n{p}{D}Exiting...{RS}")
                sys.exit(0)
            else:
                print(f"\n{p}{D}[!] Invalid option{RS}")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print(f"\n\n{p}{D}[!] Ctrl+C - press Enter to return...{RS}")
            try: input()
            except: pass

if __name__ == "__main__":
    main()
