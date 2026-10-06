package io.github.missin03.agendaacademica;

import android.app.DatePickerDialog;
import android.os.Bundle;
import android.widget.RadioGroup;

import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.textfield.TextInputLayout;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

/** Formulario para registrar una tarea nueva. */
public class TareaActivity extends AppCompatActivity {

    private TextInputLayout materia, titulo, descripcion, fecha;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tarea);
        Bordes.aplicar(findViewById(R.id.raiz));
        MaterialToolbar barra = findViewById(R.id.barra);
        barra.setNavigationOnClickListener(v -> finish());

        materia = findViewById(R.id.campo_materia);
        titulo = findViewById(R.id.campo_titulo);
        descripcion = findViewById(R.id.campo_descripcion);
        fecha = findViewById(R.id.campo_fecha);
        fecha.setEndIconOnClickListener(v -> elegirFecha());

        findViewById(R.id.guardar).setOnClickListener(v -> guardar());
        findViewById(R.id.cancelar).setOnClickListener(v -> finish());
    }

    private void elegirFecha() {
        Calendar hoy = Calendar.getInstance();
        new DatePickerDialog(this, (picker, anio, mes, dia) ->
                fecha.getEditText().setText(String.format(Locale.US, "%04d-%02d-%02d", anio, mes + 1, dia)),
                hoy.get(Calendar.YEAR), hoy.get(Calendar.MONTH), hoy.get(Calendar.DAY_OF_MONTH)).show();
    }

    private static String texto(TextInputLayout campo) {
        return campo.getEditText().getText().toString().trim();
    }

    private static boolean fechaValida(String valor) {
        SimpleDateFormat formato = new SimpleDateFormat("yyyy-MM-dd", Locale.US);
        formato.setLenient(false);
        try {
            formato.parse(valor);
            return valor.length() == 10;
        } catch (ParseException e) {
            return false;
        }
    }

    private void guardar() {
        Tarea t = new Tarea();
        t.materia = texto(materia);
        t.titulo = texto(titulo);
        t.descripcion = texto(descripcion);
        t.fechaEntrega = texto(fecha);

        boolean ok = true;
        materia.setError(null);
        titulo.setError(null);
        fecha.setError(null);
        if (t.materia.isEmpty()) {
            materia.setError(getString(R.string.error_materia));
            ok = false;
        }
        if (t.titulo.length() < 3) {
            titulo.setError(getString(R.string.error_titulo));
            ok = false;
        }
        if (!fechaValida(t.fechaEntrega)) {
            fecha.setError(getString(R.string.error_fecha));
            ok = false;
        }
        if (!ok) return;

        int elegido = ((RadioGroup) findViewById(R.id.estados)).getCheckedRadioButtonId();
        if (elegido == R.id.estado_curso) t.estado = Tarea.EN_CURSO;
        else if (elegido == R.id.estado_completada) t.estado = Tarea.COMPLETADA;
        else t.estado = Tarea.PENDIENTE;

        new BaseDatos(this).guardar(t);
        finish();
    }
}
