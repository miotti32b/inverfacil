import requests
from django.conf import settings


class MetaApiError(Exception):
    pass


def _graph_url():
    return f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"


def _headers():
    return {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }


def _post(payload):
    try:
        resp = requests.post(_graph_url(), headers=_headers(), json=payload, timeout=15)
    except requests.RequestException as e:
        raise MetaApiError(f"Error de red llamando a Meta: {e}")

    if resp.status_code >= 400:
        raise MetaApiError(f"Meta respondió {resp.status_code}: {resp.text}")

    data = resp.json()
    try:
        return data["messages"][0]["id"]
    except (KeyError, IndexError):
        raise MetaApiError(f"Respuesta inesperada de Meta: {data}")


def enviar_texto(wa_id, texto):
    payload = {
        "messaging_product": "whatsapp",
        "to": wa_id,
        "type": "text",
        "text": {"body": texto},
    }
    return _post(payload)


def enviar_template(wa_id, template_name, language="es", params=None):
    components = []
    if params:
        components.append(
            {
                "type": "body",
                "parameters": [{"type": "text", "text": p} for p in params],
            }
        )

    payload = {
        "messaging_product": "whatsapp",
        "to": wa_id,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
            "components": components,
        },
    }
    return _post(payload)
