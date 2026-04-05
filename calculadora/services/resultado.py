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
# MAPEO DE METAS CON FEEDBACK PERSONALIZADO
# ========================
def generar_feedback_meta(objetivo_principal, snapshot, perfil):
    """Genera feedback personalizado para cada meta"""
    ahorro = float(snapshot.get('ahorro', 0))
    patrimonio = float(snapshot.get('patrimonio', 0))
    deuda = float(snapshot.get('deuda', 0))
    gastos = float(snapshot.get('gastos', 0))
    ingresos = float(snapshot.get('ingresos', 0))
    margen_libertad = float(snapshot.get('ratio_libertad', 0))
    
    feedbacks = {
        'independencia_financiera': f"Necesitas ${gastos:,.0f}/mes en ingresos pasivos. Con tu ahorro actual (${ahorro:,.0f}/mes) alcanzarías la independencia en {max(1, int((gastos * 12) / ahorro / 12))} años si inviertes al 8% anual. ¡Es posible!",
        
        'emprender': f"Tienes un margen de libertad del {margen_libertad*100:.0f}%. Para emprender con seguridad necesitas 6-12 meses de gastos ahorrados. Actualmente tienes ${patrimonio:,.0f}. Objetivo: ${gastos * 9:,.0f} en fondo de emergencia.",
        
        'invertir_mas': f"Tu capacidad actual de ahorro es ${ahorro:,.0f}/mes. Para invertir más: 1) Reduce gastos en 10% (${gastos*0.1:,.0f}), 2) Aumenta ingresos 15%, 3) Diversifica en índices. Meta: invertir ${ahorro*1.5:,.0f}/mes.",
        
        'comprar_vivienda': f"Necesitas un inicial del 20% para casa de $200k = $40k. A tu ritmo de ahorro (${ahorro:,.0f}/mes) lo logras en {int(40000/ahorro)} meses. ¡Menos de {int(40000/ahorro/12)} años!",
        
        'viajar': f"Fondo viajes recomendado: ${gastos*6:,.0f} (6 meses de gastos). Con 10% de tu ahorro (${ahorro*0.1:,.0f}/mes) lo logras en {int((gastos*6)/(ahorro*0.1))} meses. ¡Planifica ya!",
        
        'educacion': f"Inversión en educación > inversión en cualquier otra cosa. Tu ROI será ${ahorro*1.5:,.0f}/mes en 5 años. Destina 15% de ahorro (${ahorro*0.15:,.0f}/mes) a tu formación.",
        
        'calidad_vida': f"La calidad de vida no es lujo, es urgencia. Con margen de {margen_libertad*100:.0f}%, necesitas mejorar. Plan: 1) Reduce horas esclavas, 2) Automatiza tareas, 3) Vive cerca del trabajo. Tu tiempo = dinero infinito.",
        
        'ayudar': f"Filantropía inteligente: destina 5% de ahorro (${ahorro*0.05:,.0f}/mes) a causas que ames. En 10 años habrás dado ${ahorro*0.05*120:,.0f}. ¡Genera impacto sin sacrificar tu libertad financiera!",
    }
    
    return feedbacks.get(objetivo_principal, "Tu meta es importante. Construyamos un plan personalizado para lograrla.")

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

