import hashlib
import json
import os
from decimal import Decimal

from openai import OpenAI


api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


METAS_MAP = {
    "independencia_financiera": {
        "emoji": "💸",
        "label": "Independencia Financiera",
        "imagen": "/static/metas/if.png",
        "descripcion": "Generar ingresos pasivos suficientes para cubrir tus gastos sin trabajar.",
    },
    "emprender": {
        "emoji": "🚀",
        "label": "Emprender",
        "imagen": "/static/metas/em.png",
        "descripcion": "Crear tu propio negocio y ser tu jefe con completa libertad.",
    },
    "invertir_mas": {
        "emoji": "📈",
        "label": "Aumentar Inversiones",
        "imagen": "/static/metas/im.png",
        "descripcion": "Hacer crecer tu patrimonio a través de inversiones inteligentes.",
    },
    "comprar_vivienda": {
        "emoji": "🏠",
        "label": "Comprar Vivienda",
        "imagen": "/static/metas/cc.png",
        "descripcion": "Tener tu propio hogar pagado y asegurado.",
    },
    "viajar": {
        "emoji": "🌍",
        "label": "Viajar y Disfrutar",
        "imagen": "/static/metas/v.png",
        "descripcion": "Explorar el mundo y vivir experiencias inolvidables.",
    },
    "educacion": {
        "emoji": "🎓",
        "label": "Educación y Formación",
        "imagen": "/static/metas/e.png",
        "descripcion": "Invertir en tu desarrollo personal y profesional continuo.",
    },
    "calidad_vida": {
        "emoji": "🧘",
        "label": "Calidad de Vida",
        "imagen": "/static/metas/cv.png",
        "descripcion": "Trabajar menos y disfrutar más con tiempo para ti y tu familia.",
    },
    "ayudar": {
        "emoji": "❤️",
        "label": "Ayudar a Otros",
        "imagen": "/static/metas/a.png",
        "descripcion": "Impactar positivamente en la vida de otras personas.",
    },
}


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
    raw = json.dumps(safe_data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _money(value) -> str:
    return f"${float(value):,.0f}"


def _first(values, default="sin_definir"):
    if values:
        return values[0]
    return default


def obtener_meta_del_perfil(perfil, diagnostico=None):
    if diagnostico and getattr(diagnostico, "objetivos_ordenados", None):
        return diagnostico.objetivos_ordenados[0]
    if perfil and getattr(perfil, "objetivos", None):
        return perfil.objetivos[0]
    return "independencia_financiera"


def construir_radiografia_base(diagnostico, snapshot):
    ingresos = float(snapshot.get("ingresos", 0))
    gastos = float(snapshot.get("gastos", 0))
    ahorro = float(snapshot.get("ahorro", 0))
    patrimonio = float(snapshot.get("patrimonio", 0))
    deuda = float(snapshot.get("deuda", 0))
    ratio_libertad = float(snapshot.get("ratio_libertad", 0)) * 100
    estado = snapshot.get("estado_general", "despegando")
    riesgo = snapshot.get("riesgo_principal", "crecer sin sistema claro")
    palanca = snapshot.get("palanca_principal", "ordenar tu sistema financiero")
    estabilidad = int(snapshot.get("percepcion_estabilidad", 0) or 0)
    conocimiento = int(snapshot.get("conocimiento_financiero", 0) or 0)
    prejuicio = snapshot.get("nivel_prejuicio", "bajo")
    bloqueos = ", ".join(snapshot.get("bloqueos_detectados", []) or []) or "sin bloqueos declarados"

    if ahorro <= 0:
        parrafo_1 = (
            f"Hoy estás en una posición {estado}: ingresás {_money(ingresos)} por mes, gastás {_money(gastos)} "
            f"y tu flujo mensual está en {_money(ahorro)}. Con un margen de libertad de {ratio_libertad:.1f}%, "
            "tu prioridad no es invertir mejor sino dejar de operar con el agua al cuello."
        )
    else:
        parrafo_1 = (
            f"Hoy estás en una posición {estado}: ingresás {_money(ingresos)} por mes, gastás {_money(gastos)} "
            f"y te queda un excedente de {_money(ahorro)}. Tu margen de libertad está en {ratio_libertad:.1f}%, "
            "así que ya existe base para construir, pero todavía no necesariamente un sistema sólido."
        )

    parrafo_2 = (
        f"Tu balance muestra patrimonio por {_money(patrimonio)} frente a deudas por {_money(deuda)}. "
        f"El riesgo principal hoy es {riesgo}. Además, tu estabilidad percibida está en {estabilidad}/5, "
        f"tu conocimiento financiero en {conocimiento}/5 y tu nivel de prejuicio hacia el sistema es {prejuicio}. "
        f"Eso explica por qué tus bloqueos actuales giran alrededor de: {bloqueos}."
    )

    parrafo_3 = (
        f"La palanca que más puede cambiar tu resultado hoy es {palanca}. Si ordenás primero flujo, liquidez "
        "y criterio de decisión, recién ahí tu esfuerzo empieza a transformarse en patrimonio con dirección. "
        "El diagnóstico no marca falta de potencial: marca dónde se está fugando o frenando."
    )

    return "\n\n".join([parrafo_1, parrafo_2, parrafo_3])


def construir_feedback_meta_base(meta, diagnostico, snapshot):
    meta_info = METAS_MAP.get(meta, METAS_MAP["independencia_financiera"])
    ahorro = float(snapshot.get("ahorro", 0))
    gastos = float(snapshot.get("gastos", 1) or 1)
    meses_supervivencia = float(snapshot.get("meses_supervivencia", 0) or 0)
    conocimiento = int(snapshot.get("conocimiento_financiero", 0) or 0)
    prejuicio = snapshot.get("nivel_prejuicio", "bajo")

    if ahorro > 0:
        tiempo = "Tenés base para acercarte si transformás ese excedente en sistema."
    else:
        tiempo = "Hoy esa meta no está lejos por falta de deseo, sino por falta de margen operativo."

    return (
        f"{meta_info['label']} no es solo un deseo aspiracional: es una dirección válida para vos. "
        f"{tiempo} Hoy tu colchón cubre alrededor de {meses_supervivencia:.1f} meses de gastos, "
        f"tu conocimiento financiero está en {conocimiento}/5 y tu nivel de prejuicio es {prejuicio}. "
        "Eso significa que la distancia a tu meta no depende solo de ganar más, sino de ordenar mejor tu relación "
        "con el riesgo, la liquidez y las decisiones que venís postergando."
    )


def construir_plan_guerra_base(meta, diagnostico, snapshot):
    ingresos = float(snapshot.get("ingresos", 0))
    gastos = float(snapshot.get("gastos", 0))
    ahorro = float(snapshot.get("ahorro", 0))
    deuda = float(snapshot.get("deuda", 0))
    prejuicio = snapshot.get("nivel_prejuicio", "bajo")
    conocimiento = int(snapshot.get("conocimiento_financiero", 0) or 0)
    estabilidad = int(snapshot.get("percepcion_estabilidad", 0) or 0)
    ratio_libertad = float(snapshot.get("ratio_libertad", 0)) * 100

    corto = []
    mediano = []
    largo = []

    if ahorro <= 0:
        corto.append(
            f"En las próximas 48 horas cerrá una radiografía operativa: ingresos {_money(ingresos)}, gastos {_money(gastos)} y fuga real. "
            "Tu primera misión es volver positivo el flujo mensual, aunque sea con un recorte temporal agresivo."
        )
        corto.append(
            f"Congelá cualquier decisión de inversión nueva y atacá el frente que más presión mete hoy: deuda por {_money(deuda)} o gasto fijo sobredimensionado. "
            "Sin flujo libre, el resto es ruido."
        )
    else:
        corto.append(
            f"Automatizá desde este mes una separación del excedente actual de {_money(ahorro)} antes de tocarlo. "
            "Si no sale primero, ese dinero termina financiando desorden en vez de construir libertad."
        )
        corto.append(
            f"Definí una cuenta o vehículo de caja para tu colchón táctico hasta cubrir al menos 3 meses de gastos. "
            f"Hoy tu margen de libertad es {ratio_libertad:.1f}% y eso todavía necesita defensa."
        )

    mediano.append(
        f"Durante los próximos 90 días reducí tu dependencia del ingreso principal y levantá una segunda fuente real o más estable. "
        f"Tu estabilidad percibida es {estabilidad}/5, así que crecer sin respaldo te deja expuesto."
    )
    mediano.append(
        f"Subí tu criterio financiero un punto completo: hoy estás en {conocimiento}/5 de conocimiento y prejuicio {prejuicio}. "
        "Elegí un sistema simple de seguimiento, una rutina semanal y un set chico de instrumentos que realmente entiendas."
    )

    largo.append(
        f"Tu plan de 12 a 24 meses tiene que responder a la meta {METAS_MAP.get(meta, METAS_MAP['independencia_financiera'])['label']}. "
        "No acumules activos al azar: definí porcentaje de liquidez, porcentaje invertible y reglas claras de reinversión."
    )
    largo.append(
        "Cuando el flujo, la caja y el criterio estén ordenados, recién ahí escalá. El objetivo no es parecer sofisticado, "
        "sino construir una estructura que no se caiga cada vez que el mercado, tu trabajo o tu cabeza meten presión."
    )

    return {"corto_plazo": corto, "mediano_plazo": mediano, "largo_plazo": largo}


def _prompt_context(diagnostico, snapshot, meta_label):
    return f"""
DATOS:
- Ingresos: {_money(snapshot.get('ingresos', 0))}
- Gastos: {_money(snapshot.get('gastos', 0))}
- Ahorro: {_money(snapshot.get('ahorro', 0))}
- Patrimonio: {_money(snapshot.get('patrimonio', 0))}
- Deuda: {_money(snapshot.get('deuda', 0))}
- Estado general: {snapshot.get('estado_general')}
- Perfil financiero: {snapshot.get('perfil_financiero')}
- Riesgo principal: {snapshot.get('riesgo_principal')}
- Palanca principal: {snapshot.get('palanca_principal')}
- Estabilidad laboral: {snapshot.get('estabilidad_laboral')}
- Estabilidad percibida: {snapshot.get('percepcion_estabilidad')}/5
- Conocimiento financiero: {snapshot.get('conocimiento_financiero')}/5
- Confianza en el sistema: {snapshot.get('confianza_sistema')}/5
- Prejuicio detectado: {snapshot.get('nivel_prejuicio')}
- Bloqueos detectados: {', '.join(snapshot.get('bloqueos_detectados', []) or [])}
- Objetivo principal: {meta_label}
"""


def generar_radiografia_ia(diagnostico, snapshot):
    base = construir_radiografia_base(diagnostico, snapshot)
    if client is None:
        return base

    prompt = f"""
Sos un analista financiero senior. Reescribí esta radiografía para que sea más precisa, honesta y útil.

{_prompt_context(diagnostico, snapshot, snapshot.get('objetivo_principal'))}

BASE:
{base}

REGLAS:
- 3 párrafos
- Segunda persona
- Directo pero no agresivo
- Sin markdown ni títulos
- Conservá el sentido estratégico de la base y mejorá redacción, claridad y contundencia
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=650,
            temperature=0.5,
        )
        return response.choices[0].message.content.replace("**", "").replace("_", "")
    except Exception:
        return base


def generar_feedback_meta(meta, diagnostico, snapshot):
    base = construir_feedback_meta_base(meta, diagnostico, snapshot)
    if client is None:
        return base

    meta_info = METAS_MAP.get(meta, METAS_MAP["independencia_financiera"])
    prompt = f"""
Escribí un feedback corto y humano sobre la meta financiera del cliente.

{_prompt_context(diagnostico, snapshot, meta_info['label'])}

BASE:
{base}

REGLAS:
- 1 párrafo entre 90 y 140 palabras
- Sin markdown
- Debe unir emoción con realidad financiera
- No uses frases vacías de motivación
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=260,
            temperature=0.6,
        )
        return response.choices[0].message.content.replace("**", "").replace("_", "")
    except Exception:
        return base


