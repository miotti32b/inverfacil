import json
import hashlib
from decimal import Decimal
from openai import OpenAI
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
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


def _resolver_url_estatica(path_relativo: str) -> str:
    try:
        return staticfiles_storage.url(path_relativo)
    except Exception:
        return f"{settings.STATIC_URL}{path_relativo}"

# ========================
# FUNCIÓN: GENERAR FEEDBACK INTELIGENTE (NO HARDCODEADO)
# ========================
def generar_feedback_meta(objetivo_principal, snapshot, perfil):
    """Genera feedback DINÁMICO basado en datos reales sin hardcodeo"""
    ahorro = float(snapshot.get('ahorro', 0))
    patrimonio = float(snapshot.get('patrimonio', 0))
    deuda = float(snapshot.get('deuda', 0))
    gastos = float(snapshot.get('gastos', 0))
    ingresos = float(snapshot.get('ingresos', 0))
    margen_libertad = float(snapshot.get('ratio_libertad', 0))
    
    # VALIDAR que los valores sean válidos (no 0 o negativos)
    if gastos <= 0:
        gastos = 1
    if ahorro <= 0:
        ahorro = 0.1
    if patrimonio <= 0:
        patrimonio = 1000
    if ingresos <= 0:
        ingresos = 1
    
    # Generar feedback DINÁMICO con IA en lugar de hardcodeado
    prompt = f"""Genera UN SOLO párrafo (máx 80 palabras) de feedback REALISTA y personalizado para alguien que:
- Meta principal: {objetivo_principal.replace('_', ' ')}
- Ahorra: ${ahorro:,.0f}/mes
- Patrimonio: ${patrimonio:,.0f}
- Deuda: ${deuda:,.0f}
- Gasta: ${gastos:,.0f}/mes
- Ingresos: ${ingresos:,.0f}/mes
- Margen libertad: {margen_libertad*100:.1f}%

El feedback debe:
1. Ser específico a sus NÚMEROS (usa los valores exactos)
2. Ser motivador pero honesto
3. Dar UN consejo práctico y tangible
4. NO ser generic - debe reflejar su situación única

Responde SOLO con el párrafo, sin explicaciones."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except:
        # Fallback si falla la IA
        return f"Tu meta es alcanzable. Con tu ahorro actual de ${ahorro:,.0f}/mes, necesitas un plan disciplinado. Comienza hoy."

# ========================
# MAPEO DE METAS CON RUTAS LOCALES Y DESCRIPCIÓN
# ========================
METAS_MAP = {
    'independencia_financiera': {
        'emoji': '💸',
        'label': 'Independencia Financiera',
        'imagen': 'metas/independencia_financiera.png',
        'descripcion': 'Generar ingresos pasivos suficientes para cubrir tus gastos sin trabajar.',
    },
    'emprender': {
        'emoji': '🚀',
        'label': 'Emprender',
        'imagen': 'metas/emprender.png',
        'descripcion': 'Crear tu propio negocio y ser tu jefe con completa libertad.',
    },
    'invertir_mas': {
        'emoji': '📈',
        'label': 'Aumentar Inversiones',
        'imagen': 'metas/invertir_mas.png',
        'descripcion': 'Hacer crecer tu patrimonio a través de inversiones inteligentes.',
    },
    'comprar_vivienda': {
        'emoji': '🏠',
        'label': 'Comprar Vivienda',
        'imagen': 'metas/comprar_vivienda.png',
        'descripcion': 'Tener tu propio hogar pagado sin deuda hipotecaria.',
    },
    'viajar': {
        'emoji': '🌍',
        'label': 'Viajar y Disfrutar',
        'imagen': 'metas/viajar.png',
        'descripcion': 'Explorar el mundo con libertad y sin preocupaciones financieras.',
    },
    'educacion': {
        'emoji': '🎓',
        'label': 'Educación y Formación',
        'imagen': 'metas/educacion.png',
        'descripcion': 'Invertir en tu desarrollo personal y profesional continuo.',
    },
    'calidad_vida': {
        'emoji': '🧘',
        'label': 'Calidad de Vida',
        'imagen': 'metas/calidad_vida.png',
        'descripcion': 'Trabajar menos, disfrutar más y tener tiempo para lo importante.',
    },
    'ayudar': {
        'emoji': '❤️',
        'label': 'Ayudar a Otros',
        'imagen': 'metas/ayudar.png',
        'descripcion': 'Tener los recursos para impactar positivamente en otras personas.',
    },
}

def generar_acciones_inteligentes(snapshot, perfil):
    """Genera acciones con IA basadas en datos reales"""
    gastos = float(snapshot.get('gastos', 0)) or 1
    ahorro = float(snapshot.get('ahorro', 0)) or 0.1
    patrimonio = float(snapshot.get('patrimonio', 0)) or 1000
    deuda = float(snapshot.get('deuda', 0)) or 0
    
    horas_esclavas = float(snapshot.get('horas_esclavas', 0)) or 0
    margen_libertad = float(snapshot.get('ratio_libertad', 0)) or 0
    deuda_toxica_pct = float(snapshot.get('porcentaje_deuda_toxica', 0)) or 0
    
    ingreso_negocio = float(snapshot.get('ingreso_negocio', 0)) or 0
    ingreso_trabajo = float(snapshot.get('ingreso_trabajo', 0)) or 0
    ingresos = float(snapshot.get('ingresos', 0)) or 1
    
    acciones = {"corto_plazo": [], "mediano_plazo": [], "largo_plazo": []}
    
    # Generar acciones CON IA en lugar de hardcodeadas
    prompt = f"""Genera 7 acciones financieras específicas y concretas (2 CORTO, 2 MEDIANO, 3 LARGO plazo).

