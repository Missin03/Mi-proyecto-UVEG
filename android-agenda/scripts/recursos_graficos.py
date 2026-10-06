"""Genera los recursos gráficos de la ficha de Play Store a partir del mismo diseño del icono.

- play/icono-512.png          icono de alta resolución (512 x 512, 32 bits)
- play/grafico-1024x500.png   gráfico de funciones (1024 x 500, sin transparencia)
- play/capturas/*.png         capturas del emulador recortadas sin barra de estado
"""
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SALIDA = os.path.join(RAIZ, 'play')
CAPTURAS = os.path.abspath(os.path.join(RAIZ, '..', '..', '..', 'capturas', 'R4'))
VERDE = (18, 99, 72)
BLANCO = (255, 255, 255)
TINTA = (20, 42, 58)


def dibujar_icono(lado, fondo=True):
    """Calendario con palomita sobre la cuadrícula de 108 unidades del icono adaptable."""
    escala = 4
    s = lado * escala / 108
    im = Image.new('RGBA', (lado * escala,) * 2, VERDE + (255,) if fondo else (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p = lambda x, y: (x * s, y * s)
    d.rounded_rectangle([p(34, 36), p(74, 76)], radius=6 * s, outline=BLANCO, width=round(4 * s))
    d.rounded_rectangle([p(34, 36), p(74, 47)], radius=6 * s, fill=BLANCO)
    d.rectangle([p(34, 42), p(74, 47)], fill=BLANCO)
    for x in (44, 64):
        d.line([p(x, 30), p(x, 39)], fill=BLANCO, width=round(4 * s))
        d.ellipse([p(x - 2, 28), p(x + 2, 32)], fill=BLANCO)
    d.line([p(44, 61), p(51, 68), p(65, 54)], fill=BLANCO, width=round(5 * s), joint='curve')
    for x, y in ((44, 61), (65, 54)):
        d.ellipse([p(x - 2.5, y - 2.5), p(x + 2.5, y + 2.5)], fill=BLANCO)
    return im.resize((lado, lado), Image.LANCZOS)


def fuente(tam, negrita=False):
    nombre = 'segoeuib.ttf' if negrita else 'segoeui.ttf'
    return ImageFont.truetype(os.path.join(os.environ['WINDIR'], 'Fonts', nombre), tam)


def grafico_funciones():
    im = Image.new('RGB', (1024, 500), VERDE)
    d = ImageDraw.Draw(im)
    icono = dibujar_icono(340)
    im.paste(icono, (10, 80), icono)
    d.text((330, 150), 'Agenda Académica', font=fuente(64, True), fill=BLANCO)
    d.text((332, 240), 'Tus tareas escolares por materia y fecha', font=fuente(32), fill=(220, 240, 230))
    d.text((332, 300), 'Sin anuncios · Sin cuentas · Sin permisos', font=fuente(26), fill=(190, 225, 210))
    return im


def recortar_capturas():
    destino = os.path.join(SALIDA, 'capturas')
    os.makedirs(destino, exist_ok=True)
    for nombre, archivo in (('telefono-1', 'R4_lista'), ('telefono-2', 'R4_lista_abajo'),
                            ('telefono-3', 'R4_validacion'), ('telefono-4', 'R4_privacidad'),
                            ('tableta-1', 'R4_tableta')):
        im = Image.open(os.path.join(CAPTURAS, archivo + '.png')).convert('RGB')
        im.save(os.path.join(destino, nombre + '.png'), optimize=True)
        print(nombre, im.size)


if __name__ == '__main__':
    os.makedirs(SALIDA, exist_ok=True)
    dibujar_icono(512).save(os.path.join(SALIDA, 'icono-512.png'), optimize=True)
    grafico_funciones().save(os.path.join(SALIDA, 'grafico-1024x500.png'), optimize=True)
    recortar_capturas()
    for f in ('icono-512.png', 'grafico-1024x500.png'):
        im = Image.open(os.path.join(SALIDA, f))
        print(f, im.size, im.mode, os.path.getsize(os.path.join(SALIDA, f)), 'bytes')
