from openai import OpenAI
from django.conf import settings

def get_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def generar_bloque_ia(tipo, contexto):
    """
    Genera un bloque de texto IA según el tipo solicitado.
    Tipos válidos:
    - diagnostico
    - estructura
    - sesgo
    - proyeccion
    - accion
    - cierre
    """

    perfil = contexto["perfil"]
    diagnostico = contexto["diagnostico"]
    snapshot = contexto["snapshot"]
    proy = contexto["proyecciones"]

    # =========================
    # CONTEXTO COMÚN (para IA)
    # =========================
    base_contexto = f"""
Perfil del usuario:
Edad: {getattr(perfil, 'edad', 'N/D')}
Situación habitacional: {getattr(perfil, 'situacion_habitacional', 'N/D')}

Diagnóstico:
Ingresos totales: {snapshot['ingresos']}
Gastos totales: {snapshot['gastos']}
Ahorro mensual: {snapshot['ahorro_mensual']}
Patrimonio neto: {snapshot['patrimonio_neto']}
Ratio deuda/patrimonio: {snapshot['ratio_deuda_patrimonio']}

Objetivos declarados (orden real):
{snapshot['objetivos']}

Proyección 10 años:
Escenario positivo: {proy['positiva'][-1]}
Escenario medio: {proy['media'][-1]}
Escenario negativo: {proy['negativa'][-1]}
"""

    # =========================
    # PROMPTS POR BLOQUE
    # =========================

    prompts = {

        "diagnostico": f"""
Sos Emiliano Miotti.
Hablás directo, seco, profesional. Segunda persona.

Objetivo:
Explicar dónde está parada HOY esta persona.
No adornes. No suavices.
Marcá urgencia de cambio, pero también resaltá una fortaleza real.

No listes datos.
No prometas resultados.
No hables como IA.

Contexto:
{base_contexto}

Texto esperado:
Un diagnóstico ejecutivo claro, incómodo y honesto.
200–250 palabras.
""",

        "estructura": f"""
Actuás como mentor financiero estratégico.

Objetivo:
Explicar la estructura financiera del usuario.
Dónde está sólido y dónde es frágil.
Qué parte depende de esfuerzo y cuál de sistema.

Sé concreto.
Usá números solo si aportan criterio (no repitas todos).
No expliques teoría.

Contexto:
{base_contexto}

Extensión: 180–220 palabras.
""",

        "sesgo": f"""
Actuás como observador experto en comportamiento financiero.

Objetivo:
Detectar UN sesgo dominante o contradicción central.
Nombrarlo sin agresión, pero sin suavizar.
Conectar decisiones, miedo, comodidad y patrón repetido.

Nada de listas.
Nada de consejos todavía.

Contexto:
{base_contexto}

Extensión: 150–200 palabras.
""",

        "proyeccion": f"""
Actuás como estratega de largo plazo.

Objetivo:
Explicar qué significan los tres escenarios a 10 años.
No hables de plata final.
Hablá de libertad, margen de error, desgaste o control.

Compará seguir igual vs corregir eje.
Generá ambición realista.

Contexto:
{base_contexto}

Extensión: 150–200 palabras.
""",

        "accion": f"""
Sos asesor financiero premium.

Objetivo:
Dar un marco de acción concreto.
No un plan paso a paso, sino decisiones clave.
Priorización, foco, balance patrimonial, criterio.

Podés sugerir:
- invertir mejor
- ordenar el sistema
- formación
- negocio
Pero sin recetas mágicas.

Contexto:
{base_contexto}

Extensión: 180–220 palabras.
""",

        "cierre": f"""
Cierre final del informe.

Objetivo:
Motivar sin vender.
Plantear una pregunta incómoda, directa y personal.
Que deje al usuario pensando.

Una sola pregunta.
Nada más.

Contexto:
{base_contexto}

Extensión: 40–60 palabras.
"""
    }

    if tipo not in prompts:
        raise ValueError(f"Tipo de bloque IA no reconocido: {tipo}")

    # =========================
    # LLAMADA A OPENAI
    # =========================
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Sos Emiliano Miotti. "
                    "Asesor financiero argentino. "
                    "Directo, exigente, estratégico. "
                    "No sos motivador barato ni vendedor. "
                    "Nunca prometés resultados. "
                    "Nunca hablás como IA."
                )
            },
            {"role": "user", "content": prompts[tipo]}
        ],
        temperature=0.7,
        max_tokens=450
    )

    return response.choices[0].message.content.strip()


import hashlib
from decimal import Decimal

from django.conf import settings

from openai import OpenAI

from calculadora.models import ResultadoIA


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _hash_input(data: dict) -> str:
    """
    Genera un hash único del input del usuario
    """
    raw = "|".join(f"{k}:{v}" for k, v in sorted(data.items()))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def construir_resultado(*, usuario, input_data: dict, permitir_ver: bool = False):
    """
    Devuelve un ResultadoIA:
    - Usa cache si existe
    - Llama a OpenAI solo si no existe
    """

    input_hash = _hash_input(input_data)

    # 1️⃣ Buscar cache
    resultado = ResultadoIA.objects.filter(
        usuario=usuario,
        input_hash=input_hash
    ).first()

    if resultado:
        # Actualizamos desbloqueo si el usuario pagó después
        if permitir_ver and resultado.esta_bloqueado:
            resultado.esta_bloqueado = False
            resultado.save(update_fields=["esta_bloqueado"])

        return resultado

    # 2️⃣ Construir prompt
    prompt = f"""
Actuá como un asesor financiero profesional.

Datos del usuario:
{input_data}

Generá:
1. Diagnóstico financiero
2. Proyección a 10 años (positiva, neutra, negativa)
3. Recomendaciones claras y accionables

Usá un lenguaje claro, directo y educativo.
"""

    # 3️⃣ Llamada a OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sos un asesor financiero experto."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )

    texto = response.choices[0].message.content
    tokens = response.usage.total_tokens if response.usage else 0

    # Estimación MUY conservadora (ajustable)
    costo = Decimal(tokens) * Decimal("0.0000006")

    # 4️⃣ Guardar resultado
    resultado = ResultadoIA.objects.create(
        usuario=usuario,
        input_hash=input_hash,
        contenido=texto,
        modelo_ia="gpt-4o-mini",
        tokens_usados=tokens,
        costo_estimado_usd=costo,
        esta_bloqueado=not permitir_ver,
    )

    return resultado