def generar_acciones_personalizadas(snapshot, perfil):
    """Genera ACCIONES REALES basadas en los datos del usuario."""
    gastos = float(snapshot.get('gastos', 0))
    ahorro = float(snapshot.get('ahorro', 0))
    patrimonio = float(snapshot.get('patrimonio', 0))
    deuda = float(snapshot.get('deuda', 0))
    
    horas_esclavas = float(snapshot.get('horas_esclavas', 0))
    margen_libertad = float(snapshot.get('ratio_libertad', 0))
    deuda_toxica_pct = float(snapshot.get('porcentaje_deuda_toxica', 0))
    
    ingreso_negocio = float(snapshot.get('ingreso_negocio', 0))
    ingreso_trabajo = float(snapshot.get('ingreso_trabajo', 0))
    ingresos = float(snapshot.get('ingresos', 0))
    
    pat_inmuebles = float(snapshot.get('pat_inmuebles', 0))
    porcentaje_inmuebles = float(snapshot.get('porcentaje_inmuebles', 0))
    
    acciones = {"corto_plazo": [], "mediano_plazo": [], "largo_plazo": []}
    
    # ========================
    # CORTO PLAZO (0-3 meses)
    # ========================
    if horas_esclavas > 200:
        acciones["corto_plazo"].append(
            f"⏰ URGENCIA: Trabajas {horas_esclavas:.0f} hs/mes. Plan: 1) Negocia reducción 4hs/semana, "
            f"2) Delega o automatiza 3 tareas, 3) Busca cliente más rentable. Meta: 180 hs/mes en 30 días."
        )
    
    deuda_toxica_monto = deuda * (deuda_toxica_pct / 100) if deuda > 0 else 0
    if deuda_toxica_pct > 30:
        acciones["corto_plazo"].append(
            f"💳 DEUDA TÓXICA: ${deuda_toxica_monto:,.0f} al {deuda_toxica_pct:.0f}%. "
            f"Plan: 1) Refinancia en banco (6% < 25%), 2) Negocia con emisor, 3) Destina 50% ahorro a extinción. "
            f"Meta: -50% en 90 días."
        )
    
    if ahorro < gastos * 3:
        monto_fondo = gastos * 3
        acciones["corto_plazo"].append(
            f"🛡️ FONDO EMERGENCIA: Necesitas ${monto_fondo:,.0f}. "
            f"Plan: Ahorra ${monto_fondo/3:,.0f}/mes en 3 meses. Coloca en: Plazo fijo 5% + SELIC + CCL."
        )
    
    if margen_libertad < 0.1:
        acciones["corto_plazo"].append(
            f"🚨 SIN INGRESOS PASIVOS: Gastos ${gastos:,.0f}/mes sin cobertura. "
            f"Opciones: 1) Inmovilizado al 5-6% = ${gastos/0.06:,.0f} capital, "
            f"2) Acciones dividen 3-5% = ${gastos/0.04:,.0f}, 3) Startup 10% = ${gastos/0.10:,.0f}."
        )
    
    # ========================
    # MEDIANO PLAZO (3-12 meses)
    # ========================
    if ingreso_negocio > ingresos * 0.4:
        acciones["mediano_plazo"].append(
            f"🚀 EMPRENDEDOR: Negocio ${ingreso_negocio:,.0f}/mes. "
            f"Plan: 1) Sistematiza operaciones (reduce horas), 2) Aumenta precio 10%, "
            f"3) Retén 30% ganancias para reinversión. Meta: ${ingreso_negocio * 1.5:,.0f}/mes en 6 meses."
        )
    else:
        acciones["mediano_plazo"].append(
            f"💼 ASALARIADO: Ingresos ${ingresos:,.0f}/mes. "
            f"Plan: 1) Invierte ${ahorro:,.0f}/mes en índices (SPY, VTI), "
            f"2) Negocia aumento (benchmarkea), 3) Busca side hustle +10% ingresos."
        )
    
    if porcentaje_inmuebles > 70:
        acciones["mediano_plazo"].append(
            f"🏠 SOBRE-CONCENTRACIÓN: {porcentaje_inmuebles:.0f}% en inmuebles (${pat_inmuebles:,.0f}). "
            f"Plan: 1) Vende secundario, 2) Refinancia con bono, 3) Diversifica: 40% acciones, 30% renta fija, 20% cripto, 10% alternativas."
        )
    
    objetivos = getattr(perfil, 'objetivos', [])
    objetivo_principal = objetivos[0] if objetivos else 'independencia_financiera'
    
    if objetivo_principal == 'independencia_financiera' or margen_libertad < 0.2:
        acciones["mediano_plazo"].append(
            f"💰 HACIA INDEPENDENCIA: Necesitas ${gastos:,.0f}/mes pasivos. "
            f"Construye: 1) 50% en renta fija 5% = ${gastos/0.05 * 0.5:,.0f}, "
            f"2) 30% en dividen-stocks = ${gastos/0.04 * 0.3:,.0f}, "
            f"3) 20% en bienes raíces alquiler = ${gastos/0.06 * 0.2:,.0f}."
        )
    
    # ========================
    # LARGO PLAZO (1-10 años)
    # ========================
    if objetivo_principal == 'emprender':
        acciones["largo_plazo"].append(
            f"🎯 ESCALA TU NEGOCIO: De ${ingreso_negocio:,.0f} → ${ingreso_negocio * 5:,.0f}/mes. "
            f"Etapas: 1) Sistematiza (año 1), 2) Contrata equipo (año 2-3), 3) Vende o escala (año 4+)."
        )
    elif objetivo_principal == 'comprar_vivienda':
        acciones["largo_plazo"].append(
            f"🏘️ COMPRA VIVIENDA: Ahorra ${ahorro:,.0f}/mes × 60 meses = ${ahorro * 60:,.0f} + rendimientos. "
            f"Préstamo hipotecario al 20% menos. Meta: 2026-2027."
        )
    elif objetivo_principal == 'viajar':
        acciones["largo_plazo"].append(
            f"✈️ FONDO VIAJES: Destina 10% ahorro (${ahorro * 0.1:,.0f}/mes). "
            f"En 5 años = ${ahorro * 0.1 * 60:,.0f} + inversiones. Viajes premium asegurados."
        )
    else:
        acciones["largo_plazo"].append(
            f"📈 RIQUEZA: Construye patrimonio ${patrimonio:,.0f} → ${patrimonio * 3:,.0f} en 10 años. "
            f"Tasa 12% anual realista con diversificación."
        )
    
    acciones["largo_plazo"].append(
        "📅 REVISIÓN ANUAL: Rebalanceo, impuestos, inflación ARG (50%+). Ajusta según contexto macroeconómico."
    )
    
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

