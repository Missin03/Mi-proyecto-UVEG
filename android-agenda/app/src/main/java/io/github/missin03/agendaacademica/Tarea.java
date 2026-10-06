package io.github.missin03.agendaacademica;

/** Una tarea escolar registrada en el teléfono. */
public class Tarea {

    public static final String PENDIENTE = "pendiente";
    public static final String EN_CURSO = "en_curso";
    public static final String COMPLETADA = "completada";

    public long id;
    public String materia;
    public String titulo;
    public String descripcion;
    /** Fecha de entrega en formato AAAA-MM-DD. */
    public String fechaEntrega;
    public String estado;

    /** Estado que sigue al actual: pendiente → en curso → completada → pendiente. */
    public static String siguienteEstado(String estado) {
        switch (estado) {
            case PENDIENTE:
                return EN_CURSO;
            case EN_CURSO:
                return COMPLETADA;
            default:
                return PENDIENTE;
        }
    }
}
