from whatsapp_bot.models import AutoReplyRule


def buscar_respuesta(texto_entrante):
    texto = (texto_entrante or "").lower()

    reglas = AutoReplyRule.objects.filter(activo=True).order_by("prioridad", "id")

    for regla in reglas:
        if regla.es_fallback:
            continue
        if regla.palabra_clave and regla.palabra_clave.lower() in texto:
            return regla

    return reglas.filter(es_fallback=True).first()
