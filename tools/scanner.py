from tools.base import *

SERVICIOS = {
    21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",
    110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",993:"IMAPS",995:"POP3S",
    1433:"MSSQL",1521:"Oracle",3306:"MySQL",3389:"RDP",5432:"PostgreSQL",
    5900:"VNC",6379:"Redis",8080:"HTTP-Proxy",8443:"HTTPS-Alt",27017:"MongoDB",
}
resultados_scan = []
lock_scan = threading.Lock()

def escanear_puerto(host, puerto, timeout):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        if s.connect_ex((host, puerto)) == 0:
            servicio = SERVICIOS.get(puerto, "Unknown")
            banner = ""
            try:
                s.send(b"\r\n")
                banner = s.recv(1024).decode("utf-8", errors="ignore").strip()[:60]
            except: pass
            with lock_scan: resultados_scan.append((puerto, servicio, banner))
        s.close()
    except: pass

def escanear_puerto_udp(host, puerto, timeout):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(timeout)
        s.sendto(b"", (host, puerto))
        try:
            s.recvfrom(1024)
            with lock_scan: resultados_scan.append((puerto, SERVICIOS.get(puerto, "Unknown"), "UDP"))
        except: pass
        s.close()
    except: pass

def port_scanner():
    try:
        limpiar(); barra_menu("PORT SCANNER")
        host = input(f"  {R2}Host/IP{RS} > ").strip()
        if not host: return pausa()
        try:
            ip = socket.gethostbyname(host)
            print(f"  {R1}[+] Resolved: {host} -> {ip}{RS}")
        except: print(f"  {D}[!] Could not resolve{RS}"); return pausa()

        modo = input(f"  {R2}Mode (T=TCP, U=UDP, B=both) [T]{RS} > ").strip().upper() or "T"
        rango = input(f"  {R2}Ports (1-1000, 80,443 or Enter for common){RS} > ").strip()
        puertos = []
        if not rango:
            puertos = list(SERVICIOS.keys())
            print(f"  {D}[+] Scanning {len(puertos)} common ports{RS}")
        else:
            for parte in rango.split(","):
                parte = parte.strip()
                try:
                    if "-" in parte:
                        i, f = map(int, parte.split("-"))
                        puertos.extend(range(i, f+1))
                    else: puertos.append(int(parte))
                except: print(f"  {D}[!] Invalid range: {parte}{RS}"); return pausa()

        timeout = 0.3 if len(puertos) > 500 else 0.5 if len(puertos) > 100 else 1.0
        resultados_scan.clear()
        sp = Spinner("Scanning ports"); sp.start()
        hilos = []
        for p in puertos:
            if modo in ("T", "A"):
                t = threading.Thread(target=escanear_puerto, args=(ip, p, timeout))
                t.daemon = True; hilos.append(t); t.start()
            if modo in ("U", "A"):
                t = threading.Thread(target=escanear_puerto_udp, args=(ip, p, timeout))
                t.daemon = True; hilos.append(t); t.start()
        for t in hilos: t.join()
        sp.stop()

        datos = [{"puerto": p, "servicio": sv, "banner": bn} for p, sv, bn in sorted(resultados_scan)]
        if datos:
            opc = input(f"  {R2}Export? (J=JSON, H=HTML, N=no) [N]{RS} > ").strip().upper()
            if opc == "J":
                path = exportar_json(f"scan_{ip}.json", datos)
                print(f"  {R1}[+] Saved to {path}{RS}")
            elif opc == "H":
                path = exportar_html(f"scan_{ip}.html", f"Scan: {ip}", ["Port","Service","Banner"],
                                     [[str(p), sv, bn] for p, sv, bn in sorted(resultados_scan)])
                print(f"  {R1}[+] HTML report at {path}{RS}")

        print(f"\n  {R1}[+] {len(resultados_scan)} open ports{RS}")
        if resultados_scan:
            print(f"\n  {R2}{'PORT':<8} {'SERVICE':<18} {'BANNER'}{RS}")
            print(f"  {'─' * 56}")
            for p, sv, bn in sorted(resultados_scan):
                print(f"  {W}{p:<8} {sv:<18} {bn}{RS}")
    except KeyboardInterrupt: print(f"\n  {D}[!] Cancelled{RS}")
    pausa()
