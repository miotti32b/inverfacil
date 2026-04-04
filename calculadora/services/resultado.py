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

# ============================================================
# 🆕 ANÁLISIS INTELIGENTE DEL PERFIL
# ============================================================

def analizar_perfil_estrategico(diagnostico_financiero, snapshot):
    """
    Detecta si el usuario es emprendedor, asalariado, o híbrido.
    También identifica trampas de concentración de patrimonio.
    
    Retorna un dict con el análisis estratégico personalizado.
    """
    
    # --- ANÁLISIS DE INGRESOS ---
    ingresos_total = float(snapshot.get('ingresos') or 0)
    ingreso_trabajo = float(diagnostico_financiero.ingreso_trabajo or 0) if diagnostico_financiero else 0
    ingreso_negocio = float(diagnostico_financiero.ingreso_negocio or 0) if diagnostico_financiero else 0
    ingreso_rentas = float(diagnostico_financiero.ingreso_rentas or 0) if diagnostico_financiero else 0
    ingreso_inversiones = float(diagnostico_financiero.ingreso_inversiones or 0) if diagnostico_financiero else 0
    
    # Calcular pesos
    peso_trabajo = (ingreso_trabajo / ingresos_total * 100) if ingresos_total > 0 else 0
    peso_negocio = (ingreso_negocio / ingresos_total * 100) if ingresos_total > 0 else 0
    peso_pasivo = ((ingreso_rentas + ingreso_inversiones) / ingresos_total * 100) if ingresos_total > 0 else 0
    
    # Detectar si es emprendedor (>40% del ingreso viene de negocio)
    es_emprendedor = peso_negocio > 40
    
    # --- ANÁLISIS DE PATRIMONIO ---
    patrimonio_total = float(snapshot.get('patrimonio') or 0)
    
    # Leer desde JSONField patrimonio_comp
    patrimonio_comp = getattr(diagnostico_financiero, "patrimonio_comp", {}) or {}
    pat_inmuebles = float(patrimonio_comp.get("pat_inmuebles", 0) or 0)
    pat_empresa = float(patrimonio_comp.get("pat_empresa", 0) or 0)
    pat_vehiculos = float(patrimonio_comp.get("pat_vehiculos", 0) or 0)
    pat_inversiones = float(patrimonio_comp.get("pat_inversiones", 0) or 0)
    pat_cash = float(patrimonio_comp.get("pat_cash", 0) or 0)
    
    # Calcular porcentajes
    porcentaje_inmuebles = (pat_inmuebles / patrimonio_total * 100) if patrimonio_total > 0 else 0
    porcentaje_empresa = (pat_empresa / patrimonio_total * 100) if patrimonio_total > 0 else 0
    porcentaje_liquidez = ((pat_cash + pat_inversiones) / patrimonio_total * 100) if patrimonio_total > 0 else 0
    
    # Detectar trampas
    hay_trampa_inmueble = (porcentaje_inmuebles > 80 and 
                          float(snapshot.get('ratio_libertad') or 0) < 0.15)
    
    hay_trampa_empresa = (porcentaje_empresa > 60 and 
                         es_emprendedor and 
                         pat_empresa > 0)
    
    falta_liquidez = (porcentaje_liquidez < 10 and patrimonio_total > 0)
    
    # --- ESTADO DE ALARMA ---
    nivel_alarma = "OK"
    if hay_trampa_inmueble or hay_trampa_empresa:
        nivel_alarma = "CRÍTICO"
    elif float(snapshot.get('margen_error') == 'bajo') or falta_liquidez:
        nivel_alarma = "ALTO"
    elif float(snapshot.get('estado_general') == 'intermedio'):
        nivel_alarma = "MEDIO"
    
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

# ============================================================
# 🆕 GENERADOR DE ACCIONES PERSONALIZADAS
# ============================================================

