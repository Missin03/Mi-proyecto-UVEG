"""Automatiza el emulador para registrar tareas de ejemplo y tomar capturas.

Uso:
    python scripts/emulador.py tareas            # registra las tareas de ejemplo
    python scripts/emulador.py captura NOMBRE    # guarda capturas/R4/NOMBRE.png

El texto se pega desde el portapapeles del equipo (el emulador lo comparte) porque
`adb shell input text` no admite acentos.
"""
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ADB = os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk', 'platform-tools', 'adb.exe')
PAQUETE = 'io.github.missin03.agendaacademica'
CAPTURAS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'capturas', 'R4'))

TAREAS = [
    ('Estadía profesional', 'Plan de proyecto con cronograma',
     'Firma del asesor organizacional en todas las hojas.', '2026-10-07', 'estado_completada'),
    ('Inglés IV', 'Presentación oral sobre tecnología',
     'Video de tres minutos con subtítulos.', '2026-10-09', 'estado_pendiente'),
    ('Bases de datos', 'Modelo entidad-relación de la biblioteca',
     'Diagrama con cardinalidades y diccionario de datos.', '2026-10-14', 'estado_pendiente'),
    ('Matemáticas discretas', 'Ejercicios de grafos y árboles', '', '2026-10-16', 'estado_pendiente'),
    ('Despliegue de aplicaciones', 'Publicación simulada en Google Play',
     'Ficha, políticas, AAB firmado y comunicado de lanzamiento.', '2026-10-21', 'estado_curso'),
]


def adb(*args):
    return subprocess.run([ADB, *args], capture_output=True, text=True, encoding='utf-8').stdout


def nodos():
    adb('shell', 'uiautomator', 'dump', '/sdcard/ui.xml')
    return ET.fromstring(adb('shell', 'cat', '/sdcard/ui.xml')).iter('node')


def centro(nodo):
    x1, y1, x2, y2 = map(int, re.findall(r'\d+', nodo.get('bounds')))
    return (x1 + x2) // 2, (y1 + y2) // 2


def tocar(id_recurso=None, texto=None):
    for n in nodos():
        if (id_recurso and n.get('resource-id') == f'{PAQUETE}:id/{id_recurso}') or \
                (texto and n.get('text') == texto):
            adb('shell', 'input', 'tap', *map(str, centro(n)))
            time.sleep(0.6)
            return
    raise RuntimeError(f'No se encontró {id_recurso or texto}')


def escribir(id_recurso, valor):
    if not valor:
        return
    tocar(id_recurso)
    subprocess.run(['powershell', '-NoProfile', '-Command', 'Set-Clipboard -Value $env:TEXTO'],
                   env={**os.environ, 'TEXTO': valor}, check=True)
    time.sleep(0.8)
    adb('shell', 'input', 'keyevent', '279')  # KEYCODE_PASTE
    time.sleep(0.4)


def registrar_tareas():
    for materia, titulo, descripcion, fecha, estado in TAREAS:
        tocar('nueva')
        time.sleep(1)
        escribir('materia_texto', materia)
        escribir('titulo_texto', titulo)
        escribir('descripcion_texto', descripcion)
        escribir('fecha_texto', fecha)
        adb('shell', 'input', 'keyevent', '111')  # cierra el teclado
        time.sleep(0.5)
        tocar(estado)
        tocar('guardar')
        time.sleep(1)


def captura(nombre):
    os.makedirs(CAPTURAS, exist_ok=True)
    adb('shell', 'screencap', '-p', '/sdcard/captura.png')
    destino = os.path.join(CAPTURAS, nombre + '.png')
    adb('pull', '/sdcard/captura.png', destino)
    print(destino)


if __name__ == '__main__':
    if sys.argv[1] == 'tareas':
        registrar_tareas()
    elif sys.argv[1] == 'captura':
        captura(sys.argv[2])
    elif sys.argv[1] == 'tocar':
        tocar(texto=sys.argv[2])
    elif sys.argv[1] == 'tocar-id':
        tocar(id_recurso=sys.argv[2])
