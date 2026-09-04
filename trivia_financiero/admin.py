from django.contrib import admin

from .models import Jugador, Miembro, Partida, PartidaPregunta, Pregunta, Respuesta, VotoMiembro


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ("texto", "dificultad", "categoria", "activa")
    list_filter = ("dificultad", "categoria", "activa")
    search_fields = ("texto",)


class JugadorInline(admin.TabularInline):
    model = Jugador
    extra = 0
    fields = ("nombre", "tipo", "puntaje_total")
    readonly_fields = fields


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "colegio", "curso", "estado", "pregunta_actual_index", "host_user", "creado_en")
    list_filter = ("estado", "colegio", "curso")
    inlines = [JugadorInline]


class MiembroInline(admin.TabularInline):
    model = Miembro
    extra = 0
    readonly_fields = ("token", "creado_en")


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "partida", "tipo", "puntaje_total")
    list_filter = ("partida", "tipo")
    inlines = [MiembroInline]


@admin.register(PartidaPregunta)
class PartidaPreguntaAdmin(admin.ModelAdmin):
    list_display = ("partida", "orden", "pregunta")
    list_filter = ("partida",)


@admin.register(VotoMiembro)
class VotoMiembroAdmin(admin.ModelAdmin):
    list_display = ("miembro", "partida_pregunta", "opcion_elegida", "tiempo_ms")
    list_filter = ("partida_pregunta__partida",)


@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ("jugador", "partida_pregunta", "opcion_elegida", "es_correcta", "puntos_obtenidos")
    list_filter = ("partida_pregunta__partida", "es_correcta")
