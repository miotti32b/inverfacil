from django.contrib import admin
from django.contrib import messages
from django.utils.crypto import get_random_string

from .models import (
    CarreraRata,
    ClientePerfil,
    DiagnosticoFinanciero,
    Player,
    PlayerResult,
    Scenario,
    QuizQuestion,
    QuizOption,
    QuizParticipacion,
    Plan,
    Subscripcion,
    PromoCode,
)

# =========================
# PERFIL CLIENTE
# =========================
@admin.register(ClientePerfil)
class ClientePerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "edad", "plan_activo", "quiz_score_total", "total_referred")
    search_fields = ("user__username", "referral_code")
    list_filter = ("plan_activo",)
    readonly_fields = ("referral_code", "creado_en", "actualizado_en")


# =========================
# DIAGNÓSTICO
# =========================
@admin.register(DiagnosticoFinanciero)
class DiagnosticoFinancieroAdmin(admin.ModelAdmin):
    list_display = ("cliente", "fecha", "perfil_asignado")
    search_fields = ("cliente__user__username",)
    list_filter = ("fecha",)


# =========================
# MODELOS SIMPLES
# =========================
admin.site.register(CarreraRata)
admin.site.register(Player)
admin.site.register(PlayerResult)
admin.site.register(Scenario)
admin.site.register(QuizQuestion)
admin.site.register(QuizOption)
admin.site.register(QuizParticipacion)


# =========================
# PROMO CODES
# =========================
@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "plan",
        "used_count",
        "max_uses",
        "is_available",
    )
    list_filter = ("plan",)
    search_fields = ("code",)
    readonly_fields = ("used_count",)

    def is_available(self, obj):
        return obj.can_use()

    is_available.boolean = True
    is_available.short_description = "Disponible"


# =========================
# ACCIÓN MASIVA PARA PLANES
# =========================
@admin.action(description="Generar códigos masivos")
def generar_codigos_masivos(modeladmin, request, queryset):
    cantidad = int(request.POST.get("cantidad", 10))
    prefijo = request.POST.get("prefijo", "MASIVO")

    creados = 0

    for plan in queryset:
        for _ in range(cantidad):
            code = f"{prefijo}-{plan.id}-{get_random_string(6).upper()}"
            PromoCode.objects.create(
                code=code,
                plan=plan,
                max_uses=1,
            )
            creados += 1

    messages.success(
        request,
        f"✅ Se generaron {creados} códigos correctamente"
    )


# =========================
# PLANES
# =========================
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "precio")
    actions = [generar_codigos_masivos]


# =========================
# SUBSCRIPCIONES
# =========================
@admin.register(Subscripcion)
class SubscripcionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "plan", "estado", "preapproval_id")
    search_fields = ("usuario__username", "usuario__email")
    list_filter = ("estado", "plan")


from django.contrib import admin
from .models import GiftRequest

@admin.register(GiftRequest)
class GiftRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre_destinatario",
        "telefono_destinatario",
        "plan",
        "pagado",
        "creado_en",
    )
    list_filter = ("pagado", "plan")
    search_fields = ("nombre_destinatario", "telefono_destinatario")
    readonly_fields = ("creado_en",)