PÁRRAFO 1: Situación actual (¿dónde está hoy?)
PÁRRAFO 2: Dinámicas ocultas (¿qué está fallando?)
PÁRRAFO 3: Potencial (¿qué podría cambiar en 12 meses?)

Tono: directo, seco, sin esperanza falsa. Genera URGENCIA."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except:
        return "Radiografía no disponible"

def construir_resultado(perfil, diagnostico_financiero, permitir_ver=False):
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
            print(f"[⚠️ REPARACIÓN] ResultadoIA incompleto detectado para {perfil.user.username}. Regenerando...")
            resultado_existente.delete()
            resultado_existente = None
        else:
            if permitir_ver and resultado_existente.esta_bloqueado:
                resultado_existente.esta_bloqueado = False
                resultado_existente.save(update_fields=["esta_bloqueado"])
            return resultado_existente

    try:
        radiografia = generar_radiografia_ia(diagnostico_financiero, snapshot)
        acciones = generar_acciones_personalizadas(snapshot, perfil)
        
        objetivos = getattr(perfil, 'objetivos', [])
        objetivo_principal = objetivos[0] if objetivos else 'independencia_financiera'
        meta_info = METAS_MAP.get(objetivo_principal, METAS_MAP['independencia_financiera'])
        
        # 🔴 AGREGAR FEEDBACK PERSONALIZADO
        feedback_personalizado = generar_feedback_meta(objetivo_principal, snapshot, perfil)
        meta_info['feedback'] = feedback_personalizado
        
        bloque_metas = json.dumps(meta_info)
        bloque_acciones = json.dumps(acciones)
        
        contenido = f"RADIOGRAFÍA\n{radiografia}\n\nPLAN DE GUERRA\n{json.dumps(acciones, indent=2)}"
        
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
        print(f"[ERROR construir_resultado] {str(e)}")
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