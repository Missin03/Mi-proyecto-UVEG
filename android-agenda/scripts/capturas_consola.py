"""Recorre la consola simulada con Playwright (Edge) y guarda una captura por sección.

La sección de versión carga el AAB real con el selector de archivos para que el navegador
calcule su huella SHA-256.
"""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
CONSOLA = (RAIZ / 'play' / 'consola' / 'index.html').as_uri()
AAB = RAIZ / 'app' / 'build' / 'outputs' / 'bundle' / 'release' / 'app-release.aab'
SALIDA = Path(os.path.abspath(RAIZ / '..' / '..' / '..' / 'capturas' / 'R4'))

with sync_playwright() as p:
    navegador = p.chromium.launch(channel='msedge')
    pagina = navegador.new_page(viewport={'width': 1366, 'height': 900}, locale='es-MX')
    pagina.goto(CONSOLA)
    for seccion in ('crear', 'ficha', 'configuracion', 'contenido'):
        pagina.evaluate(f"location.hash = '{seccion}'")
        pagina.wait_for_timeout(400)
        pagina.screenshot(path=SALIDA / f'consola_{seccion}.png', full_page=True)

    pagina.evaluate("location.hash = 'version'")
    pagina.set_input_files('#archivo', str(AAB))
    pagina.wait_for_selector('#zona.lista')
    pagina.screenshot(path=SALIDA / 'consola_version.png', full_page=True)

    pagina.evaluate("location.hash = 'precios'")
    pagina.wait_for_timeout(300)
    pagina.screenshot(path=SALIDA / 'consola_precios.png', full_page=True)

    pagina.evaluate("location.hash = 'resumen'")
    pagina.wait_for_timeout(300)
    pagina.screenshot(path=SALIDA / 'consola_checklist.png', full_page=True)
    pagina.click('#b-enviar')
    pagina.wait_for_timeout(300)
    pagina.screenshot(path=SALIDA / 'consola_envio.png', full_page=True)
    print(pagina.inner_text('#envio-msg'))
    navegador.close()