Situación:
- Gastos: ${gastos:,.0f}/mes
- Ahorro: ${ahorro:,.0f}/mes
- Patrimonio: ${patrimonio:,.0f}
- Deuda: ${deuda:,.0f}
- Horas trabajo: {horas_esclavas:.0f}/mes
- Margen libertad: {margen_libertad*100:.1f}%
- Ingresos negocio: ${ingreso_negocio:,.0f}/mes

Formato EXACTO (o el sistema fallará):
{{"corto_plazo": ["acción 1", "acción 2"], "mediano_plazo": ["acción 1", "acción 2"], "largo_plazo": ["acción 1", "acción 2", "acción 3"]}}

Cada acción DEBE:
1. Ser ESPECÍFICA con números
2. Ser REALISTA para su situación
3. Tener plazo claro
4. Ser ACCIONABLE inmediatamente

SOLO JSON, sin explicaciones."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        json_str = response.choices[0].message.content.strip()
        # Limpiar markdown si viene envuelto
        if json_str.startswith('```'):
            json_str = json_str.split('```')[1].replace('json\n', '').strip()
        acciones = json.loads(json_str)
    except Exception as e:
        # Fallback con acciones básicas
        acciones = {
            "corto_plazo": [
                f"Audita tus gastos esta semana: categoriza cada peso de los ${gastos:,.0f}/mes",
                f"Abre una cuenta de ahorro fijo al 5%+ para tu fondo de emergencia"
            ],
            "mediano_plazo": [
                f"Invierte ${ahorro*0.7:,.0f}/mes en índices diversificados (VOO, VTI)",
                f"Negocia reducción de deuda tóxica si la hay ({deuda_toxica_pct:.0f}%)"
            ],
            "largo_plazo": [
                f"Construye portafolio diversificado: 50% renta fija, 30% acciones, 20% alternativas",
                f"Genera ingresos pasivos: objetivo ${gastos:,.0f}/mes en pasivos en 10 años",
                f"Aumenta patrimonio de ${patrimonio:,.0f} a ${patrimonio*3:,.0f}"
            ]
        }
    
    return acciones

