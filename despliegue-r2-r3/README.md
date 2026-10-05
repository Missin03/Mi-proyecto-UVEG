# Agenda Académica

Aplicación web para organizar tareas escolares por materia, fecha de entrega y avance
(*Pendiente*, *En curso*, *Completada*). Se desarrolló como práctica de los Retos 2 y 3 del
módulo **Despliegue de aplicaciones web y móviles v2** (UVEG) para empaquetarla, versionarla y
desplegarla con **Nginx** en un entorno local de simulación.

- **Autor:** Emmanuel Missin Garcia Vargas
- **Versión:** 1.0.0
- **Tecnologías:** Python 3.14, Flask 3.1, Waitress 3.0, Flask-WTF 1.3, PostgreSQL 17, Nginx 1.30

## Estructura del proyecto

```
despliegue-r2-r3/
├── app.py                  # Aplicación Flask (rutas, validaciones, consultas)
├── requirements.txt        # Dependencias con versión fija
├── db/init.sql             # Script de inicialización de PostgreSQL
├── templates/              # Vistas HTML (Jinja2)
├── static/
│   ├── css/                # app.css (fuente) y app.min.css (minificado)
│   ├── js/                 # app.js (fuente) y app.min.js (minificado)
│   └── img/                # icono.png optimizado para la web
├── src/img/                # Imagen original sin optimizar
├── deploy/nginx/           # Server Blocks de Nginx (HTTP y HTTPS)
├── scripts/                # Optimización, empaquetado, certificado y entorno local
├── tests/                  # Pruebas funcionales en Chrome y Edge
└── evidencias/             # Resultados de optimización, pruebas y rendimiento
```

## 1. Preparación y optimización

`scripts/optimizar.py` minifica CSS y JS (elimina comentarios y espacios) y redimensiona el
icono de 256 px a 64 px con paleta reducida. La interfaz solo carga los archivos `.min`.

```powershell
.venv\Scripts\python.exe scripts\optimizar.py
```

| Archivo | Original | Optimizado | Reducción |
|---|---:|---:|---:|
| css/app.css | 4,366 B | 3,745 B | 14.2 % |
| js/app.js | 216 B | 134 B | 38.0 % |
| img/icono.png | 196,993 B | 606 B | 99.7 % |

## 2. Empaquetado

`scripts/empaquetar.py` genera `dist/agenda-academica-1.0.0.zip` únicamente con los archivos de
producción (aplicación, plantillas, estáticos optimizados, script SQL y configuración de Nginx),
comprueba la integridad del ZIP y calcula su SHA-256. Las fuentes sin optimizar, las pruebas y el
entorno virtual no se incluyen.

```powershell
.venv\Scripts\python.exe scripts\empaquetar.py
```

## 3. Versionamiento

El proyecto se versiona en GitHub con un *commit* por cada cambio: estructura base, optimización,
Server Block, empaquetado, documentación, base de datos, HTTPS y pruebas. `.gitignore` excluye el
entorno virtual, el paquete generado, los registros y las llaves privadas.

```powershell
git log --oneline -- despliegue-r2-r3
```

## 4. Servidor web: Nginx (Server Block)

`deploy/nginx/agenda-http.conf` (Reto 2) publica la aplicación en una ruta simulada:

| Elemento | Configuración |
|---|---|
| Ruta simulada | `http://localhost/agenda/` |
| Puerto | `127.0.0.1:80` (Nginx) → `127.0.0.1:5055` (Waitress) |
| Mapeo de directorios | `/agenda/static/` → `static/` del proyecto, con caché de 7 días |
| Proxy | `/agenda/` → aplicación Flask con `X-Forwarded-Prefix: /agenda` |

`deploy/nginx/agenda.conf` (Reto 3) agrega el dominio local `agenda.local`, HTTPS con certificado
propio, redirección obligatoria de HTTP a HTTPS y encabezados de seguridad (CSP, HSTS, etc.).

```powershell
.venv\Scripts\python.exe scripts\entorno.py iniciar --modo http    # Reto 2
.venv\Scripts\python.exe scripts\entorno.py iniciar --modo https   # Reto 3
.venv\Scripts\python.exe scripts\entorno.py detener
```

La instalación completa paso a paso está en [INSTALL.md](INSTALL.md).

## Documentos legales

La aplicación muestra en el pie de página el **Aviso de privacidad** (`/agenda/privacidad`) y los
**Términos de uso** (`/agenda/terminos`).
