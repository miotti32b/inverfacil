from openai import OpenAI
from django.conf import settings

def get_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


from openai import OpenAI
from django.conf import settings
import json

def generar_bloques_ia(contexto):

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    perfil = contexto["perfil"]
    snapshot = contexto["snapshot"]
    proy = contexto["proyecciones"]

    base_contexto = f"""
Perfil:
Edad: {getattr(perfil, 'edad', 'N/D')}
Situación habitacional: {getattr(perfil, 'situacion_habitacional', 'N/D')}
Ingreso por hora real: {snapshot.get('ingreso_por_hora')}
Horas diarias: {snapshot.get('horas_diarias')}

Diagnóstico:
Ingresos: {snapshot.get('ingresos')}
Gastos: {snapshot.get('gastos')}
Ahorro mensual: {snapshot.get('ahorro')}
Patrimonio: {snapshot.get('patrimonio')}
Ratio deuda/patrimonio: {snapshot.get('ratio_deuda_patrimonio')}

Objetivos:
{perfil.objetivos}

Proyección 10 años:
Positivo final: {proy['positiva'][-1]}
Medio final: {proy['media'][-1]}
Negativo final: {proy['negativa'][-1]}
"""

    prompt = f"""
Sos Emiliano Miotti.
Asesor financiero argentino.
Directo, estratégico, profesional.
No hablás como IA.
No prometés resultados.

Generá un JSON con EXACTAMENTE esta estructura:

{{
  "diagnostico": "...",
  "estructura": "...",
  "sesgo": "...",
  "proyeccion": "...",
  "accion": "...",
  "cierre": "..."
}}

Cada bloque debe ser texto continuo.
No uses markdown.
No agregues texto fuera del JSON.

Contexto:
{base_contexto}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "Sos Emiliano Miotti. Asesor financiero argentino. Directo y estratégico."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=1200,
    )

    contenido = response.choices[0].message.content

    return json.loads(contenido)





from calculadora.services.proyecciones import calcular_proyecciones
# calculadora/services/resultado.py
import hashlib
from calculadora.models import ResultadoIA

import json
from decimal import Decimal

def _to_json_safe(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_json_safe(v) for v in obj]
    return obj


def _hash_input(data: dict) -> str:
    safe_data = _to_json_safe(data)
    raw = json.dumps(safe_data, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()

# calculadora/services/resultado.py
from calculadora.services.motor_calculos import calcular_motor_financiero


def construir_resultado(perfil, diagnostico, permitir_ver=False):

    snapshot = calcular_motor_financiero(diagnostico)
    proy = calcular_proyecciones(diagnostico)

    snapshot_safe = _to_json_safe(snapshot)
    proy_safe = _to_json_safe(proy)


    input_data = {
        **snapshot,
        "proyecciones": proy,
        "objetivos": perfil.objetivos,   # 👈 IMPORTANTE PARA EL HASH
    }

    input_hash = _hash_input(input_data)

    resultado = ResultadoIA.objects.filter(
        usuario=perfil.user,
        input_hash=input_hash
    ).first()

    if resultado:
        if permitir_ver and resultado.esta_bloqueado:
            resultado.esta_bloqueado = False
            resultado.save(update_fields=["esta_bloqueado"])
        return resultado

    contexto = {
        "perfil": perfil,
        "diagnostico": diagnostico,
        "snapshot": snapshot_safe,
        "proyecciones": proy_safe,
        "objetivos": perfil.objetivos,
    }
    bloques = generar_bloques_ia(contexto)

    bloque_diagnostico = bloques["diagnostico"]
    bloque_estructura  = bloques["estructura"]
    bloque_sesgo       = bloques["sesgo"]
    bloque_proyeccion  = bloques["proyeccion"]
    bloque_accion      = bloques["accion"]
    bloque_cierre      = bloques["cierre"]


    contenido = "\n\n".join([
        "DIAGNÓSTICO\n" + bloque_diagnostico,
        "ESTRUCTURA\n" + bloque_estructura,
        "SESGO\n" + bloque_sesgo,
        "PROYECCIÓN\n" + bloque_proyeccion,
        "ACCIÓN\n" + bloque_accion,
        "CIERRE\n" + bloque_cierre,
    ])


    resultado = ResultadoIA.objects.create(
        usuario=perfil.user,
        input_hash=input_hash,
        contenido=contenido,  # 👈 CLAVE

        bloque_diagnostico=bloque_diagnostico,
        bloque_estructura=bloque_estructura,
        bloque_sesgo=bloque_sesgo,
        bloque_proyeccion=bloque_proyeccion,
        bloque_accion=bloque_accion,
        bloque_cierre=bloque_cierre,

        proy_pos=proy["positiva"],
        proy_med=proy["media"],
        proy_neg=proy["negativa"],
        modelo_ia="gpt-4o-mini",
        esta_bloqueado=not permitir_ver,
    )

    return resultado

