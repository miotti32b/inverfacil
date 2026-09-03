from django.contrib import admin

from .models import HistorialCapital, Miembro, Participante, Partida, Voto


class MiembroInline(admin.TabularInline):
    model = Miembro
    extra = 0
    readonly_fields = ("token", "creado_en")


class ParticipanteInline(admin.TabularInline):
    model = Participante
    extra = 0
    fields = ("nombre", "tipo", "capital_actual", "deuda")
    readonly_fields = fields


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "estado", "ronda_actual", "ronda_estado", "host_user", "creado_en")
    list_filter = ("estado",)
    inlines = [ParticipanteInline]


@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "partida", "tipo", "capital_inicial", "capital_actual", "deuda")
    list_filter = ("partida", "tipo")
    inlines = [MiembroInline]


@admin.register(Miembro)
class MiembroAdmin(admin.ModelAdmin):
    list_display = ("nombre", "participante", "peso_tier", "monto_asignado", "habilidad", "token")
    list_filter = ("participante__partida", "peso_tier", "habilidad")


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ("miembro", "participante", "ronda", "opcion", "actualizado_en")
    list_filter = ("participante__partida", "ronda")


@admin.register(HistorialCapital)
class HistorialCapitalAdmin(admin.ModelAdmin):
    list_display = ("participante", "ronda", "capital", "deuda")
    list_filter = ("participante__partida", "ronda")
