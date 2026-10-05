"""Genera el paquete comprimido listo para copiar al servidor.

Uso: python scripts/empaquetar.py
Crea dist/agenda-academica-<versión>.zip con solo los archivos de producción
(sin fuentes sin optimizar, pruebas ni entornos virtuales) y su hash SHA-256.
"""
import hashlib
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VERSION = '1.0.0'
INCLUIR = [
    'app.py', 'requirements.txt', 'INSTALL.md', 'README.md',
    'db/init.sql',
    'deploy/nginx/agenda.conf',
    'static/css/app.min.css', 'static/js/app.min.js', 'static/img/icono.png',
    'templates/base.html', 'templates/index.html', 'templates/create.html',
    'templates/legal.html', 'templates/error.html',
]


def main():
    dist = RAIZ / 'dist'
    dist.mkdir(exist_ok=True)
    paquete = dist / f'agenda-academica-{VERSION}.zip'
    carpeta = f'agenda-academica-{VERSION}'
    with zipfile.ZipFile(paquete, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for ruta in INCLUIR:
            archivo = RAIZ / ruta
            if not archivo.exists():
                raise SystemExit(f'Falta {ruta}; ejecuta primero scripts/optimizar.py')
            zf.write(archivo, f'{carpeta}/{ruta}')
    with zipfile.ZipFile(paquete) as zf:
        if zf.testzip() is not None:
            raise SystemExit('El paquete está dañado')
        for info in zf.infolist():
            print(f'{info.file_size:>8} B  {info.filename}')
    digest = hashlib.sha256(paquete.read_bytes()).hexdigest()
    (dist / f'{paquete.name}.sha256').write_text(f'{digest}  {paquete.name}\n', encoding='utf-8')
    print(f'\nPaquete: {paquete.name} ({paquete.stat().st_size} B)\nSHA-256: {digest}')


if __name__ == '__main__':
    main()
