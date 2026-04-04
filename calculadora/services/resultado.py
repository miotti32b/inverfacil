import json
import hashlib
from decimal import Decimal
from openai import OpenAI
from django.conf import settings
from calculadora.models import ResultadoIA
from calculadora.services.motor_calculos import calcular_motor_financiero
from calculadora.services.proyecciones import calcular_proyecciones

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

# ========================
# MAPEO DE METAS
# ========================
METAS_MAP = {
    'independencia_financiera': {
        'emoji': '💸',
        'label': 'Independencia Financiera',
        'imagen': '/static/metas/independencia_financiera.png'
    },
    'emprender': {
        'emoji': '🚀',
        'label': 'Emprender',
        'imagen': '/static/metas/emprender.png'
    },
    'invertir_mas': {
        'emoji': '📈',
        'label': 'Aumentar Inversiones',
        'imagen': '/static/metas/invertir_mas.png'
    },
    'comprar_vivienda': {
        'emoji': '🏠',
        'label': 'Comprar Vivienda',
        'imagen': '/static/metas/comprar_vivienda.png'
    },
    'viajar': {
        'emoji': '🌍',
        'label': 'Viajar y Disfrutar',
        'imagen': '/static/metas/viajar.png'
    },
    'educacion': {
        'emoji': '🎓',
        'label': 'Educación y Formación',
        'imagen': '/static/metas/educacion.png'
    },
    'calidad_vida': {
        'emoji': '🧘‍♂️',
        'label': 'Calidad de Vida',
        'imagen': '/static/metas/calidad_vida.png'
    },
    'ayudar': {
        'emoji': '❤️',
        'label': 'Ayudar a Otros',
        'imagen': '/static/metas/ayudar.png'
    },
}

def analizar_perfil_estrategico(diagnostico_financiero, snapshot):
    ingresos_total = float(snapshot.get('ingresos') or 0)
    ingreso_trabajo = float(diagnostico_financiero.ingreso_trabajo or 0) if diagnostico_financiero else 0
    ingreso_negocio = float(diagnostico_financiero.ingreso_negocio or 0) if diagnostico_financiero else 0
    ingreso_rentas = float(diagnostico_financiero.ingreso_rentas or 0) if diagnostico_financiero else 0
    ingreso_inversiones = float(diagnostico_financiero.ingreso_inversiones or 0) if diagnostico_financiero else 0
    
    peso_trabajo = (ingreso_trabajo / ingresos_total * 100) if ingresos_total > 0 else 0
    peso_negocio = (ingreso_negocio / ingresos_total * 100) if ingresos_total > 0 else 0
    peso_pasivo = ((ingreso_rentas + ingreso_inversiones) / ingresos_total * 100) if ingresos_total > 0 else 0
    
    es_emprendedor = peso_negocio > 40
    
    patrimonio_total = float(snapshot.get('patrimonio') or 0)
    patrimonio_comp = getattr(diagnostico_financiero, "patrimonio_comp", {}) or {}
    pat_inmuebles = float(patrimonio_comp.get("pat_inmuebles", 0) or 0)
    pat_empresa = float(patrimonio_comp.get("pat_empresa", 0) or 0)
    pat_cash = float(patrimonio_comp.get("pat_cash", 0) or 0)
    pat_inversiones = float(patrimonio_comp.get("pat_inversiones", 0) or 0)
    
    porcentaje_inmuebles = (pat_inmuebles / patrimonio_total * 100) if patrimonio_total > 0 else 0
    porcentaje_empresa = (pat_empresa / patrimonio_total * 100) if patrimonio_total > 0 else 0
    porcentaje_liquidez = ((pat_cash + pat_inversiones) / patrimonio_total * 100) if patrimonio_total > 0 else 0
    
    hay_trampa_inmueble = (porcentaje_inmuebles > 80 and float(snapshot.get('ratio_libertad') or 0) < 0.15)
    hay_trampa_empresa = (porcentaje_empresa > 60 and es_emprendedor and pat_empresa > 0)
    falta_liquidez = (porcentaje_liquidez < 10 and patrimonio_total > 0)
    
    nivel_alarma = "OK"
    if hay_trampa_inmueble or hay_trampa_empresa:
        nivel_alarma = "CRÍTICO"
    
    return {
        "es_emprendedor": es_emprendedor,
        "peso_trabajo": peso_trabajo,
        "peso_negocio": peso_negocio,
        "peso_pasivo": peso_pasivo,
        "porcentaje_inmuebles": porcentaje_inmuebles,
        "porcentaje_empresa": porcentaje_empresa,
        "porcentaje_liquidez": porcentaje_liquidez,
        "hay_trampa_inmueble": hay_trampa_inmueble,
        "hay_trampa_empresa": hay_trampa_empresa,
        "falta_liquidez": falta_liquidez,
        "nivel_alarma": nivel_alarma,
    }

