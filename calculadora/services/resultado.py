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
        diagnostico = contexto.get("diagnostico")

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

        # Extracción de datos duros para el cerebro de Emiliano
        edad = getattr(perfil, 'edad', 0)
        hijos = getattr(perfil, 'hijos_a_cargo', 0)
        ingresos = snapshot.get('ingresos', 0)
        gastos = snapshot.get('gastos', 0)
        ahorro = snapshot.get('ahorro', 0)
        patrimonio = snapshot.get('patrimonio', 0)
        deuda = snapshot.get('deuda', 0)
        comp_patrimonio = diagnostico.patrimonio_comp if diagnostico else {}
        comp_deuda = diagnostico.deuda_comp if diagnostico else {}

        # 🚀 EL PROMPT MAESTRO
        prompt = f"""
        Sos Emiliano Miotti, un experto en finanzas y creación de patrimonio. 
        Tu misión: Darle al usuario una lectura estratégica de su vida financiera con un STORYTELLING implacable, empático y 100% personalizado.
        
        REGLAS DE ORO DE TU TONO Y ESTILO:
        - NO hables como un robot. NO repitas los datos textualmente. En lugar de decir "Tu inmovilizado es 0%", decí "Tenés la ventaja de no tener guita atrapada en cosas inútiles".
        - Si algún dato dice "No especificado" o es "0.0", IGNORALO COMPLETAMENTE. No lo menciones.
        - Usá voseo argentino, directo al hueso. 

        DATOS DUROS DEL USUARIO (Analizalos, pero contale una historia, no le leas el Excel):
        - Edad: {edad} años
        - Perfil de riesgo: {reaccion}
        - Horas esclavas al mes: {horas_esclavas:.0f} hs (esto es clave para medir su valor hora y calidad de vida).
        - Ingresos (Total: ${ingresos:,.0f}): Mirá de dónde vienen. ¿Sueldo, Negocio, Inversiones?
        - Patrimonio: Mirá la composición {comp_patrimonio}.
        - Deuda: Mirá la composición {comp_deuda}.

        REGLAS DE INVERSIÓN (TU CEREBRO FINANCIERO):
        1. LA REGLA DEL EMPRENDEDOR: Si detectás que sus ingresos vienen fuerte de su negocio ('ingreso_negocio') o tiene patrimonio en su empresa ('empresa'), CAMBIA TOTALMENTE LA RECETA. NO le recomiendes diversificar agresivamente en la bolsa. Decile que su mejor y mayor activo es su negocio. Su foco debe ser aumentar su ingreso por hora y reinvertir en la empresa para escalar. Para sus inversiones financieras, recomendale algo automático y periférico: DCA (Dollar Cost Averaging) de montos mínimos (ej: 2 a 5 dólares diarios) en Bitcoin (reserva de valor dura) o QQQ, para blindarse del riesgo local sin desenfocarse de su negocio.
        2. LA REGLA DEL EMPLEADO: Si es empleado y no tiene negocios, ahí sí aplicá diversificación clásica (CEDEARs, ONs) según su edad y riesgo.
        3. LA TRAMPA DE LA CASA: Si está muy concentrado en inmuebles propios y tiene bajo flujo, sugerí "downsizing".

        ESTRUCTURA DE TU RESPUESTA (DEVOLVÉ ÚNICAMENTE ESTE JSON VÁLIDO):
        Quiero que escribas de forma fluida, como si fuera una carta o un diagnóstico médico integral.
        {{
            "bloque_diagnostico": "Un párrafo potente. Radiografía cruda de su realidad. Mencioná sus horas quemadas y de dónde viene su plata. Conectá emocionalmente con su situación.",
            "bloque_estructura": "Análisis de su patrimonio y deuda. Si su capital está bien o mal alocado. Si tiene deuda tóxica, destrozala. Si no tiene, felicitalo por la prolijidad.",
            "bloque_sesgo": "Desafiá su psicología. ¿Tiene aversión al riesgo pero quiere ser libre? Marcale la contradicción. (Si no hay datos psicológicos, llená esto con un consejo mental sobre el dinero).",
            "bloque_proyeccion": "Mostrale el costo de no hacer nada. Contrastá su futuro en 10 años (Positivo: ${proy_pos_final:,.0f} vs Negativo: ${proy_neg_final:,.0f}) pero de forma narrativa, ej: 'Si seguís en piloto automático, en 10 años vas a estar estancado en X...'.",
            "bloque_accion": "El Plan de Guerra. 3 pasos tácticos. APLICÁ ACÁ LA REGLA DEL EMPRENDEDOR O DEL EMPLEADO según corresponda. Sé súper específico (ej: DCA en Bitcoin/QQQ, reinversión en negocio, etc).",
            "bloque_cierre": "Un mensaje final corto, motivador y con autoridad. Firma: Emiliano."
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
        return {
            "estado": "error",
            "error_msg": str(e),
            "data": None,
            "tokens": 0,
            "costo": 0
        }

def construir_resultado(perfil, diagnostico, permitir_ver=False):

    snapshot = calcular_motor_financiero(diagnostico)
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
        "diagnostico": diagnostico,
        "snapshot": snapshot_safe,
        "proyecciones": proy_safe,
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