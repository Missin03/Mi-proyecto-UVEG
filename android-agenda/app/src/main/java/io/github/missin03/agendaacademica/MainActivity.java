package io.github.missin03.agendaacademica;

import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.ViewCompat;

import com.google.android.material.button.MaterialButton;
import com.google.android.material.chip.Chip;
import com.google.android.material.chip.ChipGroup;
import com.google.android.material.dialog.MaterialAlertDialogBuilder;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {

    private static final Locale ES_MX = Locale.forLanguageTag("es-MX");

    private BaseDatos db;
    private String filtro;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Bordes.aplicar(findViewById(R.id.raiz));
        setSupportActionBar(findViewById(R.id.barra));
        db = new BaseDatos(this);
        ViewCompat.setAccessibilityHeading(findViewById(R.id.encabezado), true);

        ChipGroup filtros = findViewById(R.id.filtros);
        filtros.setOnCheckedStateChangeListener((grupo, ids) -> {
            int id = ids.isEmpty() ? R.id.filtro_todas : ids.get(0);
            if (id == R.id.filtro_pendiente) filtro = Tarea.PENDIENTE;
            else if (id == R.id.filtro_curso) filtro = Tarea.EN_CURSO;
            else if (id == R.id.filtro_completada) filtro = Tarea.COMPLETADA;
            else filtro = null;
            mostrarTareas();
        });

        findViewById(R.id.nueva).setOnClickListener(v ->
                startActivity(new Intent(this, TareaActivity.class)));
    }

    @Override
    protected void onResume() {
        super.onResume();
        mostrarTareas();
    }

    private void mostrarTareas() {
        ((TextView) findViewById(R.id.num_pendientes)).setText(String.valueOf(db.contar(Tarea.PENDIENTE)));
        ((TextView) findViewById(R.id.num_curso)).setText(String.valueOf(db.contar(Tarea.EN_CURSO)));
        ((TextView) findViewById(R.id.num_completadas)).setText(String.valueOf(db.contar(Tarea.COMPLETADA)));

        LinearLayout lista = findViewById(R.id.lista);
        lista.removeAllViews();
        List<Tarea> tareas = db.listar(filtro);
        findViewById(R.id.vacio).setVisibility(tareas.isEmpty() ? View.VISIBLE : View.GONE);

        LayoutInflater inflador = getLayoutInflater();
        for (Tarea t : tareas) {
            View tarjeta = inflador.inflate(R.layout.item_tarea, lista, false);
            ((TextView) tarjeta.findViewById(R.id.materia)).setText(t.materia);
            ((TextView) tarjeta.findViewById(R.id.titulo)).setText(t.titulo);
            TextView descripcion = tarjeta.findViewById(R.id.descripcion);
            descripcion.setText(t.descripcion);
            descripcion.setVisibility(t.descripcion.isEmpty() ? View.GONE : View.VISIBLE);
            ((TextView) tarjeta.findViewById(R.id.fecha)).setText(getString(R.string.entrega, fechaLegible(t.fechaEntrega)));

            Chip estado = tarjeta.findViewById(R.id.estado);
            estado.setText(nombreEstado(t.estado));
            if (!Tarea.PENDIENTE.equals(t.estado)) {
                boolean hecha = Tarea.COMPLETADA.equals(t.estado);
                estado.setChipBackgroundColorResource(hecha ? R.color.verde_claro : R.color.ambar_claro);
                estado.setTextColor(getColor(hecha ? R.color.verde : R.color.ambar));
                estado.setChipStrokeWidth(0);
            }

            MaterialButton avanzar = tarjeta.findViewById(R.id.avanzar);
            avanzar.setText(getString(R.string.marcar_como, nombreEstado(Tarea.siguienteEstado(t.estado)).toLowerCase(ES_MX)));
            avanzar.setOnClickListener(v -> {
                db.cambiarEstado(t.id, Tarea.siguienteEstado(t.estado));
                mostrarTareas();
            });

            MaterialButton eliminar = tarjeta.findViewById(R.id.eliminar);
            eliminar.setContentDescription(getString(R.string.eliminar_tarea, t.titulo));
            eliminar.setOnClickListener(v -> new MaterialAlertDialogBuilder(this)
                    .setTitle(R.string.eliminar_titulo)
                    .setMessage(getString(R.string.eliminar_mensaje, t.titulo))
                    .setNegativeButton(R.string.cancelar, null)
                    .setPositiveButton(R.string.eliminar, (d, w) -> {
                        db.eliminar(t.id);
                        mostrarTareas();
                    })
                    .show());

            lista.addView(tarjeta);
        }
    }

    private String nombreEstado(String estado) {
        switch (estado) {
            case Tarea.EN_CURSO:
                return getString(R.string.en_curso);
            case Tarea.COMPLETADA:
                return getString(R.string.completada);
            default:
                return getString(R.string.pendiente);
        }
    }

    private static String fechaLegible(String iso) {
        try {
            Date fecha = new SimpleDateFormat("yyyy-MM-dd", Locale.US).parse(iso);
            return new SimpleDateFormat("d 'de' MMMM 'de' yyyy", ES_MX).format(fecha);
        } catch (ParseException e) {
            return iso;
        }
    }

    private String version() {
        try {
            return getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
        } catch (PackageManager.NameNotFoundException e) {
            return "";
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.principal, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.menu_privacidad || id == R.id.menu_terminos) {
            startActivity(new Intent(this, LegalActivity.class)
                    .putExtra(LegalActivity.EXTRA_TIPO, id == R.id.menu_privacidad
                            ? LegalActivity.PRIVACIDAD : LegalActivity.TERMINOS));
            return true;
        }
        if (id == R.id.menu_acerca) {
            new MaterialAlertDialogBuilder(this)
                    .setTitle(R.string.app_name)
                    .setMessage(getString(R.string.acerca_mensaje, version()))
                    .setPositiveButton(R.string.aceptar, null)
                    .show();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
}
