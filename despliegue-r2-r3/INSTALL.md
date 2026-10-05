# Instalación de Agenda Académica (entorno local en Windows)

Estas instrucciones reproducen el entorno usado en los Retos 2 y 3: PostgreSQL, Flask servido por
Waitress, Nginx como servidor web con HTTPS y el dominio local `agenda.local`.

## Versiones instaladas

| Componente | Versión | Función |
|---|---|---|
| Windows | 11 Pro (64 bits) | Sistema operativo |
| Python | 3.14.3 | Lenguaje de la aplicación |
| Flask | 3.1.3 | *Framework* principal |
| Waitress | 3.0.2 | Servidor WSGI de producción |
| Flask-WTF | 1.3.0 | *Plugin*: protección CSRF de formularios |
| Psycopg (binary) | 3.3.6 | Conector de PostgreSQL |
| PostgreSQL | 17.11 (binarios ZIP para Windows) | Base de datos |
| Nginx | 1.30.5 para Windows | Servidor web y proxy inverso |
| Playwright | 1.63.0 | Pruebas funcionales en Chrome y Edge (solo desarrollo) |
| Node.js | 24.18.0 | Ejecuta Lighthouse (solo desarrollo) |
| Lighthouse | 13.5.0 | Pruebas de rendimiento (solo desarrollo) |

## 1. Obtener el proyecto

```powershell
git clone https://github.com/Missin03/Mi-proyecto-UVEG.git
cd Mi-proyecto-UVEG\despliegue-r2-r3
```

## 2. Entorno virtual y dependencias

```powershell
py -3.14 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt   # solo para pruebas
```

## 3. PostgreSQL y Nginx

1. Descarga los binarios ZIP de PostgreSQL 17 para Windows y extráelos en
   `..\..\.local\postgres\` (debe quedar `..\..\.local\postgres\pgsql\bin\pg_ctl.exe`).
2. Descarga Nginx 1.30 para Windows y extráelo en `..\..\.local\nginx\` (queda
   `..\..\.local\nginx\nginx-1.30.5\nginx.exe`).
3. Si los instalaste en otra ubicación, define las variables `AGENDA_LOCAL`, `PG_BIN` y `NGINX_DIR`.

La primera vez, `scripts/entorno.py` crea el clúster con `initdb`, la base `agenda_academica`,
ejecuta `db/init.sql` (tablas, llaves foráneas, índices y datos de ejemplo) y crea el usuario
`agenda_app` con permisos mínimos. Las contraseñas aleatorias se guardan en
`..\..\.local\entorno.json`, fuera del repositorio.

## 4. Dominio local

Abre el Bloc de notas **como administrador**, edita `C:\Windows\System32\drivers\etc\hosts` y
agrega:

```
127.0.0.1   agenda.local
```

Comprueba con `ping agenda.local` que responda `127.0.0.1`.

## 5. Iniciar la aplicación

```powershell
.venv\Scripts\python.exe scripts\entorno.py iniciar --modo https
```

El script genera el certificado autofirmado (`scripts/generar_certificado.py`) si no existe,
construye `nginx.conf` a partir de `deploy/nginx/agenda.conf`, valida la configuración con
`nginx -t` y levanta los tres servicios:

| Servicio | Dirección |
|---|---|
| PostgreSQL | `127.0.0.1:55432` |
| Flask + Waitress | `127.0.0.1:5055` (solo accesible desde Nginx) |
| Nginx HTTP | `http://agenda.local` → redirección 301 a HTTPS |
| Nginx HTTPS | `https://agenda.local/agenda/` |

El certificado es autofirmado: el navegador mostrará una advertencia hasta que importes
`..\..\.local\certificados\ca-local.crt` en *Entidades de certificación raíz de confianza* (opcional).

Para el modo del Reto 2 (solo HTTP en `http://localhost/agenda/`) usa `--modo http`.
Para detener todo: `.venv\Scripts\python.exe scripts\entorno.py detener`.

## 6. Pruebas

```powershell
# Funcionales en Google Chrome y Microsoft Edge (deben estar instalados)
.venv\Scripts\python.exe tests\test_navegadores.py

# Rendimiento con Lighthouse
npx lighthouse@13.5.0 https://agenda.local/agenda/ --chrome-flags="--headless=new --ignore-certificate-errors" --output html --output json --output-path evidencias\lighthouse\agenda
```

## 7. Empaquetar para el servidor

```powershell
.venv\Scripts\python.exe scripts\optimizar.py
.venv\Scripts\python.exe scripts\empaquetar.py
```
