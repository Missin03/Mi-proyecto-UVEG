"""Pruebas funcionales de Agenda Académica en Google Chrome y Microsoft Edge.

Uso: python tests/test_navegadores.py [url_base]
Por defecto prueba https://agenda.local/agenda/ con los navegadores instalados en el equipo
(Playwright con channel='chrome' y channel='msedge'). Guarda capturas y un resumen en
evidencias/pruebas/.
"""
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
BASE = (sys.argv[1] if len(sys.argv) > 1 else 'https://agenda.local/agenda/').rstrip('/') + '/'
SALIDA = RAIZ / 'evidencias/pruebas'
NAVEGADORES = {'chrome': 'Google Chrome', 'msedge': 'Microsoft Edge'}


def probar(p, canal):
    carpeta = SALIDA / canal
    carpeta.mkdir(parents=True, exist_ok=True)
    navegador = p.chromium.launch(channel=canal)
    # El certificado es autofirmado por una CA local que el navegador de pruebas no conoce.
    pagina = navegador.new_page(ignore_https_errors=True, viewport={'width': 1280, 'height': 900})
    errores_consola = []
    pagina.on('console', lambda m: errores_consola.append(m.text) if m.type == 'error' else None)
    resultados = []

    def caso(nombre, funcion):
        inicio = time.perf_counter()
        try:
            detalle = funcion() or ''
            estado = 'OK'
        except Exception as error:  # se registra la falla y se continúa con los demás casos
            detalle, estado = str(error).splitlines()[0], 'FALLA'
        resultados.append({'caso': nombre, 'resultado': estado, 'detalle': detalle,
                           'ms': round((time.perf_counter() - inicio) * 1000)})
        pagina.screenshot(path=carpeta / f'{len(resultados):02d}.png')

    def redireccion():
        http = BASE.replace('https://', 'http://')
        pagina.goto(http)
        assert pagina.url.startswith('https://'), f'no redirigió: {pagina.url}'
        return f'{http} -> {pagina.url}'

    def inicio_y_encabezados():
        respuesta = pagina.goto(BASE)
        expect(pagina).to_have_title('Agenda Académica')
        expect(pagina.locator('.stat')).to_have_count(3)
        h = respuesta.headers
        for encabezado in ('content-security-policy', 'strict-transport-security', 'x-content-type-options'):
            assert encabezado in h, f'falta {encabezado}'
        return f"HSTS: {h['strict-transport-security']}"

    titulo = f'Prueba en {NAVEGADORES[canal]} {time.strftime("%H%M%S")}'

    def crear_tarea():
        pagina.get_by_role('link', name='Nueva tarea').click()
        pagina.get_by_label('Título').fill(titulo)
        pagina.get_by_label('Descripción opcional').fill('Registro creado por la prueba automatizada')
        pagina.get_by_label('Materia').select_option(label='Despliegue de aplicaciones web y móviles')
        pagina.get_by_label('Fecha de entrega').fill((date.today() + timedelta(days=7)).isoformat())
        pagina.get_by_role('button', name='Guardar tarea').click()
        expect(pagina.get_by_role('status')).to_have_text('La tarea se guardó correctamente.')
        expect(pagina.get_by_role('heading', name=titulo)).to_be_visible()
        return titulo

    def cambiar_estado():
        tarea = pagina.locator('article.task', has=pagina.get_by_role('heading', name=titulo))
        tarea.get_by_role('combobox').select_option('Completada')
        tarea.get_by_role('button', name='Guardar avance').click()
        expect(pagina.get_by_role('status')).to_have_text('El estado se actualizó correctamente.')
        return 'Pendiente -> Completada'

    def filtrar():
        pagina.get_by_label('Buscar por título').fill(titulo)
        pagina.get_by_label('Estado').select_option('Completada')
        pagina.get_by_role('button', name='Aplicar filtros').click()
        expect(pagina.locator('article.task')).to_have_count(1)
        return '1 resultado'

    def validacion():
        pagina.goto(BASE + 'tareas/nueva')
        # Se quitan las validaciones del navegador para comprobar las del servidor.
        pagina.evaluate("document.querySelectorAll('[required],[minlength]').forEach(e => "
                        "{e.removeAttribute('required'); e.removeAttribute('minlength');})")
        pagina.get_by_label('Título').fill('ab')
        pagina.get_by_role('button', name='Guardar tarea').click()
        expect(pagina.get_by_role('alert')).to_contain_text('Revisa el título')
        # El 400 de este caso es la respuesta esperada; no cuenta como error de consola.
        errores_consola[:] = [e for e in errores_consola if 'status of 400' not in e]
        return 'El servidor rechaza un título de 2 caracteres (HTTP 400)'

    def documentos_legales():
        pagina.goto(BASE)
        pagina.get_by_role('link', name='Términos de uso').click()
        expect(pagina.get_by_role('heading', level=1)).to_have_text('Términos de uso')
        pagina.get_by_role('link', name='Aviso de privacidad').click()
        expect(pagina.get_by_role('heading', level=1)).to_have_text('Aviso de privacidad')
        return 'Enlaces visibles en el pie de página'

    def sin_errores():
        assert not errores_consola, errores_consola[0]
        return 'Sin errores ni bloqueos de CSP en consola'

    caso('Redirección HTTP a HTTPS', redireccion)
    caso('Carga inicial y encabezados de seguridad', inicio_y_encabezados)
    caso('Registrar una tarea', crear_tarea)
    caso('Actualizar el avance', cambiar_estado)
    caso('Buscar y filtrar', filtrar)
    caso('Validación en el servidor', validacion)
    caso('Aviso de privacidad y términos', documentos_legales)
    caso('Consola sin errores', sin_errores)
    version = navegador.version
    navegador.close()
    return {'navegador': NAVEGADORES[canal], 'version': version, 'casos': resultados}


def main():
    with sync_playwright() as p:
        reporte = [probar(p, canal) for canal in NAVEGADORES]
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / 'resultados.json').write_text(json.dumps({'url': BASE, 'fecha': time.strftime('%Y-%m-%d %H:%M'),
                                                        'navegadores': reporte}, indent=2, ensure_ascii=False),
                                            encoding='utf-8')
    fallas = 0
    for r in reporte:
        print(f"\n{r['navegador']} {r['version']}  ({BASE})")
        for c in r['casos']:
            fallas += c['resultado'] != 'OK'
            print(f"  [{c['resultado']:<5}] {c['caso']:<42} {c['ms']:>5} ms  {c['detalle']}")
    total = sum(len(r['casos']) for r in reporte)
    print(f'\nResultado: {total - fallas}/{total} casos correctos')
    sys.exit(1 if fallas else 0)


if __name__ == '__main__':
    main()
