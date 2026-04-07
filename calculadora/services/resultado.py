# calculadora/services/resultado.py
"""
CORRECCIÓN FINAL: Rutas correctas para imágenes JPG
'imagen': '/static/metas/independencia_financiera.jpg',
                    ↑ /static/ al inicio
                                                   ↑ .jpg no .png
"""

import hashlib
import json
from decimal import Decimal
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ========================
# METAS MAP - RUTAS CORREGIDAS ✅
# ========================
METAS_MAP = {
    'independencia_financiera': {
        'emoji': '💸',
        'label': 'Independencia Financiera',
        'imagen': '/static/metas/if.png',  # ✅ CORREGIDO
        'descripcion': 'Generar ingresos pasivos suficientes para cubrir tus gastos sin trabajar.',
    },
    'emprender': {
        'emoji': '🚀',
        'label': 'Emprender',
        'imagen': '/static/metas/em.png',  # ✅ CORREGIDO
        'descripcion': 'Crear tu propio negocio y ser tu jefe con completa libertad.',
    },
    'invertir_mas': {
        'emoji': '📈',
        'label': 'Aumentar Inversiones',
        'imagen': '/static/metas/im.png',  # ✅ CORREGIDO
        'descripcion': 'Hacer crecer tu patrimonio a través de inversiones inteligentes.',
    },
    'comprar_vivienda': {
        'emoji': '🏠',
        'label': 'Comprar Vivienda',
        'imagen': '/static/metas/cc.png',  # ✅ CORREGIDO
        'descripcion': 'Tener tu propio hogar pagado y asegurado.',
    },
    'viajar': {
        'emoji': '🌍',
        'label': 'Viajar y Disfrutar',
        'imagen': '/static/metas/v.png',  # ✅ CORREGIDO
        'descripcion': 'Explorar el mundo y vivir experiencias inolvidables.',
    },
    'educacion': {
        'emoji': '🎓',
        'label': 'Educación y Formación',
        'imagen': '/static/metas/e.png',  # ✅ CORREGIDO
        'descripcion': 'Invertir en tu desarrollo personal y profesional continuo.',
    },
    'calidad_vida': {
        'emoji': '🧘',
        'label': 'Calidad de Vida',
        'imagen': '/static/metas/cv.png',  # ✅ CORREGIDO
        'descripcion': 'Trabajar menos y disfrutar más con tiempo para ti y tu familia.',
    },
    'ayudar': {
        'emoji': '❤️',
        'label': 'Ayudar a Otros',
        'imagen': '/static/metas/a.png',  # ✅ CORREGIDO
        'descripcion': 'Impactar positivamente en la vida de otras personas.',
    },
}


# ========================
# FUNCIONES HELPER
# ========================

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

def obtener_meta_del_perfil(perfil):
    """Obtiene la meta principal del perfil."""
    if perfil and hasattr(perfil, 'objetivos') and perfil.objetivos:
        return perfil.objetivos[0]
    return 'independencia_financiera'


