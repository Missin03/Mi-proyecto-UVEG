// Agenda Académica (iOS con Capacitor). Las tareas se guardan en el almacenamiento local del WebView.
const CLAVE = 'agenda.tareas.v1';
const ESTADOS = { pendiente: 'Pendiente', en_curso: 'En curso', completada: 'Completada' };
const SIGUIENTE = { pendiente: 'en_curso', en_curso: 'completada', completada: 'pendiente' };
const $ = (id) => document.getElementById(id);
let filtro = '';

function leer() {
  try { return JSON.parse(localStorage.getItem(CLAVE)) || []; } catch { return []; }
}
function guardar(tareas) { localStorage.setItem(CLAVE, JSON.stringify(tareas)); }

function fechaLegible(iso) {
  const [a, m, d] = iso.split('-').map(Number);
  return new Date(a, m - 1, d).toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' });
}

function mostrar() {
  const tareas = leer();
  for (const e of Object.keys(ESTADOS)) $('n-' + e).textContent = tareas.filter((t) => t.estado === e).length;
  const visibles = tareas
    .filter((t) => !filtro || t.estado === filtro)
    .sort((x, y) => (x.estado === 'completada') - (y.estado === 'completada') || x.fecha.localeCompare(y.fecha));
  $('vacio').hidden = visibles.length > 0;
  const lista = $('lista');
  lista.replaceChildren();
  for (const t of visibles) {
    const li = document.createElement('li');
    li.innerHTML = `
      <div class="fila"><span class="materia"></span><span class="estado ${t.estado}">${ESTADOS[t.estado]}</span></div>
      <h3></h3><p></p><time datetime="${t.fecha}">Entrega: ${fechaLegible(t.fecha)}</time>
      <div class="acciones">
        <button class="eliminar">Eliminar</button>
        <button class="avanzar">Marcar ${ESTADOS[SIGUIENTE[t.estado]].toLowerCase()}</button>
      </div>`;
    li.querySelector('.materia').textContent = t.materia;
    li.querySelector('h3').textContent = t.titulo;
    li.querySelector('p').textContent = t.descripcion;
    li.querySelector('p').hidden = !t.descripcion;
    li.querySelector('.eliminar').setAttribute('aria-label', `Eliminar la tarea ${t.titulo}`);
    li.querySelector('.eliminar').onclick = () => {
      if (confirm(`Se borrará «${t.titulo}» de este iPhone. ¿Continuar?`)) {
        guardar(leer().filter((x) => x.id !== t.id));
        mostrar();
      }
    };
    li.querySelector('.avanzar').onclick = () => {
      guardar(leer().map((x) => (x.id === t.id ? { ...x, estado: SIGUIENTE[x.estado] } : x)));
      mostrar();
    };
    lista.append(li);
  }
}

// Filtros
document.querySelectorAll('[data-filtro]').forEach((b) => b.addEventListener('click', () => {
  filtro = b.dataset.filtro;
  document.querySelectorAll('[data-filtro]').forEach((x) => x.setAttribute('aria-checked', String(x === b)));
  mostrar();
}));

// Formulario con validación
function error(campo, mensaje) {
  $('e-' + campo).textContent = mensaje;
  $('f-' + campo).setAttribute('aria-invalid', mensaje ? 'true' : 'false');
  return !mensaje;
}
$('nueva').onclick = () => { $('form-tarea').reset(); ['materia', 'titulo', 'fecha'].forEach((c) => error(c, '')); $('formulario').showModal(); };
$('cancelar').onclick = () => $('formulario').close();
$('form-tarea').addEventListener('submit', (ev) => {
  const t = {
    id: Date.now(),
    materia: $('f-materia').value.trim(),
    titulo: $('f-titulo').value.trim(),
    descripcion: $('f-descripcion').value.trim(),
    fecha: $('f-fecha').value,
    estado: document.querySelector('[name=estado]:checked').value,
  };
  const ok = [
    error('materia', t.materia ? '' : 'Escribe la materia.'),
    error('titulo', t.titulo.length >= 3 ? '' : 'El título debe tener al menos 3 caracteres.'),
    error('fecha', /^\d{4}-\d{2}-\d{2}$/.test(t.fecha) ? '' : 'Elige la fecha de entrega.'),
  ].every(Boolean);
  if (!ok) { ev.preventDefault(); return; }
  guardar([...leer(), t]);
  mostrar();
});

// Menú y documentos legales
const LEGAL = {
  privacidad: ['Aviso de privacidad', `
    <p><b>Responsable:</b> Emmanuel Missin Garcia Vargas, desarrollador de Agenda Académica.</p>
    <p><b>Qué datos se guardan.</b> Solo lo que escribes en cada tarea: materia, título, descripción, fecha de entrega y estado.</p>
    <p><b>Dónde se guardan.</b> En el almacenamiento local de la app dentro de este iPhone. No hay cuentas ni servidores: la información no sale del dispositivo.</p>
    <p><b>Publicidad y rastreo.</b> La app no muestra anuncios, no rastrea a los usuarios y no incluye SDK de analítica.</p>
    <p><b>Cómo borrar tus datos.</b> Elimina cada tarea desde la lista o desinstala la app para borrar todo.</p>
    <p><b>Soporte:</b> github.com/Missin03/Mi-proyecto-UVEG/issues</p>
    <p>Última actualización: 6 de octubre de 2026.</p>`],
  terminos: ['Términos de uso', `
    <p>Agenda Académica es una herramienta gratuita para organizar tareas escolares.</p>
    <p><b>Uso permitido.</b> Úsala para tus actividades. No guardes contraseñas ni datos de terceros.</p>
    <p><b>Responsabilidad.</b> La app no sustituye el calendario oficial de tu escuela; verifica tus fechas en la plataforma institucional.</p>
    <p>Última actualización: 6 de octubre de 2026.</p>`],
};
$('abrir-menu').onclick = () => $('menu').showModal();
$('cerrar-menu').onclick = () => $('menu').close();
document.querySelectorAll('[data-legal]').forEach((b) => b.addEventListener('click', () => {
  const [titulo, html] = LEGAL[b.dataset.legal];
  $('titulo-legal').textContent = titulo;
  $('texto-legal').innerHTML = html;
  $('menu').close();
  $('legal').showModal();
  $('texto-legal').focus();
}));
$('cerrar-legal').onclick = () => $('legal').close();
$('acerca').onclick = () => {
  $('menu').close();
  alert('Agenda Académica 1.0.0\n\nApp para organizar tareas escolares. Sin anuncios, sin cuentas y sin rastreo.\nDesarrollada por Emmanuel Missin Garcia Vargas (UVEG).');
};

mostrar();
