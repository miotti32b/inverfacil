def generar_bloque_ia(tipo, contexto):
    if tipo == "diagnostico":
        prompt = prompt_diagnostico_ejecutivo(contexto)
    elif tipo == "estructura":
        prompt = prompt_lectura_estructural(contexto)
    elif tipo == "sesgo":
        prompt = prompt_sesgo_central(contexto)
    elif tipo == "proyeccion":
        prompt = prompt_proyeccion(contexto)
    elif tipo == "accion":
        prompt = prompt_marco_accion(contexto)
    elif tipo == "cierre":
        prompt = prompt_cierre(contexto)
    else:
        return ""

    # llamada a OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=300,
    )

    return response.choices[0].message.content


def prompt_diagnostico_ejecutivo(contexto):
    return f"""
Redactá un diagnóstico ejecutivo financiero.

Tono: directo, seco, profesional.
Persona: segunda persona.
Objetivo: generar urgencia de cambio.

Contexto:
- Estado general: {contexto["snapshot"]["estado_general"]}
- Margen de error: {contexto["snapshot"]["margen_error"]}
- Dependencia del ingreso: {contexto["snapshot"]["dependencia_ingreso"]}

Reglas:
- No usar cifras.
- No usar listas.
- Máximo 120 palabras.
"""

def prompt_lectura_estructural(contexto):
    return f"""
Explicá la estructura financiera de la persona.

Claves:
- equilibrio ingresos / gastos
- ahorro como sistema o accidente
- patrimonio vs deuda

Reglas:
- No repetir números.
- No motivar.
- Máximo 120 palabras.
"""
def prompt_sesgo_central(contexto):
    return f"""
Identificá UNA contradicción central en la forma de manejar el dinero.

Ejemplos:
- esfuerzo sin sistema
- comodidad disfrazada de prudencia
- querer crecer sin incomodarse

Reglas:
- Elegí solo una.
- Decila explícitamente.
- Máximo 90 palabras.
"""
def prompt_proyeccion(contexto):
    return f"""
Explicá qué implica seguir igual vs corregir el eje central.

Hablá de:
- libertad
- margen de error
- desgaste mental

Reglas:
- No hablar de montos.
- No prometer resultados.
- Máximo 100 palabras.
"""
def prompt_marco_accion(contexto):
    return f"""
Explicá por qué el orden correcto es:
1. crear margen
2. construir sistema
3. recién después crecer

Reglas:
- No dar recetas técnicas.
- No recomendar activos.
- Máximo 120 palabras.
"""
def prompt_cierre(contexto):
    return f"""
Cerrá el informe con una pregunta incómoda y personal.

Reglas:
- Una sola pregunta.
- No responderla.
- No vender nada.
"""