def generar_radiografia_ia(diagnostico, snapshot):
    """
    Genera radiografía con IA usando gpt-4o-mini.
    Estructura: 3 párrafos sin asteriscos ni markdown.
    """
    ingresos = float(snapshot.get('ingresos', 0))
    gastos = float(snapshot.get('gastos', 0))
    ahorro = float(snapshot.get('ahorro', 0))
    patrimonio = float(snapshot.get('patrimonio', 0))
    deuda = float(snapshot.get('deuda', 0))
    ratio_libertad = float(snapshot.get('ratio_libertad', 0))
    dependencia = snapshot.get('dependencia_ingreso', 'alta')
    
    # Valores mínimos seguros
    if ingresos <= 0:
        ingresos = 1
    if gastos <= 0:
        gastos = 1
    if ahorro <= 0:
        ahorro = 0
    
    # Clasificar estadio para adaptar el tono
    en_crisis = ahorro <= 0 or gastos >= ingresos
    deuda_critica = deuda > 0 and ingresos > 0 and (deuda / ingresos) > 12
    puede_invertir = ahorro > 0 and not en_crisis and not deuda_critica

    if en_crisis:
        estadio_radio = "CRÍTICO: gastos igualan o superan ingresos. El análisis debe reflejar urgencia real, sin suavizar la situación."
    elif deuda_critica:
        estadio_radio = "ENDEUDADO: deuda alta en relación a ingresos. El análisis debe enfocarse en el peso de la deuda y cómo afecta la libertad financiera."
    elif not puede_invertir:
        estadio_radio = "ESTABILIZACIÓN: flujo positivo pero margen ajustado. El análisis debe destacar la oportunidad de consolidar."
    else:
        estadio_radio = "CRECIMIENTO: el cliente tiene capacidad de ahorro e inversión. El análisis puede ser más ambicioso."

    prompt = f"""
Sos un analista financiero senior. Escribí la radiografía financiera de este cliente: un diagnóstico honesto, técnico y directo. Tres párrafos, sin rodeos.

DATOS DEL CLIENTE:
- Ingresos mensuales: ${ingresos:,.0f}
- Gastos mensuales: ${gastos:,.0f}
- Ahorro mensual: ${ahorro:,.0f}
- Patrimonio: ${patrimonio:,.0f}
- Deuda total: ${deuda:,.0f}
- Margen de libertad: {ratio_libertad*100:.1f}%
- Dependencia de ingresos: {dependencia}

ESTADIO: {estadio_radio}

ESTRUCTURA:
Párrafo 1 — Diagnóstico actual: Describí su estado financiero real usando sus números. Nombrá el margen de libertad, la relación ingreso/gasto y qué implica. Sin eufemismos si la situación es mala.
Párrafo 2 — Fortalezas y vulnerabilidades: Identificá concretamente qué tiene a favor y qué lo expone. Usá sus datos (patrimonio, deuda, ahorro) para fundamentar.
Párrafo 3 — Diagnóstico de capacidad: Evaluá su capacidad real de acción financiera hoy: ¿puede ahorrar, invertir, o primero debe sanear? Sé directo con qué debe priorizar.

REGLAS:
- Tres párrafos separados por una línea en blanco
- Sin asteriscos, sin markdown, sin títulos
- Tono técnico y honesto, en segunda persona (vos)
- Mencioná números reales del cliente en cada párrafo

Generá la radiografía ahora:
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7,
        )
        radiografia = response.choices[0].message.content
        # Limpiar cualquier asterisco que haya
        radiografia = radiografia.replace('**', '').replace('_', '')
        return radiografia
    except Exception as e:
        return f"Error generando radiografía: {str(e)}"


def generar_feedback_meta(meta, diagnostico, snapshot):
    """
    Genera feedback personalizado para la meta usando IA.
    """
    ahorro = float(snapshot.get('ahorro', 0))
    ingresos = float(snapshot.get('ingresos', 0))
    gastos = float(snapshot.get('gastos', 0))
    patrimonio = float(snapshot.get('patrimonio', 0))
    deuda = float(snapshot.get('deuda', 0))
    ratio_libertad = float(snapshot.get('ratio_libertad', 0))
    
    # Valores mínimos
    if ahorro <= 0:
        ahorro = 0
    if ingresos <= 0:
        ingresos = 1
    if gastos <= 0:
        gastos = 1
    
    meta_info = METAS_MAP.get(meta, {})
    meta_label = meta_info.get('label', meta)
    meta_desc = meta_info.get('descripcion', '')
    
    prompt = f"""
Eres un asesor financiero empático y humano. Tu tarea es escribir un mensaje personal y motivador para alguien que sueña con "{meta_label}".

META: {meta_label}
DESCRIPCIÓN: {meta_desc}

DATOS DEL CLIENTE:
- Ahorro mensual: ${ahorro:,.0f}
- Ingresos: ${ingresos:,.0f}
- Gastos: ${gastos:,.0f}
- Patrimonio: ${patrimonio:,.0f}
- Deuda: ${deuda:,.0f}
- Margen de libertad: {ratio_libertad*100:.1f}%

INSTRUCCIONES:
1. Abrí con una frase que conecte emocionalmente con el sueño de esta persona (sin ser cursi). Hacela sentir que su meta tiene sentido.
2. Analizá su situación real con sus números concretos: ¿está cerca o lejos? ¿cuánto tiempo le llevaría con su ahorro actual?
3. Incluí un dato curioso o sorprendente relacionado con esta meta (puede ser estadístico, histórico o psicológico).
4. Cerrá con 1-2 acciones concretas mencionando sus números reales.

IMPORTANTE:
- Escribí en segunda persona (vos), tono cercano y humano
- Entre 6 y 8 líneas en total, sin saltos de línea dobles
- Sin markdown, sin asteriscos, sin títulos
- Que se sienta como un mensaje escrito para esta persona en particular, no un texto genérico

