CREATE TABLE IF NOT EXISTS materias (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 nombre varchar(100) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS tareas (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 titulo varchar(100) NOT NULL CHECK(length(trim(titulo))>=3),
 descripcion varchar(600) NOT NULL DEFAULT '',
 materia_id integer NOT NULL REFERENCES materias(id),
 fecha_entrega date NOT NULL,
 estado varchar(12) NOT NULL DEFAULT 'Pendiente'
   CHECK(estado IN ('Pendiente','En curso','Completada')),
 creada_en timestamptz NOT NULL DEFAULT current_timestamp
);
CREATE INDEX IF NOT EXISTS idx_tareas_estado_fecha ON tareas(estado,fecha_entrega);
CREATE INDEX IF NOT EXISTS idx_tareas_materia ON tareas(materia_id);
INSERT INTO materias(nombre) VALUES ('Despliegue de aplicaciones web y móviles'),
 ('Ingeniería de software'),('Bases de datos') ON CONFLICT DO NOTHING;
INSERT INTO tareas(titulo,descripcion,materia_id,fecha_entrega,estado)
SELECT 'Preparar el despliegue web','Organizar archivos y documentar el servidor', id,'2026-10-15','En curso'
FROM materias WHERE nombre='Despliegue de aplicaciones web y móviles'
AND NOT EXISTS(SELECT 1 FROM tareas WHERE titulo='Preparar el despliegue web');
INSERT INTO tareas(titulo,descripcion,materia_id,fecha_entrega,estado)
SELECT 'Revisar el modelo de datos','Verificar relaciones e índices', id,'2026-10-18','Pendiente'
FROM materias WHERE nombre='Bases de datos'
AND NOT EXISTS(SELECT 1 FROM tareas WHERE titulo='Revisar el modelo de datos');
INSERT INTO tareas(titulo,descripcion,materia_id,fecha_entrega,estado)
SELECT 'Definir casos de prueba','Documentar entradas y resultados esperados', id,'2026-10-20','Completada'
FROM materias WHERE nombre='Ingeniería de software'
AND NOT EXISTS(SELECT 1 FROM tareas WHERE titulo='Definir casos de prueba');
