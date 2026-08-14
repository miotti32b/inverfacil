import hashlib
import hmac
import json

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Contact, Message
from .services import meta_api
from .services.bot_engine import buscar_respuesta


def _firma_valida(request):
    secret = settings.WHATSAPP_APP_SECRET
    if not secret:
        return True

    firma = request.headers.get("X-Hub-Signature-256", "")
    if not firma.startswith("sha256="):
        return False

    esperada = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(firma[len("sha256="):], esperada)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request):
    if request.method == "GET":
        if (
            request.GET.get("hub.mode") == "subscribe"
            and request.GET.get("hub.verify_token") == settings.WHATSAPP_VERIFY_TOKEN
        ):
            return HttpResponse(request.GET.get("hub.challenge", ""), status=200)
        return HttpResponseForbidden("Token de verificación inválido")

    if not _firma_valida(request):
        return HttpResponseForbidden("Firma inválida")

    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": True}, status=200)

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            _procesar_change(change.get("value", {}))

    return JsonResponse({"ok": True}, status=200)


def _procesar_change(value):
    mensajes = value.get("messages")
    if not mensajes:
        return  # payload de "statuses" (entregado/leído) u otro evento que no procesamos en el MVP

    perfiles = {c["wa_id"]: c.get("profile", {}).get("name", "") for c in value.get("contacts", [])}

    for msg in mensajes:
        if msg.get("type") != "text":
            continue  # MVP: solo texto plano

        wa_message_id = msg.get("id")
        if wa_message_id and Message.objects.filter(wa_message_id=wa_message_id).exists():
            continue  # reintento de Meta, ya procesado

        wa_id = msg.get("from")
        texto = msg.get("text", {}).get("body", "")

        contact, _ = Contact.objects.get_or_create(
            wa_id=wa_id, defaults={"nombre_perfil": perfiles.get(wa_id, "")}
        )
        if perfiles.get(wa_id) and contact.nombre_perfil != perfiles[wa_id]:
            contact.nombre_perfil = perfiles[wa_id]
        contact.ultimo_mensaje_en = timezone.now()
        contact.save()

        Message.objects.create(
            contact=contact,
            direccion=Message.DIRECCION_ENTRANTE,
            cuerpo=texto,
            wa_message_id=wa_message_id,
        )

        regla = buscar_respuesta(texto)
        if not regla:
            continue

        try:
            respuesta_id = meta_api.enviar_texto(wa_id, regla.respuesta)
            Message.objects.create(
                contact=contact,
                direccion=Message.DIRECCION_SALIENTE,
                cuerpo=regla.respuesta,
                wa_message_id=respuesta_id,
                es_automatico=True,
            )
            contact.ultimo_mensaje_en = timezone.now()
            contact.save(update_fields=["ultimo_mensaje_en"])
        except meta_api.MetaApiError as e:
            Message.objects.create(
                contact=contact,
                direccion=Message.DIRECCION_SALIENTE,
                cuerpo=regla.respuesta,
                es_automatico=True,
                error_detalle=str(e),
            )


@staff_member_required
def bandeja(request):
    contactos = Contact.objects.all()
    return render(request, "whatsapp_bot/bandeja.html", {"contactos": contactos})


@staff_member_required
def conversacion(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)

    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()
        if texto:
            try:
                wa_message_id = meta_api.enviar_texto(contact.wa_id, texto)
                Message.objects.create(
                    contact=contact,
                    direccion=Message.DIRECCION_SALIENTE,
                    cuerpo=texto,
                    wa_message_id=wa_message_id,
                )
                contact.ultimo_mensaje_en = timezone.now()
                contact.save(update_fields=["ultimo_mensaje_en"])
            except meta_api.MetaApiError as e:
                Message.objects.create(
                    contact=contact,
                    direccion=Message.DIRECCION_SALIENTE,
                    cuerpo=texto,
                    error_detalle=str(e),
                )

    mensajes = contact.mensajes.all()
    return render(
        request, "whatsapp_bot/conversacion.html", {"contact": contact, "mensajes": mensajes}
    )
