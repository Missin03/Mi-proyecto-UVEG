"""Inicia o detiene el entorno local: PostgreSQL, aplicación Flask (Waitress) y Nginx.

Uso:
    python scripts/entorno.py iniciar --modo http    # Reto 2: http://localhost/agenda/
    python scripts/entorno.py iniciar --modo https   # Reto 3: https://agenda.local/agenda/
    python scripts/entorno.py detener
    python scripts/entorno.py estado

Rutas configurables con variables de entorno (ver INSTALL.md):
    AGENDA_LOCAL  carpeta de trabajo con datos, logs y certificados (por defecto ../../.local)
    PG_BIN        carpeta bin de PostgreSQL           (por defecto AGENDA_LOCAL/postgres/pgsql/bin)
    NGINX_DIR     carpeta de Nginx para Windows        (por defecto AGENDA_LOCAL/nginx/nginx-*)
"""
import argparse
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

APP = Path(__file__).resolve().parent.parent
LOCAL = Path(os.environ.get('AGENDA_LOCAL', APP.parent.parent / '.local')).resolve()
PG_BIN = Path(os.environ.get('PG_BIN', LOCAL / 'postgres/pgsql/bin'))
NGINX = Path(os.environ['NGINX_DIR']) if 'NGINX_DIR' in os.environ else next((LOCAL / 'nginx').glob('nginx-*'))
PGDATA = LOCAL / 'pgdata'
LOGS = LOCAL / 'logs'
PUERTO_PG = '55432'
SEGUNDO_PLANO = 0x00000008 | 0x00000200 | 0x08000000  # DETACHED | NEW_PROCESS_GROUP | NO_WINDOW


def ejecutar(args, **kwargs):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, **kwargs)
    if r.returncode:
        raise SystemExit(f'Error en {Path(str(args[0])).name}: {r.stderr.strip() or r.stdout.strip()}')
    return r.stdout.strip()


def credenciales():
    archivo = LOCAL / 'entorno.json'
    if not archivo.exists():
        archivo.write_text(json.dumps({'admin_password': secrets.token_urlsafe(28),
                                       'app_password': secrets.token_urlsafe(28),
                                       'app_secret': secrets.token_urlsafe(40)}))
    return json.loads(archivo.read_text())


def psql(cred, base, *extra):
    env = dict(os.environ, PGPASSWORD=cred['admin_password'])
    return ejecutar([PG_BIN / 'psql.exe', '-h', '127.0.0.1', '-p', PUERTO_PG, '-U', 'agenda_admin',
                     '-d', base, '-v', 'ON_ERROR_STOP=1', *extra], env=env)


