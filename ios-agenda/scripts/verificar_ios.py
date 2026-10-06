"""Revisa el proyecto de Xcode y los materiales de App Store Connect antes de archivar en macOS.

También escribe appstore/connect/datos.js con los valores reales que usa la consola simulada.
Uso: python scripts/verificar_ios.py
"""
import json
import plistlib
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
APP = RAIZ / 'ios' / 'App'
STORE = RAIZ / 'appstore'
sys.stdout.reconfigure(encoding='utf-8')
fallos = 0


def revisar(nombre, ok, detalle):
    global fallos
    fallos += not ok
    print(f"  {'OK ' if ok else 'ERR'}  {nombre:<44} {detalle}")


def titulo(t):
    print(f'\n== {t} ==')


pbx = (APP / 'App.xcodeproj' / 'project.pbxproj').read_text(encoding='utf-8')
ajuste = lambda clave: sorted(set(re.findall(rf'{clave} = "?([^";]+)"?;', pbx)))
info = plistlib.loads((APP / 'App' / 'Info.plist').read_bytes())
privacidad = plistlib.loads((APP / 'App' / 'PrivacyInfo.xcprivacy').read_bytes())
exportar = plistlib.loads((APP / 'ExportOptions.plist').read_bytes())
config = json.loads((RAIZ / 'capacitor.config.json').read_text(encoding='utf-8'))

titulo('Proyecto de Xcode (ios/App/App.xcodeproj)')
bundle = ajuste('PRODUCT_BUNDLE_IDENTIFIER')
revisar('Bundle Identifier único', bundle == [config['appId']], ', '.join(bundle))
version, build = ajuste('MARKETING_VERSION'), ajuste('CURRENT_PROJECT_VERSION')
revisar('Versión y build', len(version) == 1 and len(build) == 1, f'{version[0]} ({build[0]})')
minimo = ajuste('IPHONEOS_DEPLOYMENT_TARGET')
revisar('Versión mínima de iOS', minimo == ['15.0'], 'iOS ' + ', '.join(minimo))
revisar('Firma automática (perfil administrado por Xcode)', ajuste('CODE_SIGN_STYLE') == ['Automatic'], ', '.join(ajuste('CODE_SIGN_STYLE')))
revisar('Dispositivos', ajuste('TARGETED_DEVICE_FAMILY') == ['1,2'], 'iPhone y iPad')
revisar('Manifiesto de privacidad en el target', pbx.count('PrivacyInfo.xcprivacy in Resources') == 2, 'PrivacyInfo.xcprivacy')

titulo('Info.plist y cumplimiento')
revisar('Nombre visible', info['CFBundleDisplayName'] == config['appName'], info['CFBundleDisplayName'])
revisar('Región de desarrollo', info['CFBundleDevelopmentRegion'] == 'es-419', info['CFBundleDevelopmentRegion'])
revisar('Exportación: sin cifrado no exento', info.get('ITSAppUsesNonExemptEncryption') is False, 'ITSAppUsesNonExemptEncryption = NO')
permisos = [k for k in info if k.endswith('UsageDescription')]
revisar('Permisos sensibles solicitados', not permisos, 'ninguno' if not permisos else ', '.join(permisos))
revisar('Rastreo (App Tracking Transparency)', privacidad['NSPrivacyTracking'] is False, 'NSPrivacyTracking = NO')
revisar('Datos recopilados declarados', privacidad['NSPrivacyCollectedDataTypes'] == [], 'ninguno')
revisar('Exportación del .ipa', exportar['method'] == 'app-store-connect', f"method = {exportar['method']}, signing = {exportar['signingStyle']}")

titulo('Recursos gráficos')
icono = Image.open(APP / 'App' / 'Assets.xcassets' / 'AppIcon.appiconset' / 'AppIcon-512@2x.png')
revisar('Icono de la app 1024 x 1024 sin transparencia', icono.size == (1024, 1024) and icono.mode == 'RGB', f'{icono.size[0]} x {icono.size[1]} {icono.mode}')
medidas = {'iphone-69': (1320, 2868), 'ipad-13': (2064, 2752)}
capturas = {}
for clave, tam in medidas.items():
    archivos = sorted((STORE / 'capturas').glob(f'{clave}-*.png'))
    capturas[clave] = [f.name for f in archivos]
    ok = archivos and all(Image.open(f).size == tam for f in archivos)
    revisar(f'Capturas {clave} ({tam[0]} x {tam[1]})', bool(ok), f'{len(archivos)} archivos')
video = STORE / 'vista-previa-iphone-69.mp4'
datos_video = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-i', str(video)],
                             capture_output=True, text=True).stderr
duracion = re.search(r'Duration: 00:00:(\d+\.\d+)', datos_video)
segundos = float(duracion.group(1)) if duracion else 0
revisar('Vista previa en video (15 a 30 s, H.264)', 15 <= segundos <= 30 and 'h264' in datos_video and '886x1920' in datos_video,
        f'{segundos:.1f} s, 886 x 1920')

datos = {
    'bundleId': bundle[0], 'version': version[0], 'build': build[0], 'iosMinimo': minimo[0],
    'nombre': config['appName'], 'capturas': capturas, 'video': {'archivo': video.name, 'segundos': round(segundos, 1)},
    'cifrado': info.get('ITSAppUsesNonExemptEncryption'), 'rastreo': privacidad['NSPrivacyTracking'],
}
destino = STORE / 'connect' / 'datos.js'
destino.parent.mkdir(parents=True, exist_ok=True)
destino.write_text('window.DATOS = ' + json.dumps(datos, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
print(f'\n{"Todo listo para archivar en Xcode." if not fallos else f"{fallos} revisiones fallaron."}')
sys.exit(1 if fallos else 0)