def generar_acciones_personalizadas(contexto, analisis):
    """
    Genera acciones concretas según el perfil estratégico.
    Retorna un dict con acciones para 3 horizontes temporales.
    """
    
    snapshot = contexto["snapshot"]
    diagnostico_financiero = contexto.get("diagnostico_financiero")
    perfil = contexto["perfil"]
    
    # 📌 TODAS LAS VARIABLES NECESARIAS
    ingresos = float(snapshot.get('ingresos') or 0)
    gastos = float(snapshot.get('gastos') or 0)
    ahorro = float(snapshot.get('ahorro') or 0)
    patrimonio = float(snapshot.get('patrimonio') or 0)
    deuda = float(snapshot.get('deuda') or 0)
    
    # Ingresos segmentados (ESTOS FALTABAN)
    ingreso_trabajo = float(snapshot.get('ingreso_trabajo') or 0)
    ingreso_negocio = float(snapshot.get('ingreso_negocio') or 0)
    ingreso_rentas = float(snapshot.get('ingreso_rentas') or 0)
    ingreso_inversiones = float(snapshot.get('ingreso_inversiones') or 0)
    
    # Patrimonio segmentado
    pat_inmuebles = float(snapshot.get('pat_inmuebles') or 0)
    pat_empresa = float(snapshot.get('pat_empresa') or 0)
    pat_cash = float(snapshot.get('pat_cash') or 0)
    
    # Ratios
    horas_esclavas = float(snapshot.get('horas_esclavas') or 0)
    ratio_libertad = float(snapshot.get('ratio_libertad') or 0)
    deuda_toxica = float(snapshot.get('porcentaje_deuda_toxica') or 0)
    
    acciones = {
        "corto_plazo": [],
        "mediano_plazo": [],
        "largo_plazo": [],
    }
    
    # --- CORTO PLAZO (0-3 meses) ---
    if analisis["hay_trampa_inmueble"]:
        acciones["corto_plazo"].append(
            f"Evaluar venta parcial de inmueble: tienes ${pat_inmuebles:,.0f} inmovilizado. "
            f"Vender 30-50% = ${pat_inmuebles*0.4:,.0f} para descongelar capital."
        )
    
    if deuda_toxica > 30:  # >30% de deuda es tóxica
        acciones["corto_plazo"].append(
            f"Plan de extinción de deuda tóxica: ${deuda*deuda_toxica/100:,.0f}. "
            f"Destiná 50% de tu ahorro a eliminarla en 6-12 meses."
        )
    
    if horas_esclavas > 200:  # >200 horas/mes
        acciones["corto_plazo"].append(
            f"Urgencia máxima: trabajas {horas_esclavas:.0f} horas/mes (casi full-time extra). "
            f"Pausa inversiones, reduce gastos innecesarios, crea margen de seguridad."
        )
    
    if not acciones["corto_plazo"]:
        acciones["corto_plazo"].append(
            "Crear fondo de emergencia de 3-6 meses de gastos: "
            f"${gastos*3:,.0f} - ${gastos*6:,.0f}. Esta es tu primera inversión."
        )
    
    # --- MEDIANO PLAZO (3-12 meses) ---
    if analisis["es_emprendedor"]:
        acciones["mediano_plazo"].append(
            f"Tu ingreso de negocio (${ingreso_negocio:,.0f}/mes) es tu mejor activo. "
            f"Reinvierte ganancias para escalar. Objetivo: duplicar ingresos en 12-18 meses."
        )
        acciones["mediano_plazo"].append(
            f"Paralelamente: DCA mínimo en Bitcoin (${ingresos*0.01:,.0f}/mes) como blindaje inflacionario. "
            f"Sin distraerte del negocio."
        )
    else:
        acciones["mediano_plazo"].append(
            f"Tu sueldo es estable (${ingresos:,.0f}/mes). "
            f"Comenzá diversificación: 60% CEDEARs con dividendo, 30% ONs, 10% alternativas."
        )
    
    if analisis["hay_trampa_empresa"]:
        acciones["mediano_plazo"].append(
            f"Tu empresa es {analisis['porcentaje_empresa']:.0f}% de tu patrimonio. "
            f"Considerá vender participación o buscar socio de capital. Diversifica riesgo."
        )
    
    if ratio_libertad < 0.1:
        acciones["mediano_plazo"].append(
            f"Tus ingresos pasivos cubren {ratio_libertad*100:.0f}% de gastos. "
            f"Meta: llegar a 20-30% en 12 meses. Invierte en activos que generan renta."
        )
    
    # --- LARGO PLAZO (1-10 años) ---
    objetivos = getattr(perfil, 'objetivos', [])
    objetivo_principal = objetivos[0] if objetivos else 'desconocido'
    
    if objetivo_principal == 'independencia_financiera':
        acciones["largo_plazo"].append(
            f"Tu objetivo: independencia financiera. Necesitás ingresos pasivos ≥ ${gastos:,.0f}/mes. "
            f"Plan: en 10 años, portfolio de ${ingresos*12*10*2:,.0f} generando 5-7% anual."
        )
    elif objetivo_principal == 'emprender':
        acciones["largo_plazo"].append(
            f"Tu objetivo: emprender. Estructurá tu empresa para escala: procesos, equipo, sistemas. "
            f"No seás el cuello de botella. Objetivo: empresa sin ti generando ingresos."
        )
    elif objetivo_principal == 'invertir_mas':
        acciones["largo_plazo"].append(
            f"Tu objetivo: invertir más. Diversificación geográfica (mercados internacionales: US, EUR). "
            f"Crecimiento exponencial vía compounding a 7-10% anual."
        )
    else:
        acciones["largo_plazo"].append(
            f"Tu objetivo: {objetivo_principal}. Estructura patrimonial para lograrlo. "
            f"Trabajá con un asesor para estrategia fiscal y de activos."
        )
    
    acciones["largo_plazo"].append(
        f"Revisión anual: rebalanceo de portfolio, impuestos, inflación. "
        f"Cada año, incrementá inversión 10-15% para efecto snowball."
    )
    
    return acciones