def iniciar_postgres(cred):
    if not (PGDATA / 'PG_VERSION').exists():
        clave = LOCAL / 'admin.pw'
        clave.write_text(cred['admin_password'])
        ejecutar([PG_BIN / 'initdb.exe', '-D', PGDATA, '-U', 'agenda_admin', '--pwfile', clave,
                  '--auth=scram-sha-256', '-E', 'UTF8', '--locale=C'])
        clave.unlink()
    estado = subprocess.run([str(PG_BIN / 'pg_ctl.exe'), 'status', '-D', str(PGDATA)], capture_output=True)
    if estado.returncode:
        # Sin capturar la salida: el servidor hereda los descriptores y la captura nunca terminaría.
        inicio = subprocess.run([str(PG_BIN / 'pg_ctl.exe'), '-D', str(PGDATA), '-l', str(LOGS / 'postgres.log'),
                                 '-o', f'-p {PUERTO_PG} -h 127.0.0.1', '-w', 'start'],
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if inicio.returncode:
            raise SystemExit('PostgreSQL no inició; revisa logs/postgres.log')
    if '1' not in psql(cred, 'postgres', '-tAc', "SELECT 1 FROM pg_database WHERE datname='agenda_academica'"):
        psql(cred, 'postgres', '-c', 'CREATE DATABASE agenda_academica')
    psql(cred, 'agenda_academica', '-q', '-f', APP / 'db/init.sql')
    # Usuario de la aplicación con privilegios mínimos: no puede crear ni borrar tablas.
    psql(cred, 'agenda_academica', '-q', '-c', (
        "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='agenda_app') "
        "THEN CREATE ROLE agenda_app LOGIN; END IF; END $$;"
        f"ALTER ROLE agenda_app PASSWORD '{cred['app_password']}';"
        "GRANT CONNECT ON DATABASE agenda_academica TO agenda_app;"
        "GRANT USAGE ON SCHEMA public TO agenda_app;"
        "GRANT SELECT ON materias TO agenda_app;"
        "GRANT SELECT, INSERT, UPDATE ON tareas TO agenda_app;"
        "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO agenda_app;"))
    print(f'PostgreSQL activo en 127.0.0.1:{PUERTO_PG}, base agenda_academica')


def iniciar_app(cred, modo):
    try:
        urlopen('http://127.0.0.1:5055/salud', timeout=1)
        print('La aplicación ya estaba activa en 127.0.0.1:5055')
        return
    except OSError:
        pass
    env = dict(os.environ, APP_SECRET=cred['app_secret'], SECURE_COOKIES='1' if modo == 'https' else '0',
               DATABASE_URL=f"postgresql://agenda_app:{cred['app_password']}@127.0.0.1:{PUERTO_PG}/agenda_academica")
    log = (LOGS / 'app.log').open('a')
    proceso = subprocess.Popen([sys.executable, str(APP / 'app.py')], env=env, cwd=APP, stdout=log,
                               stderr=subprocess.STDOUT, creationflags=SEGUNDO_PLANO)
    (LOCAL / 'app.pid').write_text(str(proceso.pid))
    for _ in range(20):
        try:
            urlopen('http://127.0.0.1:5055/salud', timeout=1)
            print('Aplicación Flask (Waitress) activa en 127.0.0.1:5055')
            return
        except OSError:
            time.sleep(0.5)
    raise SystemExit('La aplicación no respondió; revisa logs/app.log')


def iniciar_nginx(modo):
    plantilla = APP / 'deploy/nginx' / ('agenda.conf' if modo == 'https' else 'agenda-http.conf')
    if modo == 'https' and not (LOCAL / 'certificados/agenda.crt').exists():
        ejecutar([sys.executable, APP / 'scripts/generar_certificado.py', LOCAL / 'certificados'])
    rutas = {'__APP__': APP, '__LOCAL__': LOCAL, '__NGINX__': NGINX}
    texto = plantilla.read_text(encoding='utf-8')
    for marca, ruta in rutas.items():
        texto = texto.replace(marca, ruta.as_posix())
    conf = LOCAL / 'nginx.conf'
    conf.write_text(texto, encoding='utf-8')
    detener_nginx()
    ejecutar([NGINX / 'nginx.exe', '-t', '-p', f'{NGINX}/', '-c', conf])
    subprocess.Popen([str(NGINX / 'nginx.exe'), '-p', f'{NGINX}/', '-c', str(conf)], cwd=NGINX,
                     creationflags=SEGUNDO_PLANO)
    time.sleep(1)
    destino = 'https://agenda.local/agenda/' if modo == 'https' else 'http://localhost/agenda/'
    print(f'Nginx activo ({plantilla.name}). Abre {destino}')


def detener_nginx():
    if (LOCAL / 'nginx.pid').exists():
        subprocess.run([str(NGINX / 'nginx.exe'), '-s', 'quit', '-p', f'{NGINX}/', '-c', str(LOCAL / 'nginx.conf')],
                       capture_output=True)
        time.sleep(1)


def detener():
    detener_nginx()
    pid = LOCAL / 'app.pid'
    if pid.exists():
        subprocess.run(['taskkill', '/PID', pid.read_text().strip(), '/T', '/F'], capture_output=True)
        pid.unlink()
    subprocess.run([str(PG_BIN / 'pg_ctl.exe'), 'stop', '-D', str(PGDATA), '-m', 'fast', '-w'], capture_output=True)
    print('Entorno detenido')


def estado():
    for nombre, url in (('Aplicación', 'http://127.0.0.1:5055/salud'),):
        try:
            print(nombre, urlopen(url, timeout=2).read().decode())
        except OSError as error:
            print(nombre, 'sin respuesta:', error)
    print(subprocess.run([str(PG_BIN / 'pg_ctl.exe'), 'status', '-D', str(PGDATA)],
                         capture_output=True, text=True).stdout.strip())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('accion', choices=['iniciar', 'detener', 'estado'])
    parser.add_argument('--modo', choices=['http', 'https'], default='https')
    args = parser.parse_args()
    LOGS.mkdir(parents=True, exist_ok=True)
    if args.accion == 'iniciar':
        datos = credenciales()
        iniciar_postgres(datos)
        iniciar_app(datos, args.modo)
        iniciar_nginx(args.modo)
    elif args.accion == 'detener':
        detener()
    else:
        estado()
