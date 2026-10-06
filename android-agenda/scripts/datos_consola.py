"""Lee el AAB y el APK reales y escribe play/consola/datos.js para la consola simulada.

Así la pantalla de carga muestra el tamaño, la huella SHA-256, la versión y el tamaño de
descarga calculados del archivo de distribución que se generó con Gradle.
"""
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SDK = os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk')
AAPT2 = os.path.join(SDK, 'build-tools', '36.0.0', 'aapt2.exe')
APK = os.path.join(RAIZ, 'app', 'build', 'outputs', 'apk', 'release', 'app-release.apk')
AAB = os.path.join(RAIZ, 'app', 'build', 'outputs', 'bundle', 'release', 'app-release.aab')
APKS = os.path.join(RAIZ, 'app', 'build', 'outputs', 'agenda.apks')


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, 'rb') as f:
        for bloque in iter(lambda: f.read(1 << 16), b''):
            h.update(bloque)
    return h.hexdigest()


def badging():
    salida = subprocess.run([AAPT2, 'dump', 'badging', APK], capture_output=True, text=True, encoding='utf-8').stdout
    campo = lambda patron: re.search(patron, salida).group(1)
    permisos = [p for p in re.findall(r"uses-permission: name='([^']+)'", salida) if 'DYNAMIC_RECEIVER' not in p]
    return {
        'paquete': campo(r"package: name='([^']+)'"),
        'versionCode': int(campo(r"versionCode='(\d+)'")),
        'versionName': campo(r"versionName='([^']+)'"),
        'minSdk': int(campo(r"minSdkVersion:'(\d+)'")),
        'targetSdk': int(campo(r"targetSdkVersion:'(\d+)'")),
        'permisos': permisos,
    }


def tamano_descarga():
    """Rango de descarga por dispositivo según bundletool get-size (APK divididos)."""
    entorno = {**os.environ, 'JAVA_HOME': os.path.join(os.environ['USERPROFILE'], '.jdks', 'jbr-21.0.11')}
    salida = subprocess.run(
        [os.path.join(RAIZ, 'gradlew.bat'), '-q', ':app:bundletool',
         '-Pbt=get-size total --apks=build/outputs/agenda.apks --dimensions=SCREEN_DENSITY'],
        cwd=RAIZ, capture_output=True, text=True, env=entorno).stdout
    valores = [int(x) for x in re.findall(r',(\d+),\d+', salida)]
    return min(valores), max(valores)


if __name__ == '__main__':
    minimo, maximo = tamano_descarga()
    datos = {
        **badging(),
        'aab': {'nombre': os.path.basename(AAB), 'bytes': os.path.getsize(AAB), 'sha256': sha256(AAB),
                'fecha': datetime.fromtimestamp(os.path.getmtime(AAB)).strftime('%d/%m/%Y %H:%M')},
        'apk': {'nombre': os.path.basename(APK), 'bytes': os.path.getsize(APK)},
        'descarga': {'min': minimo, 'max': maximo},
    }
    destino = os.path.join(RAIZ, 'play', 'consola', 'datos.js')
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, 'w', encoding='utf-8') as f:
        f.write('window.DATOS = ' + json.dumps(datos, ensure_ascii=False, indent=2) + ';\n')
    print(json.dumps(datos, ensure_ascii=False, indent=2))
