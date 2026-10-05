"""Agenda Académica: aplicación local de práctica para despliegue web."""
import os
from datetime import date
from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
import psycopg
from psycopg.rows import dict_row

app = Flask(__name__)
# Nginx publica la aplicación en /agenda y envía el prefijo, el host y el esquema originales.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.config.update(SECRET_KEY=os.environ['APP_SECRET'], MAX_CONTENT_LENGTH=32768,
                  SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                  SESSION_COOKIE_SECURE=os.environ.get('SECURE_COOKIES') == '1')
CSRFProtect(app)
STATES = ('Pendiente', 'En curso', 'Completada')

def db():
    return psycopg.connect(os.environ['DATABASE_URL'], row_factory=dict_row)

@app.get('/')
def index():
    status = request.args.get('estado', '')
    text = request.args.get('buscar', '').strip()[:100]
    if status and status not in STATES:
        abort(400)
    with db() as conn:
        rows = conn.execute('''SELECT t.*, m.nombre AS materia FROM tareas t
            JOIN materias m ON m.id=t.materia_id
            WHERE (%s='' OR t.estado=%s) AND (%s='' OR t.titulo ILIKE %s)
            ORDER BY t.fecha_entrega, t.id''', (status, status, text, '%'+text+'%')).fetchall()
        totals = conn.execute('SELECT estado, count(*) AS cantidad FROM tareas GROUP BY estado').fetchall()
    counts = {s: 0 for s in STATES}
    counts.update({r['estado']: r['cantidad'] for r in totals})
    return render_template('index.html', tasks=rows, counts=counts, states=STATES,
                           status=status, text=text)

@app.route('/tareas/nueva', methods=['GET', 'POST'])
def create():
    with db() as conn:
        subjects = conn.execute('SELECT id,nombre FROM materias ORDER BY nombre').fetchall()
        if request.method == 'POST':
            title = request.form.get('titulo', '').strip()
            desc = request.form.get('descripcion', '').strip()
            subject = request.form.get('materia_id', '')
            due = request.form.get('fecha_entrega', '')
            valid = len(title) >= 3 and len(title) <= 100 and len(desc) <= 600
            valid = valid and subject.isdigit() and int(subject) in [s['id'] for s in subjects]
            try:
                date.fromisoformat(due)
            except ValueError:
                valid = False
            if not valid:
                return render_template('create.html', subjects=subjects,
                    error='Revisa el título, la materia y la fecha de entrega.'), 400
            conn.execute('INSERT INTO tareas(titulo,descripcion,materia_id,fecha_entrega) VALUES(%s,%s,%s,%s)',
                         (title, desc, int(subject), due))
            flash('La tarea se guardó correctamente.')
            return redirect(url_for('index'))
    return render_template('create.html', subjects=subjects, error='')

@app.post('/tareas/<int:task_id>/estado')
def update(task_id):
    status = request.form.get('estado')
    if status not in STATES:
        abort(400)
    with db() as conn:
        row = conn.execute('UPDATE tareas SET estado=%s WHERE id=%s RETURNING id', (status, task_id)).fetchone()
        if not row:
            abort(404)
    flash('El estado se actualizó correctamente.')
    return redirect(url_for('index'))

@app.get('/privacidad')
def privacy():
    return render_template('legal.html', kind='privacidad')

@app.get('/terminos')
def terms():
    return render_template('legal.html', kind='terminos')

@app.get('/salud')
def health():
    with db() as conn:
        version = conn.execute('SELECT version() AS version').fetchone()['version']
        amount = conn.execute('SELECT count(*) AS total FROM tareas').fetchone()['total']
    return jsonify(estado='operativo', motor=version.split(',')[0], tareas=amount, framework='Flask')

@app.errorhandler(400)
def bad_request(error):
    return render_template('error.html', title='Solicitud no válida', detail='Revisa los datos y vuelve a intentar.'), 400

@app.errorhandler(404)
def missing(error):
    return render_template('error.html', title='Página no encontrada', detail='Puedes regresar a tus tareas.'), 404

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='127.0.0.1', port=int(os.environ.get('APP_PORT', '5055')))
