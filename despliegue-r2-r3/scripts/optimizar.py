"""Optimiza las imágenes y minifica CSS/JS antes de empaquetar.

Uso: python scripts/optimizar.py
Genera static/css/app.min.css, static/js/app.min.js, static/img/icono.png
y deja el resumen de pesos en evidencias/optimizacion.json.
"""
import json
import re
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent


def minificar_css(texto):
    texto = re.sub(r'/\*.*?\*/', '', texto, flags=re.S)
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'\s*([{}:;,>])\s*', r'\1', texto)
    return texto.replace(';}', '}').strip()


def minificar_js(texto):
    texto = re.sub(r'^\s*//.*$', '', texto, flags=re.M)
    return re.sub(r'\s+', ' ', texto).strip()


def main():
    resultados = []
    for tipo, funcion in (('css', minificar_css), ('js', minificar_js)):
        origen = RAIZ / f'static/{tipo}/app.{tipo}'
        destino = RAIZ / f'static/{tipo}/app.min.{tipo}'
        destino.write_text(funcion(origen.read_text(encoding='utf-8')), encoding='utf-8')
        resultados.append({'archivo': f'{tipo}/app.{tipo}', 'original_bytes': origen.stat().st_size,
                           'optimizado_bytes': destino.stat().st_size})

    # El icono original es de 256 px sin compresión; en la interfaz se muestra a 38 px.
    original = RAIZ / 'src/img/icono.png'
    optimizado = RAIZ / 'static/img/icono.png'
    with Image.open(original) as imagen:
        imagen.convert('RGB').resize((64, 64), Image.Resampling.LANCZOS).quantize(colors=32).save(
            optimizado, optimize=True)
    resultados.append({'archivo': 'img/icono.png', 'original_bytes': original.stat().st_size,
                       'optimizado_bytes': optimizado.stat().st_size})

    for r in resultados:
        r['reduccion'] = f"{100 - r['optimizado_bytes'] * 100 / r['original_bytes']:.1f} %"
        print(f"{r['archivo']:<16} {r['original_bytes']:>8} B -> {r['optimizado_bytes']:>6} B  ({r['reduccion']})")
    (RAIZ / 'evidencias').mkdir(exist_ok=True)
    (RAIZ / 'evidencias/optimizacion.json').write_text(json.dumps(resultados, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
