"""Genera el icono y el splash del proyecto de Xcode y las capturas para App Store Connect.

- AppIcon 1024 x 1024 en RGB (App Store rechaza iconos con transparencia).
- Splash de 2732 x 2732 con el icono al centro.
- Capturas con WebKit (motor de Safari): iPhone de 6.9" (1320 x 2868) e iPad de 13" (2064 x 2752).
"""
import json
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ.parent / 'android-agenda' / 'scripts'))
from recursos_graficos import dibujar_icono  # noqa: E402  mismo diseño que el icono de Android

ASSETS = RAIZ / 'ios' / 'App' / 'App' / 'Assets.xcassets'
CAPTURAS = RAIZ / 'appstore' / 'capturas'

TAREAS = [
    ('Estadía profesional', 'Plan de proyecto con cronograma', 'Firma del asesor organizacional en todas las hojas.', '2026-10-07', 'completada'),
    ('Inglés IV', 'Presentación oral sobre tecnología', 'Video de tres minutos con subtítulos.', '2026-10-09', 'pendiente'),
    ('Bases de datos', 'Modelo entidad-relación de la biblioteca', 'Diagrama con cardinalidades y diccionario de datos.', '2026-10-14', 'pendiente'),
    ('Matemáticas discretas', 'Ejercicios de grafos y árboles', '', '2026-10-16', 'pendiente'),
    ('Despliegue de aplicaciones', 'Publicación simulada en App Store', 'Metadatos, capturas, privacidad y envío a revisión.', '2026-10-21', 'en_curso'),
]
DATOS = json.dumps([dict(id=i, materia=m, titulo=t, descripcion=d, fecha=f, estado=e)
                    for i, (m, t, d, f, e) in enumerate(TAREAS)], ensure_ascii=False)
DISPOSITIVOS = {
    'iphone-69': dict(viewport={'width': 440, 'height': 956}, device_scale_factor=3, is_mobile=True, has_touch=True),
    'ipad-13': dict(viewport={'width': 1032, 'height': 1376}, device_scale_factor=2, is_mobile=True, has_touch=True),
}


def iconos():
    icono = dibujar_icono(1024).convert('RGB')
    icono.save(ASSETS / 'AppIcon.appiconset' / 'AppIcon-512@2x.png', optimize=True)
    splash = Image.new('RGB', (2732, 2732), (243, 246, 248))
    pequeno = dibujar_icono(560)
    splash.paste(pequeno, (1086, 1086), pequeno)
    for nombre in ('splash-2732x2732.png', 'splash-2732x2732-1.png', 'splash-2732x2732-2.png'):
        splash.save(ASSETS / 'Splash.imageset' / nombre, optimize=True)
    icono.save(RAIZ / 'appstore' / 'icono-1024.png', optimize=True)


def capturas():
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    url = (RAIZ / 'www' / 'index.html').as_uri()
    with sync_playwright() as p:
        navegador = p.webkit.launch()
        for nombre, opciones in DISPOSITIVOS.items():
            pagina = navegador.new_page(**opciones, locale='es-MX')
            pagina.add_init_script(f"localStorage.setItem('agenda.tareas.v1', {json.dumps(DATOS)})")
            pagina.goto(url)
            pagina.screenshot(path=CAPTURAS / f'{nombre}-1-lista.png')
            if nombre.startswith('iphone'):
                pagina.click('[data-filtro="pendiente"]')
                pagina.screenshot(path=CAPTURAS / f'{nombre}-2-filtro.png')
                pagina.click('#nueva')
                pagina.fill('#f-materia', 'Redes')
                pagina.click('#guardar')
                pagina.screenshot(path=CAPTURAS / f'{nombre}-3-validacion.png')
                pagina.click('#cancelar')
                pagina.click('#abrir-menu')
                pagina.click('[data-legal="privacidad"]')
                pagina.screenshot(path=CAPTURAS / f'{nombre}-4-privacidad.png')
            pagina.close()
        navegador.close()
    for f in sorted(CAPTURAS.glob('*.png')):
        print(f.name, Image.open(f).size)


if __name__ == '__main__':
    (RAIZ / 'appstore').mkdir(exist_ok=True)
    iconos()
    capturas()
