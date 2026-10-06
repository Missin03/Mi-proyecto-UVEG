"""Graba la vista previa de la app (App Preview) para App Store Connect.

Se graba con WebKit a 886 x 1920 (tamaño de vista previa para iPhone de 6.9") y se convierte a MP4
H.264 a 30 fps con pista de audio estéreo silenciosa, de entre 15 y 30 segundos.
"""
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

from recursos_ios import DATOS, RAIZ

SALIDA = RAIZ / 'appstore'
TEMP = SALIDA / '_video'

with sync_playwright() as p:
    navegador = p.webkit.launch()
    contexto = navegador.new_context(viewport={'width': 443, 'height': 960}, device_scale_factor=2,
                                     is_mobile=True, has_touch=True, locale='es-MX',
                                     record_video_dir=str(TEMP), record_video_size={'width': 886, 'height': 1920})
    pagina = contexto.new_page()
    pagina.add_init_script(f"localStorage.setItem('agenda.tareas.v1', {json.dumps(DATOS)})")
    pagina.goto((RAIZ / 'www' / 'index.html').as_uri())
    pausa = pagina.wait_for_timeout
    pausa(2500)
    pagina.click('[data-filtro="pendiente"]'); pausa(1500)
    pagina.click('[data-filtro=""]'); pausa(1000)
    pagina.click('li:first-child .avanzar'); pausa(1500)
    pagina.click('#nueva'); pausa(800)
    pagina.type('#f-materia', 'Redes de computadoras', delay=60)
    pagina.type('#f-titulo', 'Práctica de subredes', delay=60)
    pagina.fill('#f-fecha', '2026-10-12'); pausa(500)
    pagina.click('#guardar'); pausa(2000)
    pagina.evaluate('window.scrollBy({top: 500, behavior: "smooth"})'); pausa(1500)
    pagina.click('#abrir-menu'); pausa(1000)
    pagina.click('[data-legal="privacidad"]'); pausa(2500)
    ruta_webm = pagina.video.path()
    contexto.close()
    navegador.close()

mp4 = SALIDA / 'vista-previa-iphone-69.mp4'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-i', str(ruta_webm),
                '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-t', '22', '-vf', 'fps=30,scale=886:1920', '-c:v', 'libx264', '-profile:v', 'high',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', '-movflags', '+faststart', str(mp4)], check=True)
for f in TEMP.glob('*'):
    f.unlink()
TEMP.rmdir()
print(mp4, mp4.stat().st_size, 'bytes')
