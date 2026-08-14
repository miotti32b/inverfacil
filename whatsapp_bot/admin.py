from django.contrib import admin, messages

from .models import AutoReplyRule, BroadcastCampaign, CampaignRecipient, Contact, Message
from .services import meta_api


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("nombre_perfil", "wa_id", "estado", "cliente_perfil", "ultimo_mensaje_en")
    list_filter = ("estado",)
    search_fields = ("wa_id", "nombre_perfil")
    autocomplete_fields = ("cliente_perfil",)
    readonly_fields = ("wa_id", "creado_en", "ultimo_mensaje_en")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("contact", "direccion", "cuerpo", "es_automatico", "creado_en")
    list_filter = ("direccion", "es_automatico")
    search_fields = ("contact__wa_id", "contact__nombre_perfil", "cuerpo")
    readonly_fields = [f.name for f in Message._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(AutoReplyRule)
class AutoReplyRuleAdmin(admin.ModelAdmin):
    list_display = ("palabra_clave", "es_fallback", "prioridad", "activo")
    list_editable = ("prioridad", "activo")
    list_filter = ("activo", "es_fallback")


class CampaignRecipientInline(admin.TabularInline):
    model = CampaignRecipient
    extra = 0
    readonly_fields = ("contact", "estado", "wa_message_id", "error_detalle", "actualizado_en")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(BroadcastCampaign)
class BroadcastCampaignAdmin(admin.ModelAdmin):
    list_display = ("nombre", "template_name", "estado_objetivo", "estado", "creado_en", "enviado_en")
    list_filter = ("estado",)
    inlines = [CampaignRecipientInline]
    actions = ["enviar_campana"]

    @admin.action(description="Enviar campaña seleccionada")
    def enviar_campana(self, request, queryset):
        for campana in queryset:
            if campana.estado not in (BroadcastCampaign.ESTADO_BORRADOR, BroadcastCampaign.ESTADO_ERROR):
                self.message_user(
                    request,
                    f"'{campana}' no está en borrador/error, se omite.",
                    level=messages.WARNING,
                )
                continue

            contactos = campana.contactos_objetivo()
            enviados, fallidos = 0, 0

            for contacto in contactos:
                recipient, _ = CampaignRecipient.objects.get_or_create(
                    campaign=campana, contact=contacto
                )
                if recipient.estado == CampaignRecipient.ESTADO_ENVIADO:
                    continue
                try:
                    wa_message_id = meta_api.enviar_template(
                        contacto.wa_id, campana.template_name, campana.template_language
                    )
                    recipient.estado = CampaignRecipient.ESTADO_ENVIADO
                    recipient.wa_message_id = wa_message_id
                    recipient.error_detalle = ""
                    enviados += 1
                except meta_api.MetaApiError as e:
                    recipient.estado = CampaignRecipient.ESTADO_ERROR
                    recipient.error_detalle = str(e)
                    fallidos += 1
                recipient.save()

            from django.utils import timezone

            campana.estado = BroadcastCampaign.ESTADO_ERROR if fallidos else BroadcastCampaign.ESTADO_ENVIADO
            campana.enviado_en = timezone.now()
            campana.save(update_fields=["estado", "enviado_en"])

            self.message_user(
                request, f"'{campana}': {enviados} enviados, {fallidos} con error."
            )
