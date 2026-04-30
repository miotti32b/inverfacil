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
    Company,
    Portfolio,
    Transaction,
)

# =========================
# PERFIL CLIENTE
# =========================
@admin.register(ClientePerfil)
class ClientePerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "edad", "plan_activo", "diagnosticos_realizados", "quiz_score_total", "total_referred")
    search_fields = ("user__username", "referral_code")
    list_filter = ("plan_activo",)
    readonly_fields = ("referral_code", "creado_en", "actualizado_en")


# =========================
# DIAGNÓSTICO
# =========================
@admin.register(DiagnosticoFinanciero)
class DiagnosticoFinancieroAdmin(admin.ModelAdmin):
    list_display = ("cliente", "fecha", "estado_financiero", "estabilidad_laboral", "conocimiento_financiero", "confianza_sistema", "perfil_asignado")
    search_fields = ("cliente__user__username",)
    list_filter = ("fecha", "estado_financiero", "estabilidad_laboral", "conocimiento_financiero", "confianza_sistema")


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


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("display_name", "ticker", "sector", "current_price", "last_noise_percent", "traded_volume", "is_anonymous", "quote_reason")
    list_filter = ("sector", "is_anonymous", "quote_reason")
    search_fields = ("name",)
    readonly_fields = ("valuation_initial", "previous_price", "current_price", "last_noise_percent")


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("user", "cash_balance", "updated_at")
    search_fields = ("user__username", "user__email")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "type", "quantity", "price_at_transaction", "timestamp")
    list_filter = ("type", "company", "timestamp")
    search_fields = ("user__username", "company__name")


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


# =========================
# SOLICITUDES DE ASESORÍA
# =========================
from calculadora.models import SolicitudAsesoria, GiftRequest, ResultadoIA, InscripcionCursoFintech
from django.contrib import admin

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


@admin.register(SolicitudAsesoria)
class SolicitudAsesoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'horario_preferido', 'atendida', 'creado_en')
    list_filter = ('atendida', 'creado_en')
    search_fields = ('nombre', 'email', 'cliente__user__username')
    readonly_fields = ('cliente', 'nombre', 'email', 'creado_en')
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('cliente', 'nombre', 'email')
        }),
        ('Solicitud', {
            'fields': ('horario_preferido', 'atendida')
        }),
        ('Fecha', {
            'fields': ('creado_en',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_como_atendida']
    
    def marcar_como_atendida(self, request, queryset):
        updated = queryset.update(atendida=True)
        self.message_user(request, f"✅ {updated} solicitud(es) marcadas como atendidas")
    
    marcar_como_atendida.short_description = "✅ Marcar como atendida"


# =========================
# INSCRIPCIONES CURSO FINTECH
# =========================
@admin.register(InscripcionCursoFintech)
class InscripcionCursoFintechAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'edad', 'mes_elegido', 'atendida', 'creado_en')
    list_filter = ('mes_elegido', 'atendida', 'creado_en')
    search_fields = ('nombre', 'email', 'cliente__user__username')
    readonly_fields = ('cliente', 'nombre', 'email', 'edad', 'creado_en')

    fieldsets = (
        ('Información del Alumno', {
            'fields': ('cliente', 'nombre', 'email', 'edad')
        }),
        ('Inscripción', {
            'fields': ('mes_elegido', 'atendida')
        }),
        ('Fecha', {
            'fields': ('creado_en',),
            'classes': ('collapse',)
        }),
    )

    actions = ['marcar_como_atendida']

    def marcar_como_atendida(self, request, queryset):
        updated = queryset.update(atendida=True)
        self.message_user(request, f"✅ {updated} inscripción(es) marcadas como atendidas")

    marcar_como_atendida.short_description = "✅ Marcar como atendida"


# =========================
# RESULTADO IA (DEBUG)
# =========================
@admin.register(ResultadoIA)
class ResultadoIAAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'estado', 'creado_en', 'tiene_metas', 'tiene_acciones', 'tiene_proy')
    search_fields = ('usuario__username',)
    list_filter = ('estado', 'creado_en')
    readonly_fields = ('usuario', 'input_hash', 'creado_en', 'bloque_sesgo_display', 'bloque_accion_display', 'proy_pos_display')
    
    fieldsets = (
        ('Información General', {
            'fields': ('usuario', 'input_hash', 'creado_en', 'estado')
        }),
        ('Contenido IA', {
            'fields': ('bloque_diagnostico', 'bloque_proyeccion')
        }),
        ('Datos Parseables', {
            'fields': ('bloque_sesgo_display', 'bloque_accion_display', 'proy_pos_display'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('modelo_ia', 'tokens_usados', 'costo_estimado_usd', 'error_msg'),
            'classes': ('collapse',)
        }),
    )
    
    def tiene_metas(self, obj):
        return bool(obj.bloque_sesgo and len(obj.bloque_sesgo) > 5)
    tiene_metas.boolean = True
    tiene_metas.short_description = "¿Metas?"
    
    def tiene_acciones(self, obj):
        return bool(obj.bloque_accion and len(obj.bloque_accion) > 5)
    tiene_acciones.boolean = True
    tiene_acciones.short_description = "¿Acciones?"
    
    def tiene_proy(self, obj):
        return bool(obj.proy_pos and len(obj.proy_pos) > 0)
    tiene_proy.boolean = True
    tiene_proy.short_description = "¿Proyecciones?"
    
    def bloque_sesgo_display(self, obj):
        return obj.bloque_sesgo[:300] if obj.bloque_sesgo else "❌ VACÍO"
    bloque_sesgo_display.short_description = "Metas (primeros 300 chars)"
    
    def bloque_accion_display(self, obj):
        return obj.bloque_accion[:300] if obj.bloque_accion else "❌ VACÍO"
    bloque_accion_display.short_description = "Acciones (primeros 300 chars)"
    
    def proy_pos_display(self, obj):
        if obj.proy_pos:
            return f"[{len(obj.proy_pos)} valores] {str(obj.proy_pos)[:100]}..."
        return "❌ VACÍO"
    proy_pos_display.short_description = "Proyección Positiva"
