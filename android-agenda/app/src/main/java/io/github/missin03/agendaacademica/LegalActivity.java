package io.github.missin03.agendaacademica;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.text.HtmlCompat;

import com.google.android.material.appbar.MaterialToolbar;

/** Muestra el aviso de privacidad o los términos de uso dentro de la app. */
public class LegalActivity extends AppCompatActivity {

    static final String EXTRA_TIPO = "tipo";
    static final String PRIVACIDAD = "privacidad";
    static final String TERMINOS = "terminos";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_legal);
        Bordes.aplicar(findViewById(R.id.raiz));

        boolean privacidad = !TERMINOS.equals(getIntent().getStringExtra(EXTRA_TIPO));
        MaterialToolbar barra = findViewById(R.id.barra);
        barra.setTitle(privacidad ? R.string.privacidad_titulo : R.string.terminos_titulo);
        barra.setNavigationOnClickListener(v -> finish());

        TextView texto = findViewById(R.id.texto);
        texto.setText(HtmlCompat.fromHtml(getString(privacidad ? R.string.privacidad_html : R.string.terminos_html),
                HtmlCompat.FROM_HTML_MODE_LEGACY));

        findViewById(R.id.ver_en_linea).setOnClickListener(v -> {
            try {
                startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(getString(R.string.url_privacidad))));
            } catch (ActivityNotFoundException e) {
                // Sin navegador instalado: el texto completo ya está en esta pantalla.
            }
        });
    }
}