def generar_acciones_personalizadas(contexto, analisis):
    snapshot = contexto["snapshot"]
    diagnostico_financiero = contexto.get("diagnostico_financiero")
    perfil = contexto["perfil"]
    
    ingresos = float(snapshot.get('ingresos') or 0)
    gastos = float(snapshot.get('gastos') or 0)
    ahorro = float(snapshot.get('ahorro') or 0)
    patrimonio = float(snapshot.get('patrimonio') or 0)
    deuda = float(snapshot.get('deuda') or 0)
    
    ingreso_trabajo = float(snapshot.get('ingreso_trabajo') or 0)
    ingreso_negocio = float(snapshot.get('ingreso_negocio') or 0)
    ingreso_rentas = float(snapshot.get('ingreso_rentas') or 0)
    ingreso_inversiones = float(snapshot.get('ingreso_inversiones') or 0)
    
    pat_inmuebles = float(snapshot.get('pat_inmuebles') or 0)
    pat_empresa = float(snapshot.get('pat_empresa') or 0)
    pat_cash = float(snapshot.get('pat_cash') or 0)
    
    horas_esclavas = float(snapshot.get('horas_esclavas') or 0)
    margen_libertad = float(snapshot.get('ratio_libertad') or 0)
    deuda_toxica = float(snapshot.get('porcentaje_deuda_toxica') or 0)
    
    acciones = {"corto_plazo": [], "mediano_plazo": [], "largo_plazo": []}
    
    if analisis["hay_trampa_inmueble"]:
        acciones["corto_plazo"].append(f"Evaluar venta parcial de inmueble: tienes ${pat_inmuebles:,.0f} inmovilizado. Vender 30-50% para descongelar capital.")
    
    if deuda_toxica > 30:
        acciones["corto_plazo"].append(f"Plan de extinción de deuda tóxica: ${deuda*deuda_toxica/100:,.0f}. Destiná 50% de tu ahorro a eliminarla.")
    
    if horas_esclavas > 200:
        acciones["corto_plazo"].append(f"Urgencia: trabajas {horas_esclavas:.0f} horas/mes. Pausa inversiones, crea margen.")
    
    if not acciones["corto_plazo"]:
        acciones["corto_plazo"].append(f"Crear fondo de emergencia: ${gastos*3:,.0f} - ${gastos*6:,.0f}.")
    
    if analisis["es_emprendedor"]:
        acciones["mediano_plazo"].append(f"Tu negocio (${ingreso_negocio:,.0f}/mes) es tu mejor activo. Reinvierte.")
        acciones["mediano_plazo"].append(f"Diversifica: fondos indexados, bonos, inmuebles rentables como blindaje.")
    else:
        acciones["mediano_plazo"].append(f"Sueldo (${ingresos:,.0f}/mes). Diversifica: 60% CEDEARs, 30% ONs, 10% alternativas.")
    
    if analisis["hay_trampa_empresa"]:
        acciones["mediano_plazo"].append(f"Empresa {analisis['porcentaje_empresa']:.0f}% patrimonio. Diversifica.")
    
    if margen_libertad < 0.1:
        acciones["mediano_plazo"].append(f"Margen de libertad {margen_libertad*100:.0f}%. Meta: 20-30%.")
    
    objetivos = getattr(perfil, 'objetivos', [])
    objetivo_principal = objetivos[0] if objetivos else 'desconocido'
    
    if objetivo_principal == 'independencia_financiera':
        acciones["largo_plazo"].append(f"Independencia: necesitas ${gastos:,.0f}/mes pasivos.")
    elif objetivo_principal == 'emprender':
        acciones["largo_plazo"].append(f"Emprender: escala sin ser cuello de botella.")
    elif objetivo_principal == 'invertir_mas':
        acciones["largo_plazo"].append(f"Invertir: diversificación geográfica. Compounding 7-10%.")
    elif objetivo_principal == 'comprar_vivienda':
        acciones["largo_plazo"].append(f"Vivienda: ahorra ${gastos*12:,.0f}/año para entrada.")
    elif objetivo_principal == 'viajar':
        acciones["largo_plazo"].append(f"Viajes: crea fondo de $500-1000/mes para experiencias.")
    else:
        acciones["largo_plazo"].append(f"Objetivo: {objetivo_principal}. Estructura con asesor.")
    
    acciones["largo_plazo"].append(f"Revisión anual: rebalanceo, impuestos, inflación.")
    
    return acciones

