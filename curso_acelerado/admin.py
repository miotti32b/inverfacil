from django.contrib import admin

from .models import (
    Curso,
    ImagenModulo,
    IntentoQuiz,
    Modulo,
    OpcionDiagnostico,
    OpcionRespuesta,
    Pregunta,
    PreguntaDiagnostico,
    ProgresoCurso,
    ProgresoModulo,
    Quiz,
    RespuestaAlumno,
)


class ImagenModuloInline(admin.TabularInline):
    model = ImagenModulo
    extra = 1


class QuizInline(admin.StackedInline):
    model = Quiz
    extra = 0
    max_num = 1


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "slug", "activo", "creado_en")
    prepopulated_fields = {"slug": ("titulo",)}
    search_fields = ("titulo", "descripcion")


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ("numero", "titulo", "curso", "activo")
    list_filter = ("curso", "activo")
    search_fields = ("titulo", "descripcion", "contenido_teorico")
    inlines = (ImagenModuloInline, QuizInline)


class OpcionDiagnosticoInline(admin.TabularInline):
    model = OpcionDiagnostico
    extra = 4


@admin.register(PreguntaDiagnostico)
class PreguntaDiagnosticoAdmin(admin.ModelAdmin):
    list_display = ("texto", "modulo", "orden")
    list_filter = ("modulo",)
    search_fields = ("texto",)
    inlines = (OpcionDiagnosticoInline,)


class OpcionRespuestaInline(admin.TabularInline):
    model = OpcionRespuesta
    extra = 4


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("titulo", "modulo", "porcentaje_aprobacion", "activo")
    list_filter = ("activo", "porcentaje_aprobacion")


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ("texto", "quiz", "orden")
    list_filter = ("quiz",)
    search_fields = ("texto",)
    inlines = (OpcionRespuestaInline,)


@admin.register(OpcionRespuesta)
class OpcionRespuestaAdmin(admin.ModelAdmin):
    list_display = ("texto", "pregunta", "es_correcta", "orden")
    list_filter = ("es_correcta", "pregunta__quiz")
    search_fields = ("texto",)


class RespuestaAlumnoInline(admin.TabularInline):
    model = RespuestaAlumno
    extra = 0
    readonly_fields = ("pregunta", "opcion", "es_correcta")
    can_delete = False


@admin.register(IntentoQuiz)
class IntentoQuizAdmin(admin.ModelAdmin):
    list_display = ("usuario", "quiz", "puntaje", "aprobado", "correctas", "total_preguntas", "creado_en")
    list_filter = ("aprobado", "quiz")
    search_fields = ("usuario__username", "usuario__email")
    readonly_fields = ("usuario", "quiz", "puntaje", "aprobado", "correctas", "total_preguntas", "creado_en")
    inlines = (RespuestaAlumnoInline,)


@admin.register(ProgresoModulo)
class ProgresoModuloAdmin(admin.ModelAdmin):
    list_display = ("usuario", "modulo", "estado", "mejor_puntaje", "intentos", "aprobado_en")
    list_filter = ("estado", "modulo__curso")
    search_fields = ("usuario__username", "usuario__email", "modulo__titulo")


@admin.register(ProgresoCurso)
class ProgresoCursoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "curso", "modulos_completados", "porcentaje", "actualizado_en")
    list_filter = ("curso",)
    search_fields = ("usuario__username", "usuario__email")

# Register your models here.
