"""Plugin system: dynamic tool loading from ~/.config/0xytool/plugins/"""
from tools.base import *

PLUGIN_DIR = os.path.join(CONFIG_DIR, "plugins")
os.makedirs(PLUGIN_DIR, exist_ok=True)

_plugins = []

def cargar_plugins():
    global _plugins
    _plugins.clear()
    if not os.path.isdir(PLUGIN_DIR): return
    for fname in sorted(os.listdir(PLUGIN_DIR)):
        if fname.endswith(".py") and fname != "__init__.py":
            path = os.path.join(PLUGIN_DIR, fname)
            try:
                spec = importlib.util.spec_from_file_location(f"plugin_{fname[:-3]}", path)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    nombre = getattr(mod, "PLUGIN_NAME", fname[:-3])
                    desc = getattr(mod, "PLUGIN_DESC", "")
                    menu_fn = getattr(mod, "menu", None) or getattr(mod, "run", None)
                    if menu_fn:
                        _plugins.append({"name": nombre, "desc": desc, "fn": menu_fn, "file": fname})
                        log_evento(f"Plugin loaded: {nombre}")
            except Exception as e:
                log_evento(f"Error loading plugin {fname}: {e}")

def listar_plugins():
    if not _plugins: cargar_plugins()
    return _plugins

def ejecutar_plugin(idx):
    plugins = listar_plugins()
    if 0 <= idx < len(plugins):
        plugins[idx]["fn"]()

def menu_plugins():
    while True:
        try:
            plugins = listar_plugins()
            limpiar(); print_banner()
            barra_menu("PLUGINS")
            print()
            if not plugins:
                print(f"  {D}[!] No plugins installed.{RS}")
                print(f"  {D}Add .py scripts at: {PLUGIN_DIR}{RS}")
                print(f"  {D}Each plugin must have PLUGIN_NAME, PLUGIN_DESC and a menu() or run() function{RS}")
            else:
                items = [(str(i+1), f"{p['name']}: {p['desc']}") for i, p in enumerate(plugins)]
                items.append(("0", "Back"))
                menu_en_columnas(items)
            print()
            op = input(f"  {R2}>>{RS} ").strip()
            if op == "0": return
            elif op == "x": sys.exit(0)
            try:
                idx = int(op) - 1
                ejecutar_plugin(idx)
            except (ValueError, IndexError): pass
        except KeyboardInterrupt: return
