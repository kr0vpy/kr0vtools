import sys, os, time, base64, hashlib, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.base import centrar, relatime, UA, exportar_json
from tools.token import generar_token_discord

def test_centrar():
    result = centrar("hola", 20)
    stripped = result.strip()
    assert "hola" in stripped

def test_relatime():
    now = int(time.time() * 1000)
    assert "s" in relatime(now - 30000)
    assert "m" in relatime(now - 120000)
    assert "d" in relatime(now - 172800000)

def test_token_generado():
    tok = generar_token_discord()
    partes = tok.split(".")
    assert len(partes) == 3
    uid = base64.b64decode(partes[0] + "==").decode()
    ts_ms = int(partes[1], 16)
    assert len(uid) > 0
    assert ts_ms > 1420070400000

def test_token_decode():
    tok = generar_token_discord()
    partes = tok.split(".")
    uid = base64.b64decode(partes[0] + "==").decode()
    ts_ms = int(partes[1], 16)
    assert uid.isdigit()
    assert ts_ms > 1700000000000

def test_hasher():
    texto = "test123"
    assert hashlib.md5(texto.encode()).hexdigest() == "cc03e747a6afbbcbf8be7668acfebee5"
    assert hashlib.sha256(texto.encode()).hexdigest() == "ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae"

def test_ua():
    assert "Mozilla" in UA
    assert len(UA) >= 50

def test_centrar_ansi():
    text = "\x1b[31mtest\x1b[0m"
    result = centrar(text, 20)
    assert len(result.strip()) >= 6
