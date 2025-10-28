from django.contrib import admin
from .models import (
    CarreraRata,
    ClientePerfil,
    DiagnosticoFinanciero,
    Player,
    PlayerResult,
    Scenario,
    QuizQuestion,
    QuizOption,
    QuizParticipacion
)

@admin.register(ClientePerfil)
class ClientePerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "edad", "plan_activo", "quiz_score_total", "total_referred")
    search_fields = ("user__username", "referral_code")
    list_filter = ("plan_activo",)
    readonly_fields = ("referral_code", "creado_en", "actualizado_en")


@admin.register(DiagnosticoFinanciero)
class DiagnosticoFinancieroAdmin(admin.ModelAdmin):
    list_display = ("cliente", "fecha", "perfil_asignado")
    search_fields = ("cliente__user__username",)
    list_filter = ("fecha",)


admin.site.register(CarreraRata)
admin.site.register(Player)
admin.site.register(PlayerResult)
admin.site.register(Scenario)
admin.site.register(QuizQuestion)
admin.site.register(QuizOption)
admin.site.register(QuizParticipacion)