def generar_respuesta_ia_unica(contexto):
    try:
        perfil = contexto["perfil"]
        snapshot = contexto["snapshot"]
        proy = contexto["proyecciones"]
        diagnostico_financiero = contexto.get("diagnostico_financiero")

        analisis_estrategico = analizar_perfil_estrategico(diagnostico_financiero, snapshot)
        acciones = generar_acciones_personalizadas(contexto, analisis_estrategico)

        edad = getattr(perfil, 'edad', 0)
        ingresos = snapshot.get('ingresos', 0)
        gastos = snapshot.get('gastos', 0)
        ahorro = snapshot.get('ahorro', 0)
        margen_libertad = float(snapshot.get("ratio_libertad") or 0) * 100

        acciones_corto = "\n".join([f"→ {a}" for a in acciones.get('corto_plazo', [])])
        acciones_mediano = "\n".join([f"→ {a}" for a in acciones.get('mediano_plazo', [])])
        acciones_largo = "\n".join([f"→ {a}" for a in acciones.get('largo_plazo', [])])

        # BLOQUE 1: RADIOGRAFÍA (ejecutivo)
        prompt_radiografia = f"""Hacé una radiografía financiera EJECUTIVA en 3 párrafos (max 100 palabras cada uno).

DATOS:
- Edad: {edad}
- Ingresos: ${ingresos:,.0f}/mes
- Gastos: ${gastos:,.0f}/mes
- Ahorro: ${ahorro:,.0f}/mes
- Margen de libertad: {margen_libertad:.0f}%
- Tipo: {("EMPRENDEDOR" if analisis_estrategico["es_emprendedor"] else "ASALARIADO")}
- Alarma: {analisis_estrategico['nivel_alarma']}

PÁRRAFO 1: Situación actual (¿dónde está hoy?)
PÁRRAFO 2: Dinámicas ocultas (¿qué está fallando?)
PÁRRAFO 3: Potencial (¿qué podría cambiar?)

Tono: directo, seco, profesional. Genera urgencia de cambio."""

        response1 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sos un asesor financiero. Responde SOLO con el análisis, sin JSON."},
                {"role": "user", "content": prompt_radiografia}
            ],
            temperature=0.7,
        )
        radiografia = response1.choices[0].message.content

        # BLOQUE 2: PROYECCIÓN AMPLIADA
        proy_10 = proy.get("media", [])[-1] if proy.get("media") else 0
        prompt_proyeccion = f"""Explicá QUÉ IMPLICA seguir igual vs corregir EN 10 AÑOS.

Patrimonios proyectados:
- Hoy: ${snapshot.get('patrimonio'):,.0f}
- En 10 años: ${proy_10:,.0f}

Hablá de: libertad, margen de error, desgaste mental, impacto real.

Máximo 120 palabras. Tono: crudo, realista, sin esperanza falsa."""

        response2 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sos un asesor financiero. Responde SOLO con el análisis."},
                {"role": "user", "content": prompt_proyeccion}
            ],
            temperature=0.7,
        )
        proyeccion = response2.choices[0].message.content

        # BLOQUE 3: FEEDBACK SOBRE METAS
        objetivos = getattr(perfil, 'objetivos', [])
        objetivo_principal = objetivos[0] if objetivos else 'independencia_financiera'
        meta_info = METAS_MAP.get(objetivo_principal, METAS_MAP['independencia_financiera'])
        
        prompt_metas = f"""Feedback sobre la meta: {meta_info['label']}.

Contexto: {analisis_estrategico['nivel_alarma']} - Margen de libertad {margen_libertad:.0f}%

Escribe 2-3 frases que dejen ASOMBRADO al usuario sobre su potencial para lograr esta meta.
Tono: inspirador pero realista. Máximo 80 palabras."""

        response3 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sos un asesor financiero inspirador."},
                {"role": "user", "content": prompt_metas}
            ],
            temperature=0.7,
        )
        feedback_metas = response3.choices[0].message.content

        return {
            "estado": "ok",
            "data": {
                "bloque_radiografia": radiografia,
                "bloque_proyeccion": proyeccion,
                "bloque_metas": {
                    "objetivo": objetivo_principal,
                    "label": meta_info['label'],
                    "emoji": meta_info['emoji'],
                    "imagen": meta_info['imagen'],
                    "feedback": feedback_metas
                },
                "bloque_accion": acciones,
            },
            "tokens": response1.usage.total_tokens + response2.usage.total_tokens + response3.usage.total_tokens,
        }

    except Exception as e:
        return {"estado": "error", "error_msg": str(e), "data": None, "tokens": 0}

