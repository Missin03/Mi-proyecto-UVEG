"""Recorre la App Store Connect simulada con Playwright (Edge) y guarda una captura por sección."""
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
PAGINA = (RAIZ / 'appstore' / 'connect' / 'index.html').as_uri()
SALIDA = RAIZ.parents[2] / 'capturas' / 'R5'
SALIDA.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    navegador = p.chromium.launch(channel='msedge')
    pagina = navegador.new_page(viewport={'width': 1366, 'height': 900}, locale='es-MX')
    errores = []
    pagina.on('pageerror', lambda e: errores.append(str(e)))
    pagina.goto(PAGINA)
    for seccion in ('xcode', 'nueva', 'testflight', 'version', 'informacion', 'privacidad', 'precios', 'revision'):
        pagina.evaluate(f"location.hash = '{seccion}'")
        pagina.wait_for_timeout(700)
        pagina.screenshot(path=SALIDA / f'connect_{seccion}.png', full_page=True)
    print(pagina.inner_text('#envio-msg'))
    pagina.click('#b-enviar')
    pagina.wait_for_timeout(300)
    pagina.screenshot(path=SALIDA / 'connect_envio.png', full_page=True)
    navegador.close()
print('errores de JavaScript:', errores or 'ninguno')
