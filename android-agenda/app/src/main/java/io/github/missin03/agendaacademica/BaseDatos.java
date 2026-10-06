package io.github.missin03.agendaacademica;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.util.ArrayList;
import java.util.List;

/** Base de datos SQLite local. Nada sale del dispositivo. */
public class BaseDatos extends SQLiteOpenHelper {

    private static final String NOMBRE = "agenda.db";
    private static final int VERSION = 1;

    public BaseDatos(Context contexto) {
        super(contexto, NOMBRE, null, VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE tareas ("
                + "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                + "materia TEXT NOT NULL,"
                + "titulo TEXT NOT NULL,"
                + "descripcion TEXT NOT NULL DEFAULT '',"
                + "fecha_entrega TEXT NOT NULL,"
                + "estado TEXT NOT NULL DEFAULT 'pendiente'"
                + " CHECK (estado IN ('pendiente','en_curso','completada')),"
                + "creada TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)");
        db.execSQL("CREATE INDEX idx_tareas_fecha ON tareas (fecha_entrega)");
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int anterior, int nueva) {
        // Primera versión: todavía no hay migraciones.
    }

    /** Tareas filtradas por estado (null = todas); las completadas van al final. */
    public List<Tarea> listar(String estado) {
        String filtro = estado == null ? null : "estado = ?";
        String[] args = estado == null ? null : new String[]{estado};
        List<Tarea> tareas = new ArrayList<>();
        try (Cursor c = getReadableDatabase().query("tareas",
                new String[]{"id", "materia", "titulo", "descripcion", "fecha_entrega", "estado"},
                filtro, args, null, null,
                "estado = 'completada', fecha_entrega, id")) {
            while (c.moveToNext()) {
                Tarea t = new Tarea();
                t.id = c.getLong(0);
                t.materia = c.getString(1);
                t.titulo = c.getString(2);
                t.descripcion = c.getString(3);
                t.fechaEntrega = c.getString(4);
                t.estado = c.getString(5);
                tareas.add(t);
            }
        }
        return tareas;
    }

    public int contar(String estado) {
        try (Cursor c = getReadableDatabase().rawQuery(
                "SELECT COUNT(*) FROM tareas WHERE estado = ?", new String[]{estado})) {
            return c.moveToFirst() ? c.getInt(0) : 0;
        }
    }

    public void guardar(Tarea t) {
        ContentValues v = new ContentValues();
        v.put("materia", t.materia);
        v.put("titulo", t.titulo);
        v.put("descripcion", t.descripcion);
        v.put("fecha_entrega", t.fechaEntrega);
        v.put("estado", t.estado);
        getWritableDatabase().insert("tareas", null, v);
    }

    public void cambiarEstado(long id, String estado) {
        ContentValues v = new ContentValues();
        v.put("estado", estado);
        getWritableDatabase().update("tareas", v, "id = ?", new String[]{String.valueOf(id)});
    }

    public void eliminar(long id) {
        getWritableDatabase().delete("tareas", "id = ?", new String[]{String.valueOf(id)});
    }
}