def construir_resultado(perfil, diagnostico_financiero, permitir_ver=False):
    snapshot = calcular_motor_financiero(diagnostico_financiero)
    proy = calcular_proyecciones(perfil, snapshot)
    snapshot_safe = _to_json_safe(snapshot)
    proy_safe = _to_json_safe(proy)

    input_data = {**snapshot, "proyecciones": proy, "objetivos": getattr(perfil, 'objetivos', '')}
    input_hash = _hash_input(input_data)

    resultado_existente = ResultadoIA.objects.filter(usuario=perfil.user, input_hash=input_hash).first()

    if resultado_existente:
        if permitir_ver and resultado_existente.esta_bloqueado:
            resultado_existente.esta_bloqueado = False
            resultado_existente.save(update_fields=["esta_bloqueado"])
        return resultado_existente

    contexto = {"perfil": perfil, "diagnostico_financiero": diagnostico_financiero, "snapshot": snapshot_safe, "proyecciones": proy_safe}

    respuesta = generar_respuesta_ia_unica(contexto)

    if respuesta["estado"] == "error":
        return ResultadoIA.objects.create(
            usuario=perfil.user, input_hash=input_hash, contenido="Error", modelo_ia="gpt-4o-mini",
            tokens_usados=0, costo_estimado_usd=0, estado="error", error_msg=respuesta["error_msg"], esta_bloqueado=True,
        )

    data = respuesta["data"]
    
    # Serializar JSON para campos de texto
    bloque_radiografia = str(data.get("bloque_radiografia", ""))
    bloque_proyeccion = str(data.get("bloque_proyeccion", ""))
    bloque_metas_json = json.dumps(data.get("bloque_metas", {}))
    bloque_accion_json = json.dumps(data.get("bloque_accion", {}))

    contenido = "\n\n".join([
        "RADIOGRAFÍA\n" + bloque_radiografia,
        "PROYECCIÓN\n" + bloque_proyeccion,
        "METAS\n" + str(data.get("bloque_metas", {})),
        "ACCIONES\n" + str(data.get("bloque_accion", {})),
    ])

    resultado = ResultadoIA.objects.create(
        usuario=perfil.user,
        input_hash=input_hash,
        contenido=contenido,
        bloque_diagnostico=bloque_radiografia,
        bloque_proyeccion=bloque_proyeccion,
        bloque_sesgo=bloque_metas_json,
        bloque_accion=bloque_accion_json,
        proy_pos=proy_safe.get("positiva", []),
        proy_med=proy_safe.get("media", []),
        proy_neg=proy_safe.get("negativa", []),
        modelo_ia="gpt-4o-mini",
        tokens_usados=respuesta.get("tokens", 0),
        costo_estimado_usd=respuesta.get("tokens", 0) * 0.00000015,
        estado="ok",
        esta_bloqueado=not permitir_ver,
    )

    return resultado