Generá el mensaje ahora:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=450,
            temperature=0.7,
        )
        feedback = response.choices[0].message.content
        feedback = feedback.replace('**', '').replace('_', '')
        return feedback
    except Exception as e:
        return f"Estás en buen camino hacia esta meta."


def generar_acciones_inteligentes(diagnostico, snapshot):
    """
    Genera acciones personalizadas en 3 plazos usando IA.
    Retorna JSON con estructura: {"corto_plazo": [...], "mediano_plazo": [...], "largo_plazo": [...]}
    """
    ingresos = float(snapshot.get('ingresos', 0))
    gastos = float(snapshot.get('gastos', 0))
    ahorro = float(snapshot.get('ahorro', 0))
    deuda = float(snapshot.get('deuda', 0))
    dependencia = snapshot.get('dependencia_ingreso', 'alta')
    ratio_libertad = float(snapshot.get('ratio_libertad', 0))

    if ingresos <= 0:
        ingresos = 1
    if gastos <= 0:
        gastos = 1

    meta = getattr(diagnostico, 'meta_financiera', '') or ''
    meta_info = METAS_MAP.get(meta, {})
    meta_label = meta_info.get('label', 'libertad financiera')

    # Clasificar estadio financiero para contextualizar el plan
    en_crisis = ahorro <= 0 or gastos >= ingresos
    deuda_critica = deuda > 0 and ingresos > 0 and (deuda / ingresos) > 12  # más de 12 meses de ingresos
    puede_invertir = ahorro > 0 and not en_crisis and not deuda_critica

    if en_crisis:
        estadio = "CRISIS: gastos igualan o superan ingresos, ahorro nulo o negativo. NO recomendar instrumentos de inversión todavía."
        foco = "El plan debe enfocarse en: recuperar flujo de caja positivo, reducir gastos críticos, generar ingresos adicionales (changas, freelance, venta de activos), negociar deudas y armar un colchón mínimo de emergencia."
    elif deuda_critica:
        estadio = "DEUDA ALTA: deuda supera 12 meses de ingresos. Inversión es secundaria."
        foco = "El plan debe enfocarse en: método avalanche o snowball para deudas, refinanciación, consolidación de deuda, y recuperar margen de ahorro antes de invertir."
    elif not puede_invertir:
        estadio = "ESTABILIZACIÓN: flujo positivo pero margen ajustado. Inversión mínima, fondo de emergencia primero."
        foco = "El plan debe enfocarse en: armar fondo de emergencia (3-6 meses de gastos), reducir deuda restante, y comenzar con instrumentos de muy bajo riesgo (FCI money market, plazo fijo)."
    else:
        estadio = "CRECIMIENTO: cliente con ahorro disponible, listo para construir patrimonio."
        foco = "El plan puede incluir instrumentos de inversión: CEDEARs, ETFs, ONs, acciones, DCA, cartera diversificada, cobertura cambiaria."

    prompt = f"""
Sos un asesor financiero senior. Creá el plan financiero personalizado de este cliente: un mapa de ejecución técnico, directo y sin rodeos, adaptado a su situación real.

PERFIL DEL CLIENTE:
- Ingresos: ${ingresos:,.0f}/mes
- Gastos: ${gastos:,.0f}/mes
- Ahorro mensual disponible: ${ahorro:,.0f}/mes
- Deuda total: ${deuda:,.0f}
- Margen de libertad: {ratio_libertad*100:.1f}%
- Dependencia de ingresos: {dependencia}
- Objetivo: {meta_label}

ESTADIO FINANCIERO: {estadio}
FOCO DEL PLAN: {foco}

INSTRUCCIONES:
Generá EXACTAMENTE este JSON (sin markdown, sin ```).
Adaptá cada instrucción al estadio financiero real. Si está en crisis, no recomendés CEDEARs — recomendá cómo salir de la crisis. Si puede invertir, sé técnico con activos específicos.

{{
  "corto_plazo": [
    "Instrucción técnica 1 para 0-3 meses, adaptada al estadio. Nombrá metodologías o instrumentos según corresponda. Máximo 55 palabras.",
    "Instrucción técnica 2 para 0-3 meses: sistema de control de flujo de caja o hábito clave. Específico con los números del cliente. Máximo 55 palabras."
  ],
  "mediano_plazo": [
    "Instrucción técnica 1 para 3-12 meses orientada a {meta_label}. Si puede invertir: activos y estrategia. Si no: consolidación y escalada de ingresos. Máximo 55 palabras.",
    "Instrucción técnica 2 para 3-12 meses: reducir dependencia o diversificar fuentes. Nombrá vehículos o métodos específicos. Máximo 55 palabras."
  ],
  "largo_plazo": [
    "Hoja de ruta 1-5 años hacia {meta_label}: estructura patrimonial objetivo según su estadio actual. Nombrá activos, estrategias o protecciones concretas. Máximo 55 palabras.",
    "Instrucción de largo plazo: protección patrimonial o apalancamiento. Cobertura cambiaria, estructura legal, o reinversión compuesta según corresponda. Máximo 55 palabras."
  ]
}}

REGLAS CRÍTICAS:
- Cada item es UN SOLO párrafo continuo, sin saltos de línea
- Adaptá el nivel de sofisticación al estadio del cliente
- Usá los números reales del cliente
- Tono técnico y determinado, sin frases motivacionales vacías
- Máximo 55 palabras por item
- SIN markdown, sin asteriscos, sin enumeración interna

Respondé SOLO con el JSON válido:
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=900,
            temperature=0.7,
        )
        json_str = response.choices[0].message.content.strip()
        # Limpiar si tiene markdown

        if json_str.startswith('```'):
            json_str = json_str.split('```')[1]
            if json_str.startswith('json'):
                json_str = json_str[4:]
        
        acciones = json.loads(json_str)
        return acciones
    except Exception as e:
        # Fallback
        return {
            "corto_plazo": [
                "Registra tus gastos diarios durante una semana",
                "Identifica 3 gastos innecesarios para reducir"
            ],
            "mediano_plazo": [
                "Implementa un presupuesto mensual detallado",
                "Comienza a separar el 10% de tu ahorro para inversión"
            ],
            "largo_plazo": [
                "Crea un fondo de emergencia de 3-6 meses de gastos",
                "Establece un plan de inversión a largo plazo"
            ]
        }


# ========================
# FUNCIÓN PRINCIPAL
# ========================

def construir_resultado(perfil, diagnostico, permitir_ver=False):
    """
    Construye un resultado financiero completo.
    
    Retorna un objeto ResultadoIA con:
    - bloque_diagnostico: radiografía
    - bloque_sesgo: metas (JSON)
    - bloque_accion: acciones (JSON)
    - proy_pos/med/neg: proyecciones
    """
    from calculadora.models import ResultadoIA
    from calculadora.services.motor_calculos import calcular_motor_financiero
    from calculadora.services.proyecciones import calcular_proyecciones
    
    # Calcular motor
    snapshot = calcular_motor_financiero(diagnostico)
    proyecciones = calcular_proyecciones(perfil, snapshot)
    input_data = {
        **snapshot,
        "proyecciones": proyecciones,
        "objetivos": getattr(perfil, "objetivos", []),
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
    
    # Radiografía
    radiografia = generar_radiografia_ia(diagnostico, snapshot)
    
    # Meta
    meta = obtener_meta_del_perfil(perfil)
    meta_info = METAS_MAP.get(meta, METAS_MAP['independencia_financiera']).copy()
    
    # Feedback de la meta
    feedback = generar_feedback_meta(meta, diagnostico, snapshot)
    meta_info['feedback'] = feedback
    meta_info['meta_key'] = meta
    
    # Acciones
    acciones = generar_acciones_inteligentes(diagnostico, snapshot)
    proy_pos = proyecciones.get("positiva", [])
    proy_med = proyecciones.get("media", [])
    proy_neg = proyecciones.get("negativa", [])
    
    # Crear resultado
    resultado = ResultadoIA.objects.create(
        usuario=perfil.user,
        estado='completado',
        input_hash=input_hash,
        modelo_ia='gpt-4o-mini',
        contenido='',
        bloque_diagnostico=radiografia,
        bloque_sesgo=json.dumps(meta_info, ensure_ascii=False),
        bloque_accion=json.dumps(acciones, ensure_ascii=False),
        proy_pos=list(proy_pos),
        proy_med=list(proy_med),
        proy_neg=list(proy_neg),
        esta_bloqueado=not permitir_ver,
    )
    
    return resultado