def generar_radiografia_ia(diagnostico_financiero, snapshot):
    """Genera radiografía ejecutiva con IA."""
    age = getattr(diagnostico_financiero.cliente if diagnostico_financiero else None, 'edad', 0)
    
    prompt = f"""Radiografía financiera EJECUTIVA en 3 párrafos (max 90 palabras cada).

Edad: {age}
Ingresos: ${float(snapshot.get('ingresos', 0)):,.0f}/mes
Gastos: ${float(snapshot.get('gastos', 0)):,.0f}/mes
Ahorro: ${float(snapshot.get('ahorro', 0)):,.0f}/mes
Margen libertad: {float(snapshot.get('ratio_libertad', 0))*100:.0f}%
Patrimonio: ${float(snapshot.get('patrimonio', 0)):,.0f}

PÁRRAFO 1: Situación actual (donde estás hoy)
PÁRRAFO 2: Dinámicas ocultas (qué está fallando)
PÁRRAFO 3: Potencial (qué podría cambiar en 12 meses)

MUY IMPORTANTE: NO USES ASTERISCOS (**) NI MARKDOWN. SOLO TEXTO PLANO.
Tono: directo, seco, sin esperanza falsa. Genera URGENCIA."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        radiografia = response.choices[0].message.content
        # Limpiar asteriscos si los hay
        radiografia = radiografia.replace('**', '').replace('_', '')
        return radiografia
    except:
        return "Radiografía no disponible"

def construir_resultado(perfil, diagnostico_financiero, permitir_ver=False):
    """Construye el resultado IA completo con metas, acciones y proyecciones."""
    snapshot = calcular_motor_financiero(diagnostico_financiero)
    proy = calcular_proyecciones(perfil, snapshot)
    snapshot_safe = _to_json_safe(snapshot)
    proy_safe = _to_json_safe(proy)

    input_data = {**snapshot, "proyecciones": proy, "objetivos": getattr(perfil, 'objetivos', '')}
    input_hash = _hash_input(input_data)

    resultado_existente = ResultadoIA.objects.filter(usuario=perfil.user, input_hash=input_hash).first()
 
    if resultado_existente:
        tiene_metas = resultado_existente.bloque_sesgo and len(resultado_existente.bloque_sesgo) > 5
        tiene_acciones = resultado_existente.bloque_accion and len(resultado_existente.bloque_accion) > 5
        tiene_proyecciones = resultado_existente.proy_pos and len(resultado_existente.proy_pos) > 0
        
        if not (tiene_metas and tiene_acciones and tiene_proyecciones):
            print(f"[REPARANDO] Resultado incompleto. Regenerando...")
            resultado_existente.delete()
            resultado_existente = None
        else:
            if permitir_ver and resultado_existente.esta_bloqueado:
                resultado_existente.esta_bloqueado = False
                resultado_existente.save(update_fields=["esta_bloqueado"])
            return resultado_existente

    try:
        # 1. GENERAR CONTENIDO
        radiografia = generar_radiografia_ia(diagnostico_financiero, snapshot)
        acciones = generar_acciones_inteligentes(snapshot, perfil)
        
        # 2. GENERAR METAS CON FEEDBACK DINÁMICO
        objetivos = getattr(perfil, 'objetivos', [])
        objetivo_principal = objetivos[0] if objetivos else 'independencia_financiera'
        meta_info = METAS_MAP.get(objetivo_principal, METAS_MAP['independencia_financiera']).copy()
        meta_info['imagen'] = _resolver_url_estatica(meta_info['imagen'])
        
        # 🔴 AGREGAR FEEDBACK DINÁMICO (NO HARDCODEADO)
        feedback_personalizado = generar_feedback_meta(objetivo_principal, snapshot, perfil)
        meta_info['feedback'] = feedback_personalizado
        
        # 3. SERIALIZAR TODO
        bloque_metas = json.dumps(meta_info, ensure_ascii=False)
        bloque_acciones = json.dumps(acciones, ensure_ascii=False)
        
        contenido = f"RADIOGRAFÍA\n{radiografia}\n\nPLAN DE GUERRA\n{json.dumps(acciones, indent=2, ensure_ascii=False)}"
        
        # 4. GUARDAR EN BD
        resultado = ResultadoIA.objects.create(
            usuario=perfil.user,
            input_hash=input_hash,
            contenido=contenido,
            bloque_diagnostico=radiografia,
            bloque_proyeccion="",
            bloque_sesgo=bloque_metas,
            bloque_accion=bloque_acciones,
            proy_pos=proy_safe.get("positiva", []),
            proy_med=proy_safe.get("media", []),
            proy_neg=proy_safe.get("negativa", []),
            modelo_ia="gpt-4o-mini",
            tokens_usados=0,
            costo_estimado_usd=0,
            estado="ok",
            esta_bloqueado=not permitir_ver,
        )
        
        return resultado
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return ResultadoIA.objects.create(
            usuario=perfil.user,
            input_hash=input_hash,
            contenido="Error",
            modelo_ia="gpt-4o-mini",
            tokens_usados=0,
            costo_estimado_usd=0,
            estado="error",
            error_msg=str(e),
            esta_bloqueado=True,
        )
