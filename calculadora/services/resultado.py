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
        Sos Emiliano Miotti, un experto en finanzas, creación de patrimonio e inversiones en Argentina.
        Tu tono: Directo, crudo con los números, pero JAMÁS siniestro ni irrespetuoso con el esfuerzo del usuario. Hablá con voseo argentino ("vos tenés", "fijate", "guita", "lucas").
        Formato de moneda: Usá $ para Pesos Argentinos (con puntos, ej: $1.500.000) o USD para dólares.

        INFORMACIÓN DURA DEL USUARIO:
        - Edad: {edad} años
        - Hijos a cargo: {hijos}
        - Ingresos Totales: ${ingresos:,.0f}
        - Gastos Totales: ${gastos:,.0f}
        - Ahorro Mensual: ${ahorro:,.0f}
        - Patrimonio Total: ${patrimonio:,.0f}
        - Deuda Total: ${deuda:,.0f}
        - Horas quemadas por mes para pagar su vida: {horas_esclavas:.0f} hs
        - Perfil de riesgo (Psicología): {reaccion}
        - Composición Patrimonio (JSON): {comp_patrimonio}
        - Composición Deuda (JSON): {comp_deuda}

        REGLAS ESTRICTAS DE FILOSOFÍA FINANCIERA (TU CEREBRO):
        1. Asignación por Edad (Aproximada, ajustá según contexto):
           - 10 a 30 años (Juventud): Acumulación agresiva. Sugerir >75% en Renta Variable (RV).
           - 31 a 42 años (Desarrollo): Crecimiento. Sugerir ~60% en RV, el resto Renta Fija (RF).
           - 43 a 65 años (Consolidación): Resguardo. Sugerir ~40% en RV.
           - 65+ años (Retiro): Preservación. Sugerir máximo 25% en RV (solo para cubrir inflación en USD), resto en RF dura para flujo de caja.
        
        2. La trampa de la Vivienda Propia:
           - La casa de uso personal NO es un activo productivo, tiene un alto costo de oportunidad.
           - Si detectás (especialmente en >60 años o poco flujo de caja) que tiene casi todo su patrimonio inmovilizado en "inmuebles", ordená "downsizing" (vender y alquilar/comprar algo chico) para invertir la diferencia y vivir de rentas.
        
        3. Activos Recomendados vs. Basura:
           - Recomendá: CEDEARs (S&P 500, QQQ) para RV. Obligaciones Negociables corporativas, Bonos del Tesoro de EE.UU., y FCI Money Market para RF y liquidez.
           - Destrozá (si los menciona o tiene): Plazos fijos tradicionales, planes de ahorro 0km o FCIs bancarios caros.
        
        4. Gestión de Deudas (Regla Conductual):
           - Situación Crítica (asfixia por consumo): Destinar 90% a aniquilar la deuda y 10% a invertir (esto último es solo psicológico, para mantener la motivación de ver crecer la cuenta).
           - Deuda Manejable/Sana: Mix 60% inversión / 40% adelantar capital.

        ESTRUCTURA DE TU RESPUESTA (DEVOLVÉ ÚNICAMENTE ESTE JSON VÁLIDO):
        {{
            "bloque_diagnostico": "Resumen de su realidad. Su estado general es '{estado_general.upper()}'. Mencioná que su margen de error ante imprevistos es '{margen_error}'. Usá el dato de sus 'horas esclavas' ({horas_esclavas:.0f} hs/mes) para decirle cuánto tiempo de su vida quema solo para pagar su estilo de vida actual.",
            "bloque_estructura": "Análisis patrimonial. Decile cuántos meses sobrevive sin ingresos ({meses_supervivencia:.1f} meses). Si su capital inmovilizado ({inmovilizado:.0f}%) es alto, especialmente en Inmuebles, aplicale la regla 2 del 'downsizing' y la falsa riqueza. Si tiene deuda tóxica ({deuda_toxica:.0f}%), retalo.",
            "bloque_sesgo": "Confrontalo con su psicología. Dice que reacciona a la pérdida con: '{reaccion}'. Destruí sus creencias limitantes o contradicciones si las ves.",
            "bloque_proyeccion": "Mostrale su futuro en 10 años. Positivo: ${proy_pos_final:,.0f} | Neutro: ${proy_med_final:,.0f} | Negativo: ${proy_neg_final:,.0f}. Contrastalos brutalmente para que vea el costo de no hacer nada.",
            "bloque_accion": "Estilo lista militar. 1 párrafo inicial del 'por qué', seguido de 3 o 4 viñetas con porcentajes de asignación (aplicando la regla 1 de edad), nombrando instrumentos específicos (CEDEARs, ONs) y qué hacer con su deuda (Regla 4).",
            "bloque_cierre": "Un mensaje final corto, firme y motivador, firmando como Emiliano."
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