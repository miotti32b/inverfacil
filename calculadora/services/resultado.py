# calculadora/services/resultado.py
"""
CORRECCIÓN FINAL: Rutas correctas para imágenes JPG
'imagen': '/static/metas/independencia_financiera.jpg',
                    ↑ /static/ al inicio
                                                   ↑ .jpg no .png
"""

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
        'imagen': '/static/metas/independencia_financiera.jpg',  # ✅ CORREGIDO
        'descripcion': 'Generar ingresos pasivos suficientes para cubrir tus gastos sin trabajar.',
    },
    'emprender': {
        'emoji': '🚀',
        'label': 'Emprender',
        'imagen': '/static/metas/emprender.jpg',  # ✅ CORREGIDO
        'descripcion': 'Crear tu propio negocio y ser tu jefe con completa libertad.',
    },
    'invertir_mas': {
        'emoji': '📈',
        'label': 'Aumentar Inversiones',
        'imagen': '/static/metas/invertir_mas.jpg',  # ✅ CORREGIDO
        'descripcion': 'Hacer crecer tu patrimonio a través de inversiones inteligentes.',
    },
    'comprar_vivienda': {
        'emoji': '🏠',
        'label': 'Comprar Vivienda',
        'imagen': '/static/metas/comprar_vivienda.jpg',  # ✅ CORREGIDO
        'descripcion': 'Tener tu propio hogar pagado y asegurado.',
    },
    'viajar': {
        'emoji': '🌍',
        'label': 'Viajar y Disfrutar',
        'imagen': '/static/metas/viajar.jpg',  # ✅ CORREGIDO
        'descripcion': 'Explorar el mundo y vivir experiencias inolvidables.',
    },
    'educacion': {
        'emoji': '🎓',
        'label': 'Educación y Formación',
        'imagen': '/static/metas/educacion.jpg',  # ✅ CORREGIDO
        'descripcion': 'Invertir en tu desarrollo personal y profesional continuo.',
    },
    'calidad_vida': {
        'emoji': '🧘',
        'label': 'Calidad de Vida',
        'imagen': '/static/metas/calidad_vida.jpg',  # ✅ CORREGIDO
        'descripcion': 'Trabajar menos y disfrutar más con tiempo para ti y tu familia.',
    },
    'ayudar': {
        'emoji': '❤️',
        'label': 'Ayudar a Otros',
        'imagen': '/static/metas/ayudar.jpg',  # ✅ CORREGIDO
        'descripcion': 'Impactar positivamente en la vida de otras personas.',
    },
}


# ========================
# FUNCIONES HELPER
# ========================

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
    
    prompt = f"""
Tu tarea: Genera una RADIOGRAFÍA FINANCIERA de 3 párrafos (sin asteriscos, sin markdown).

DATOS DEL CLIENTE:
- Ingresos mensuales: ${ingresos:,.0f}
- Gastos mensuales: ${gastos:,.0f}
- Ahorro mensual: ${ahorro:,.0f}
- Patrimonio: ${patrimonio:,.0f}
- Deuda total: ${deuda:,.0f}
- Margen de libertad: {ratio_libertad*100:.1f}%
- Dependencia de ingresos: {dependencia}

INSTRUCCIONES:
1. Párrafo 1 (Situación actual): Describe su estado financiero en 3-4 líneas. Menciona ingresos, gastos y ahorro.
2. Párrafo 2 (Fortalezas y debilidades): Identifica sus puntos fuertes y áreas de mejora. Sé específico con números.
3. Párrafo 3 (Recomendaciones): Sugiere 2-3 acciones concretas para mejorar su situación.

IMPORTANTE:
- NO USES ASTERISCOS (**) ni markdown
- Escribe en español claro y accesible
- Sé positivo pero realista
- Menciona los números del cliente
- Total: 3 párrafos bien estructurados

Genera ahora la radiografía:
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
Tu tarea: Genera un FEEDBACK personalizado sobre esta meta financiera.

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
1. Evalúa si el cliente está en buen camino hacia esta meta
2. Menciona su ahorro mensual y cómo impacta en la meta
3. Sugiere 1-2 acciones concretas para avanzar en esta meta
4. Sé motivador pero realista

IMPORTANTE:
- Máximo 4-5 líneas
- Menciona números reales del cliente
- Sé específico y accionable
- Sin markdown ni asteriscos

Genera el feedback ahora:
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
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
    
    if ingresos <= 0:
        ingresos = 1
    if gastos <= 0:
        gastos = 1
    
    prompt = f"""
Tu tarea: Genera un PLAN DE GUERRA financiero con acciones en 3 plazos.

SITUACIÓN DEL CLIENTE:
- Ingresos: ${ingresos:,.0f}/mes
- Gastos: ${gastos:,.0f}/mes
- Ahorro: ${ahorro:,.0f}/mes
- Deuda: ${deuda:,.0f}
- Dependencia: {dependencia}

INSTRUCCIONES:
Genera EXACTAMENTE este JSON (sin markdown, sin ```):

{{
  "corto_plazo": [
    "Acción 1 (próximas 2 semanas)",
    "Acción 2 (próximas 2 semanas)"
  ],
  "mediano_plazo": [
    "Acción 1 (próximos 3 meses)",
    "Acción 2 (próximos 3 meses)"
  ],
  "largo_plazo": [
    "Acción 1 (próximos 12 meses)",
    "Acción 2 (próximos 12 meses)"
  ]
}}

REGLAS:
- Cada acción debe ser específica y medible
- Basarse en los datos reales del cliente
- Ser realista y alcanzable
- Máximo 10 palabras por acción
- SIN ENUMERACIÓN (solo el texto)

Responde SOLO con el JSON válido, sin explicaciones adicionales:
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
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
    
    # Radiografía
    radiografia = generar_radiografia_ia(diagnostico, snapshot)
    
    # Meta
    meta = obtener_meta_del_perfil(perfil)
    meta_info = METAS_MAP.get(meta, METAS_MAP['independencia_financiera']).copy()
    
    # Feedback de la meta
    feedback = generar_feedback_meta(meta, diagnostico, snapshot)
    meta_info['feedback'] = feedback
    
    # Acciones
    acciones = generar_acciones_inteligentes(diagnostico, snapshot)
    
    # Proyecciones
    proy_pos, proy_med, proy_neg = calcular_proyecciones(diagnostico, snapshot)
    
    # Crear resultado
    resultado = ResultadoIA.objects.create(
        usuario=perfil.user,
        estado='completado',
        modelo_ia='gpt-4o-mini',
        contenido='',
        bloque_diagnostico=radiografia,
        bloque_sesgo=json.dumps(meta_info),
        bloque_accion=json.dumps(acciones),
        proy_pos=list(proy_pos),
        proy_med=list(proy_med),
        proy_neg=list(proy_neg),
    )
    
    return resultado