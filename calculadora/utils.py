from openai import OpenAI
from django.conf import settings
import math

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# --- Motor de proyección financiera ---
def calcular_proyecciones(cliente):
    ingresos = float(
        cliente.ingreso_trabajo + cliente.ingreso_negocio + cliente.ingreso_rentas +
        cliente.ingreso_inversiones + cliente.ingreso_otros
    )
    gastos = float(
        cliente.gasto_necesarios + cliente.gasto_innecesarios +
        cliente.gasto_financieros + cliente.gasto_inversiones
    )
    patrimonio = float(
        cliente.patrimonio_vivienda + cliente.patrimonio_vehiculos +
        cliente.patrimonio_ahorros_local + cliente.patrimonio_ahorros_usd +
        cliente.patrimonio_inversiones + cliente.patrimonio_negocio + cliente.patrimonio_otros
    )
    deudas = float(cliente.deuda_tarjeta + cliente.deuda_auto + cliente.deuda_financiera)

    patrimonio_inicial = patrimonio - deudas
    ahorro_mensual = max(ingresos - gastos, 0)

    educacion = cliente.nivel_formacion / 10
    experiencia = cliente.experiencia_emprendimientos / 10
    capacidad_crecimiento = 0.6 * educacion + 0.4 * experiencia

    tasa_media = 0.03 + capacidad_crecimiento * 0.04
    tasa_positiva = tasa_media + 0.05
    tasa_negativa = max(tasa_media - 0.05, -0.03)

    proyeccion_media = []
    proyeccion_positiva = []
    proyeccion_negativa = []

    patrimonio_actual = patrimonio_inicial

    for año in range(1, 11):
        patrimonio_actual = patrimonio_actual * (1 + tasa_media) + (ahorro_mensual * 12)
        proyeccion_media.append(round(patrimonio_actual, 2))

        patrimonio_positivo = patrimonio_inicial * (1 + tasa_positiva) ** año + (ahorro_mensual * 12 * año)
        patrimonio_negativo = patrimonio_inicial * (1 + tasa_negativa) ** año + (ahorro_mensual * 12 * año * 0.5)

        proyeccion_positiva.append(round(patrimonio_positivo, 2))
        proyeccion_negativa.append(round(patrimonio_negativo, 2))

    return {
        "positiva": proyeccion_positiva,
        "media": proyeccion_media,
        "negativa": proyeccion_negativa,
        "tasa_media": round(tasa_media * 100, 2),
        "tasa_positiva": round(tasa_positiva * 100, 2),
        "tasa_negativa": round(tasa_negativa * 100, 2),
        "ahorro_mensual": ahorro_mensual,
        "patrimonio_inicial": patrimonio_inicial,
    }


from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

## --- Feedback IA con estilo Emiliano Miotti ---
def generar_feedback_ia(cliente, proyecciones):
    # --- Obtener horas trabajadas ---
    try:
        # Si viene del diagnóstico más reciente, se toma de ahí
        diag = cliente.diagnosticos.order_by('-fecha').first()
        horas_trabajadas = diag.horas_trabajadas if diag and diag.horas_trabajadas else 0
    except:
        horas_trabajadas = 0

    # --- Construcción del prompt dinámico ---
    prompt = f"""
        Una persona completó el diagnóstico financiero de InvertirEsFácil.
        Te dejo su situación resumida para que la analices y le hables directamente, como si le dieras un informe personal.

        📊 Perfil general:
        - Edad: {cliente.edad} años
        - Nivel de formación: {cliente.nivel_formacion}/10
        - Experiencia en emprendimientos: {cliente.experiencia_emprendimientos}/10
        - Horas trabajadas por día: {horas_trabajadas}

        💰 Ingresos totales: {cliente.ingreso_trabajo + cliente.ingreso_negocio + cliente.ingreso_rentas + cliente.ingreso_inversiones + cliente.ingreso_otros:,.0f} ARS
        📉 Gastos mensuales: {cliente.gasto_necesarios + cliente.gasto_innecesarios + cliente.gasto_financieros + cliente.gasto_inversiones:,.0f} ARS
        💎 Patrimonio inicial: {proyecciones['patrimonio_inicial']:,.0f} ARS
        💸 Ahorro mensual estimado: {proyecciones['ahorro_mensual']:,.0f} ARS

        📈 Proyección a 10 años:
        - Escenario Positivo: {proyecciones['positiva'][-1]:,.0f} ARS
        - Escenario Medio: {proyecciones['media'][-1]:,.0f} ARS
        - Escenario Negativo: {proyecciones['negativa'][-1]:,.0f} ARS

        🎯 Tasas simuladas:
        - Positiva: {proyecciones['tasa_positiva']}%
        - Media: {proyecciones['tasa_media']}%
        - Negativa: {proyecciones['tasa_negativa']}%

        Tu tarea es redactar un análisis personalizado **como si fueras Emiliano Miotti**.
        No repitas los datos ni hables como un informe, sino como una charla sincera y educativa.

        Instrucciones clave:
        1. Mencioná de forma natural el impacto de trabajar {horas_trabajadas} horas diarias:
           - Si trabaja más de 10 horas, remarcá la falta de libertad personal y sugerí reducir carga o diversificar ingresos.
           - Si trabaja entre 6 y 8, destacá equilibrio y potencial de crecimiento.
           - Si trabaja menos de 5, analizá si es por decisión o falta de oportunidades.
        2. Explicale qué reflejan sus números y hábitos hoy.
        3. Contale cómo podría mejorar su escenario.
        4. Cerrá con una reflexión sobre la relación entre tiempo, dinero y libertad.

        El texto debe fluir como una conversación tuya: reflexiva, concreta y humana.
    """

    # --- Llamada a la API ---
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
Sos Emiliano Miotti, asesor financiero argentino y creador de InvertirEsFácil.

Tu estilo es claro, humano y didáctico. Explicás temas financieros con precisión conceptual,
pero en lenguaje accesible y cercano. Combinás lógica con empatía, sin frases vacías ni tecnicismos innecesarios.

Tenés una mirada integral: unís educación financiera, reflexión personal y libertad económica.
Tu tono es argentino, directo pero amable. Usás expresiones naturales como “mirá”, “ojo con esto”,
“la clave está en…”, “esto pasa mucho cuando…”.

Tu objetivo: que la persona entienda, se motive y vea un camino realista para mejorar.
No desórdenes los datos ni repitas el prompt, hablá con naturalidad, como si grabaras un video reflexivo.
"""
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=750,
        temperature=0.8
    )

    return response.choices[0].message.content


from .models import ClientePerfil

def aplicar_referido(request, user):
    ref_code = request.session.get("referral_code")

    if not ref_code:
        return

    try:
        referidor = ClientePerfil.objects.get(referral_code=ref_code)
        perfil = ClientePerfil.objects.get(user=user)

        # Evitar autoreferido o doble asignación
        if perfil.referido_por is None and referidor != perfil:
            perfil.referido_por = referidor
            perfil.save()

            referidor.total_referred += 1
            referidor.save()

            # Limpiar sesión
            del request.session["referral_code"]

    except ClientePerfil.DoesNotExist:
        pass


from decimal import Decimal

def pagar_comision(perfil_referido, monto_plan):
    if not perfil_referido.referido_por:
        return

    referidor = perfil_referido.referido_por

    # Ejemplo: 10% de comisión
    comision = monto_plan * Decimal("0.10")

    referidor.referral_earnings += comision
    referidor.save()