# ============================================================
# 🔥 FUNCIÓN MEJORADA: GENERAR RESPUESTA IA ÚNICA
# ============================================================

def generar_respuesta_ia_unica(contexto):
    try:
        perfil = contexto["perfil"]
        snapshot = contexto["snapshot"]
        proy = contexto["proyecciones"]
        diagnostico_financiero = contexto.get("diagnostico_financiero")

        # 🔥 NUEVOS ANÁLISIS
        analisis_estrategico = analizar_perfil_estrategico(diagnostico_financiero, snapshot)
        acciones = generar_acciones_personalizadas(contexto, analisis_estrategico)

        # 🔥 Proyecciones al Año 10
        proy_pos_final = proy.get('positiva', [0])[-1]
        proy_med_final = proy.get('media', [0])[-1]
        proy_neg_final = proy.get('negativa', [0])[-1]

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

        # Extracción de datos duros
        edad = getattr(perfil, 'edad', 0)
        hijos = getattr(perfil, 'hijos_a_cargo', 0)
        ingresos = snapshot.get('ingresos', 0)
        gastos = snapshot.get('gastos', 0)
        ahorro = snapshot.get('ahorro', 0)
        patrimonio = snapshot.get('patrimonio', 0)
        deuda = snapshot.get('deuda', 0)

        # Formatear acciones para el prompt
        acciones_corto = "\n".join([f"→ {a}" for a in acciones.get('corto_plazo', [])])
        acciones_mediano = "\n".join([f"→ {a}" for a in acciones.get('mediano_plazo', [])])
        acciones_largo = "\n".join([f"→ {a}" for a in acciones.get('largo_plazo', [])])

        # 🚀 EL PROMPT MAESTRO MEJORADO
        prompt = f"""
        Sos Emiliano Miotti, un experto en finanzas y creación de patrimonio. 
        Tu misión: Darle al usuario una lectura estratégica de su vida financiera con un STORYTELLING implacable, empático y 100% personalizado.
        
        REGLAS DE ORO DE TU TONO Y ESTILO:
        - NO hables como un robot. NO repitas los datos textualmente.
        - Si algún dato dice "No especificado" o es "0.0", IGNORALO COMPLETAMENTE. No lo menciones.
        - Usá voseo argentino, directo al hueso. 
        - PERSONALIZACIÓN MAX: Hablá de su situación específica, no de "el usuario promedio".

        ANÁLISIS ESTRATÉGICO (TU BRÚJULA):
        - {("Sos EMPRENDEDOR" if analisis_estrategico["es_emprendedor"] else "Sos ASALARIADO")}: tu fuente principal es {(f"{analisis_estrategico['peso_negocio']:.0f}% negocio" if analisis_estrategico["es_emprendedor"] else f"{analisis_estrategico['peso_trabajo']:.0f}% sueldo")}
        - Tu patrimonio: {analisis_estrategico['porcentaje_inmuebles']:.0f}% inmuebles, {analisis_estrategico['porcentaje_empresa']:.0f}% empresa, {analisis_estrategico['porcentaje_liquidez']:.0f}% líquido
        - Tu libertad actual: {ratio_libertad:.0f}% de gastos cubiertos por ingresos pasivos (meta: >50%)
        - ALARMA: {analisis_estrategico['nivel_alarma']}
        {f"  → TRAMPA: Tienes >80% en inmuebles sin ingreso pasivo. Capital congelado." if analisis_estrategico["hay_trampa_inmueble"] else ""}
        {f"  → RIESGO: Tu empresa es >60% del patrimonio. Diversifica." if analisis_estrategico["hay_trampa_empresa"] else ""}
        {f"  → FRÁGIL: Menos de 10% líquido. Un problema = crisis." if analisis_estrategico["falta_liquidez"] else ""}

        DATOS DUROS (Contale una historia, no el Excel):
        - Edad: {edad} años
        - Horas de esclavitud: {horas_esclavas:.0f} hs/mes ({horas_esclavas/30:.1f} hs/día)
        - Ingresos totales: ${ingresos:,.0f}/mes
        - Gastos: ${gastos:,.0f}/mes
        - Ahorro: ${ahorro:,.0f}/mes ({(ahorro/ingresos*100 if ingresos > 0 else 0):.1f}% de ingresos)
        - Patrimonio neto: ${patrimonio-deuda:,.0f}

        PLAN DE GUERRA PERSONALIZADO:
        
        CORTO PLAZO (0-3 MESES):
        {acciones_corto if acciones_corto else "→ Crear fondo de emergencia 3-6 meses de gastos."}
        
        MEDIANO PLAZO (3-12 MESES):
        {acciones_mediano if acciones_mediano else "→ Comenzar diversificación según perfil."}
        
        LARGO PLAZO (1-10 AÑOS):
        {acciones_largo if acciones_largo else "→ Libertad financiera según tus objetivos."}

        ESTRUCTURA DE TU RESPUESTA (DEVOLVÉ ÚNICAMENTE ESTE JSON VÁLIDO):
        {{
            "bloque_diagnostico": "Un párrafo potente que conecte todo: su realidad, sus horas quemadas, de dónde viene su plata, su estado.",
            "bloque_estructura": "Análisis de su patrimonio y deuda. Si está concentrado, destrozá la ilusión. Si está diversificado, felicitalo.",
            "bloque_sesgo": "Desafiá su psicología. Buscá la contradicción central entre lo que dice querer y lo que está haciendo.",
            "bloque_proyeccion": "Contrastá su futuro en 10 años: Positivo ${proy_pos_final:,.0f} vs Negativo ${proy_neg_final:,.0f}. Narrativa, no números.",
            "bloque_accion": "El Plan de Guerra personalizado en 3 fases. Sé específico: qué vender, cuándo, en qué invertir. Acciones concretas.",
            "bloque_cierre": "Mensaje corto, motivador, con autoridad. Firma: Emiliano."
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Responde exclusivamente en JSON válido según la estructura solicitada."},
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
        import traceback
        tb = traceback.format_exc()
        return {
            "estado": "error",
            "error_msg": str(e),
            "traceback": tb,
            "data": None,
            "tokens": 0,
            "costo": 0
        }

# ============================================================
# 🔥 FUNCIÓN PRINCIPAL: CONSTRUIR RESULTADO
# ============================================================

def construir_resultado(perfil, diagnostico_financiero, permitir_ver=False):

    snapshot = calcular_motor_financiero(diagnostico_financiero)
    proy = calcular_proyecciones(perfil, snapshot)
    snapshot_safe = _to_json_safe(snapshot)
    proy_safe = _to_json_safe(proy)

    input_data = {
        **snapshot,
        "proyecciones": proy,
        "objetivos": getattr(perfil, 'objetivos', ''),
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
        "diagnostico_financiero": diagnostico_financiero,
        "snapshot": snapshot_safe,
        "proyecciones": proy_safe,
    }

    # 🔥 LLAMADA ÚNICA A OPENAI (CON ANÁLISIS MEJORADO)
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
