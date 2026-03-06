import json
import hashlib
from decimal import Decimal
from openai import OpenAI
from django.conf import settings
from calculadora.models import ResultadoIA
from calculadora.services.motor_calculos import calcular_motor_financiero
from calculadora.services.proyecciones import calcular_proyecciones

# Inicializamos el cliente de OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)

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

def generar_respuesta_ia_unica(contexto):
    try:
        perfil = contexto["perfil"]
        snapshot = contexto["snapshot"]
        proy = contexto["proyecciones"]

        # 🔥 Proyecciones al Año 10
        proy_pos_final = proy.get('positiva', [0])[-1]
        proy_med_final = proy.get('media', [0])[-1]
        proy_neg_final = proy.get('negativa', [0])[-1]

        # Formateo de las respuestas psicológicas
        importancia = getattr(perfil, 'importancia_dinero', 'No especificado')
        uso_millon = getattr(perfil, 'uso_millon', 'No especificado')
        reaccion = getattr(perfil, 'reaccion_perdida', 'No especificado')
        seguridad = getattr(perfil, 'conocimiento_seguridad', 'No especificado')

        # Variables cualitativas y ratios del Motor
        estado_general = snapshot.get("estado_general", "desconocido")
        dependencia = snapshot.get("dependencia_ingreso", "alta")
        margen_error = snapshot.get("margen_error", "bajo")
        
        # Multiplicamos por 100 para que la IA entienda porcentajes fácilmente
        ratio_libertad = float(snapshot.get("ratio_libertad") or 0) * 100
        deuda_toxica = float(snapshot.get("porcentaje_deuda_toxica") or 0) * 100
        inmovilizado = float(snapshot.get("porcentaje_inmovilizado") or 0) * 100
        
        meses_supervivencia = float(snapshot.get("meses_supervivencia") or 0)
        horas_esclavas = float(snapshot.get("horas_esclavas") or 0)

        prompt = f"""
        Sos Emiliano Miotti, un asesor financiero argentino de alto nivel.
        Hablá con voseo argentino ("vos tenés", "fijate", "hacé", "guita"), pero mantené un tono 100% profesional, estratégico y de autoridad.
        Sos muy frontal: elogiá lo que hace bien, pero sé directo e implacable marcando sus ineficiencias. No hablés como una IA amable ni pidas disculpas.

        Generá un análisis financiero devolviendo ÚNICAMENTE un JSON con esta estructura exacta:
        {{
            "bloque_diagnostico": "Resumen de su realidad. Su estado general es '{estado_general.upper()}'. Mencioná que su margen de error ante imprevistos es '{margen_error}'. Usá el dato de sus 'horas esclavas' ({horas_esclavas:.0f} hs/mes) para decirle cuánto tiempo de su vida quema solo para pagar su estilo de vida actual. Destruí la ilusión de que ganar bien es ser rico si gasta todo.",
            "bloque_estructura": "Análisis patrimonial. Decile cuántos meses de supervivencia reales tiene ({meses_supervivencia:.1f} meses) si hoy se queda sin ingresos. Si su capital inmovilizado ({inmovilizado:.0f}%) es alto, explicale el concepto de 'falsa riqueza' (tener bienes que generan gastos en vez de ingresos). Si tiene deuda tóxica ({deuda_toxica:.0f}%), retalo por financiarse caro para consumir.",
            "bloque_sesgo": "Confrontalo con su psicología. Dice que reacciona a las pérdidas con: '{reaccion}', que valora '{importancia}' del dinero y que se siente seguro en '{seguridad}'. Si hay contradicciones (ej: valora la libertad pero el {100 - ratio_libertad:.0f}% de su vida depende de su sueldo activo), decíselo en la cara. Cuestioná sus creencias.",
            "bloque_proyeccion": "Mostrale su futuro en 10 años basándote en los números dados. El escenario positivo (${proy_pos_final:,.0f}) debe ser muy esperanzador; el neutro (${proy_med_final:,.0f}) un estancamiento llano; y el negativo (${proy_neg_final:,.0f}) alarmante. Contrastalos brutalmente.",
            "bloque_accion": "3 pasos tácticos, claros y urgentes a ejecutar esta semana para salir del estado '{estado_general}'. Deben estar alineados a su objetivo: {contexto['objetivos']}.",
            "bloque_cierre": "Un mensaje final corto, firme y motivador, firmando como Emiliano."
        }}

        Información dura:
        - Edad: {perfil.edad}
        - Ingresos totales: ${snapshot.get('ingresos', 0):,.0f}
        - Gastos totales: ${snapshot.get('gastos', 0):,.0f}
        - Patrimonio: ${snapshot.get('patrimonio', 0):,.0f}
        - Deuda Total: ${snapshot.get('deuda', 0):,.0f}
        - Dependencia de ingreso: {dependencia.upper()} (si es alta, está a un despido/crisis de la quiebra).

        (Respondé SÓLO el JSON, sin formato markdown).
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Responde exclusivamente en JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        tokens = response.usage.total_tokens if response.usage else 0
        costo_estimado = tokens * 0.00000015 

        return {
            "estado": "ok",
            "data": data,
            "tokens": tokens,
            "costo": costo_estimado
        }

    except Exception as e:
        return {
            "estado": "error",
            "error_msg": str(e),
            "data": None,
            "tokens": 0,
            "costo": 0
        }

def construir_resultado(perfil, diagnostico, permitir_ver=False):

    snapshot = calcular_motor_financiero(diagnostico)
    proy = calcular_proyecciones(diagnostico)

    snapshot_safe = _to_json_safe(snapshot)
    proy_safe = _to_json_safe(proy)

    input_data = {
        **snapshot,
        "proyecciones": proy,
        "objetivos": perfil.objetivos,
    }

    input_hash = _hash_input(input_data)

    resultado_existente = ResultadoIA.objects.filter(
        usuario=perfil.user,
        input_hash=input_hash
    ).first()

    if resultado_existente:
        if permitir_ver and resultado_existente.esta_bloqueado:
            resultado_existente.esta_bloqueado = False
            resultado_existente.save(update_fields=["esta_bloqueado"])
        return resultado_existente

    contexto = {
        "perfil": perfil,
        "diagnostico": diagnostico,
        "snapshot": snapshot_safe,
        "proyecciones": proy_safe,
        "objetivos": perfil.objetivos,
    }

    # 🔥 LLAMADA ÚNICA A OPENAI
    respuesta = generar_respuesta_ia_unica(contexto)

    if respuesta["estado"] == "error":
        return ResultadoIA.objects.create(
            usuario=perfil.user,
            input_hash=input_hash,
            contenido="Error generando resultado",
            modelo_ia="gpt-4o-mini",
            tokens_usados=0,
            costo_estimado_usd=0,
            estado="error",
            error_msg=respuesta["error_msg"],
            esta_bloqueado=True,
        )

    data = respuesta["data"]

    bloque_diagnostico = str(data.get("bloque_diagnostico", ""))
    bloque_estructura = str(data.get("bloque_estructura", ""))
    bloque_sesgo = str(data.get("bloque_sesgo", ""))
    bloque_proyeccion = str(data.get("bloque_proyeccion", ""))
    bloque_accion = str(data.get("bloque_accion", ""))
    bloque_cierre = str(data.get("bloque_cierre", ""))

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
        contenido=contenido,

        bloque_diagnostico=bloque_diagnostico,
        bloque_estructura=bloque_estructura,
        bloque_sesgo=bloque_sesgo,
        bloque_proyeccion=bloque_proyeccion,
        bloque_accion=bloque_accion,
        bloque_cierre=bloque_cierre,

        proy_pos=proy_safe["positiva"],
        proy_med=proy_safe["media"],
        proy_neg=proy_safe["negativa"],

        modelo_ia="gpt-4o-mini",
        tokens_usados=respuesta["tokens"],
        costo_estimado_usd=respuesta["costo"],
        estado="ok",
        esta_bloqueado=not permitir_ver,
    )

    return resultado