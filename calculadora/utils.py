from openai import OpenAI
from django.conf import settings

# Inicializamos cliente OpenAI con la API Key desde settings.py
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generar_feedback_ia(cliente):
    prompt = f"""
    El usuario completó un test financiero con estos datos:

    Edad: {cliente.edad}
    Estado civil: {cliente.estado_civil}
    Ingresos mensuales: 
      - Trabajo: {cliente.ingreso_trabajo}
      - Negocio: {cliente.ingreso_negocio}
      - Rentas: {cliente.ingreso_rentas}
      - Inversiones: {cliente.ingreso_inversiones}
      - Otros: {cliente.ingreso_otros}

    Gastos mensuales:
      - Necesarios: {cliente.gasto_necesarios}
      - Innecesarios: {cliente.gasto_innecesarios}
      - Financieros: {cliente.gasto_financieros}
      - Inversiones: {cliente.gasto_inversiones}

    Patrimonio actual:
      - Vivienda: {cliente.patrimonio_vivienda}
      - Vehículos: {cliente.patrimonio_vehiculos}
      - Ahorros Locales: {cliente.patrimonio_ahorros_local}
      - Ahorros en USD: {cliente.patrimonio_ahorros_usd}
      - Inversiones financieras: {cliente.patrimonio_inversiones}
      - Negocio propio: {cliente.patrimonio_negocio}
      - Otros: {cliente.patrimonio_otros}

    Deudas:
      - Tarjeta: {cliente.deuda_tarjeta}
      - Auto: {cliente.deuda_auto}
      - Casa: {cliente.deuda_casa}
      - Financiera / Otros: {cliente.deuda_financiera}

    Objetivos declarados: {cliente.objetivos}
    Plazo de inversión preferido: {cliente.plazo_inversion}
    Reacción ante pérdidas: {cliente.reaccion_perdida}
    Importancia del dinero: {cliente.importancia_dinero}
    Qué haría con $10.000.000: {cliente.uso_millon}
    Conocimiento sobre acciones: {cliente.conocimiento_acciones}
    Conocimiento sobre seguridad: {cliente.conocimiento_seguridad}
    Nivel de liquidez preferido: {cliente.liquidez}

    Con toda esta información:
    1. Clasifica al usuario en un perfil financiero creativo.
    2. Haz un breve análisis psicológico de su relación con el dinero.
    3. Enumera 3 fortalezas.
    4. Enumera 3 puntos débiles o riesgos.
    5. Sugiere una cartera base de inversión adaptada a su perfil y objetivos.
    6. Usa un tono educativo, cercano y motivador.
    7. Mantén el feedback en 5–7 párrafos claros.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sos un asesor financiero experto, pedagógico y motivador."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=700,
        temperature=0.8
    )

    return response.choices[0].message.content
