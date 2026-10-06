package io.github.missin03.agendaacademica;

import android.view.View;

import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

/** Ajusta márgenes para que la barra de estado y la de navegación no tapen el contenido. */
final class Bordes {

    private Bordes() {
    }

    static void aplicar(View raiz) {
        int izq = raiz.getPaddingLeft();
        int arriba = raiz.getPaddingTop();
        int der = raiz.getPaddingRight();
        int abajo = raiz.getPaddingBottom();
        ViewCompat.setOnApplyWindowInsetsListener(raiz, (v, insets) -> {
            Insets b = insets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.ime());
            v.setPadding(izq + b.left, arriba + b.top, der + b.right, abajo + b.bottom);
            return WindowInsetsCompat.CONSUMED;
        });
    }
}