def generar_acciones_inteligentes(meta, diagnostico, snapshot):
    base = construir_plan_guerra_base(meta, diagnostico, snapshot)
    if client is None:
        return base

    prompt = f"""
Generá un plan de guerra financiero en JSON válido.

{_prompt_context(diagnostico, snapshot, METAS_MAP.get(meta, METAS_MAP['independencia_financiera'])['label'])}

BASE:
{json.dumps(base, ensure_ascii=False)}

REGLAS:
- Respondé solo JSON
- Mantener claves corto_plazo, mediano_plazo y largo_plazo
- Cada item: una sola acción concreta, intensa y específica
- No recomendar inversiones sofisticadas si el flujo está roto
- Usar tono técnico y accionable
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=900,
            temperature=0.6,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content)
    except Exception:
        return base


def construir_resultado(perfil, diagnostico, permitir_ver=False):
    from calculadora.models import ResultadoIA
    from calculadora.services.motor_calculos import calcular_motor_financiero
    from calculadora.services.proyecciones import calcular_proyecciones

    snapshot = calcular_motor_financiero(diagnostico)
    proyecciones = calcular_proyecciones(perfil, snapshot)
    input_data = {
        **snapshot,
        "proyecciones": proyecciones,
        "objetivos": getattr(perfil, "objetivos", []),
        "objetivos_ordenados": getattr(diagnostico, "objetivos_ordenados", []),
        "sesgos_sistema": getattr(diagnostico, "sesgos_sistema", []),
    }
    input_hash = _hash_input(input_data)

    resultado_existente = ResultadoIA.objects.filter(
        usuario=perfil.user,
        input_hash=input_hash,
    ).first()
    if resultado_existente:
        if permitir_ver and resultado_existente.esta_bloqueado:
            resultado_existente.esta_bloqueado = False
            resultado_existente.save(update_fields=["esta_bloqueado"])
        return resultado_existente

    meta = obtener_meta_del_perfil(perfil, diagnostico)
    radiografia = generar_radiografia_ia(diagnostico, snapshot)
    meta_info = METAS_MAP.get(meta, METAS_MAP["independencia_financiera"]).copy()
    meta_info["feedback"] = generar_feedback_meta(meta, diagnostico, snapshot)
    meta_info["meta_key"] = meta
    meta_info["perfil_financiero"] = snapshot.get("perfil_financiero")
    meta_info["palanca_principal"] = snapshot.get("palanca_principal")
    meta_info["riesgo_principal"] = snapshot.get("riesgo_principal")
    meta_info["bloqueos_detectados"] = snapshot.get("bloqueos_detectados")

    acciones = generar_acciones_inteligentes(meta, diagnostico, snapshot)
    estructura = {
        "estado_general": snapshot.get("estado_general"),
        "perfil_financiero": snapshot.get("perfil_financiero"),
        "palanca_principal": snapshot.get("palanca_principal"),
        "riesgo_principal": snapshot.get("riesgo_principal"),
        "nivel_prejuicio": snapshot.get("nivel_prejuicio"),
        "conocimiento_financiero": snapshot.get("conocimiento_financiero"),
        "confianza_sistema": snapshot.get("confianza_sistema"),
    }

    resultado = ResultadoIA.objects.create(
        usuario=perfil.user,
        estado="completado",
        input_hash=input_hash,
        modelo_ia="gpt-4o-mini" if client else "deterministico+gpt-4o-mini",
        contenido="",
        bloque_diagnostico=radiografia,
        bloque_estructura=json.dumps(estructura, ensure_ascii=False),
        bloque_sesgo=json.dumps(meta_info, ensure_ascii=False),
        bloque_accion=json.dumps(acciones, ensure_ascii=False),
        proy_pos=list(proyecciones.get("positiva", [])),
        proy_med=list(proyecciones.get("media", [])),
        proy_neg=list(proyecciones.get("negativa", [])),
        esta_bloqueado=not permitir_ver,
    )
    return resultado
