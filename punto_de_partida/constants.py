"""Datos fijos del diseño del juego 'Punto de Partida'.

Todos los montos/porcentajes están centralizados acá para poder ajustarlos
fácilmente antes del evento en vivo sin tocar la lógica de resolución.
"""
from decimal import Decimal

POZO_TOTAL = Decimal("1000000")

# --- Distribución del capital inicial (pesos aleatorios, no equitativos) ---
PESO_TIERS = [
    {"clave": "herencia", "label": "Herencia / beca", "prob": Decimal("0.10"), "peso": Decimal("8")},
    {"clave": "ahorros", "label": "Familia con ahorros", "prob": Decimal("0.20"), "peso": Decimal("3")},
    {"clave": "promedio", "label": "Ingreso promedio", "prob": Decimal("0.40"), "peso": Decimal("1.5")},
    {"clave": "ajustado", "label": "Ajustado", "prob": Decimal("0.20"), "peso": Decimal("0.6")},
    {"clave": "deuda_inicial", "label": "Deuda inicial", "prob": Decimal("0.10"), "peso": Decimal("0.3")},
]
DEUDA_INICIAL_MONTO = Decimal("3000")  # deuda que ya arrastra este tier, se cobra en Ronda 4

# --- Habilidades (una por integrante, se acumulan en equipos) ---
HABILIDADES = {
    "red_contactos": {
        "nombre": "Red de contactos",
        "descripcion": "Reduce costos y umbrales de acceso a oportunidades (se acumula por integrante).",
        "tipo": "positiva",
    },
    "colchon_familiar": {
        "nombre": "Colchón familiar",
        "descripcion": "Una vez en la partida, anula la pérdida de la Ronda 4 (Crisis).",
        "tipo": "positiva",
    },
    "tolerancia_riesgo": {
        "nombre": "Tolerancia al riesgo",
        "descripcion": "Multiplica el resultado (positivo o negativo) de las rondas de inversión.",
        "tipo": "riesgo",
    },
    "disciplina_ahorro": {
        "nombre": "Disciplina de ahorro",
        "descripcion": "Bonus automático al elegir la opción segura en una ronda de inversión (se acumula por integrante).",
        "tipo": "positiva",
    },
    "informacion_privilegiada": {
        "nombre": "Información privilegiada",
        "descripcion": "Ve el rango real de resultados de cada opción antes de elegir.",
        "tipo": "informativa",
    },
    "impulsividad": {
        "nombre": "Impulsividad",
        "descripcion": "Los eventos externos (crisis, suerte) golpean más fuerte (se acumula por integrante).",
        "tipo": "negativa",
    },
}
HABILIDADES_IDS = list(HABILIDADES.keys())

# --- Ronda 1: gasto inesperado ---
RONDA1_GASTO = Decimal("3000")
RONDA1_DEUDA_A_DEVOLVER = Decimal("4000")  # se cobra íntegro en Ronda 4 si se eligió "prestamo"
RONDA1_PENALIZACION_RONDA2_PP = Decimal("0.15")  # puntos porcentuales que se restan al rendimiento de Ronda 2 si "ignorar"

RONDA1_OPCIONES = [
    {"id": "ahorros", "label": f"Pagar con ahorros (-${RONDA1_GASTO:,.0f})"},
    {"id": "prestamo", "label": f"Pedir prestado (se cobra ${RONDA1_DEUDA_A_DEVOLVER:,.0f} en la Ronda 4)"},
    {"id": "ignorar", "label": "Ignorarlo (penaliza tu próxima inversión)"},
]

# --- Bonus de "disciplina_ahorro" al elegir la opción segura en Ronda 2 o 5 ---
DISCIPLINA_AHORRO_BONUS_PP = Decimal("0.05")  # puntos porcentuales, por cada integrante que tenga la habilidad

# --- Ronda 2: primera inversión ---
RONDA2_BANCO_PCT = Decimal("0.03")
RONDA2_FONDO_RANGO = (Decimal("-0.10"), Decimal("0.25"))
RONDA2_ACCION_RANGO = (Decimal("-0.60"), Decimal("1.20"))

RONDA2_OPCIONES = [
    {"id": "banco", "label": "Guardarlo en el banco (seguro, +3%)"},
    {"id": "fondo", "label": "Fondo diversificado (riesgo medio)"},
    {"id": "accion", "label": "Apostar todo a una acción (riesgo alto)"},
]

# --- Ronda 3: oportunidad exclusiva ---
RONDA3_UMBRAL = Decimal("15000")
RONDA3_UMBRAL_CON_CONTACTOS = Decimal("7500")  # umbral por cada instancia de red_contactos
RONDA3_RETORNO_PCT = Decimal("0.80")

RONDA3_OPCIONES = [
    {"id": "entrar", "label": f"Entrar a la preventa (retorno garantizado +{RONDA3_RETORNO_PCT:.0%})"},
    {"id": "mirar", "label": "Quedarse mirando"},
]

# --- Ronda 4: crisis económica global ---
RONDA4_PERDIDA_PCT = Decimal("0.15")

# --- Ronda 5: apalancamiento ---
RONDA5_MULTIPLICADOR_PRESTAMO = Decimal("2")
RONDA5_INTERES_PRESTAMO_PCT = Decimal("0.20")
RONDA5_RANGO = (Decimal("-0.15"), Decimal("0.35"))

RONDA5_OPCIONES = [
    {"id": "normal", "label": "Invertir solo tu capital"},
    {"id": "apalancado", "label": "Pedir prestado el doble e invertir todo (más riesgo)"},
]

# --- Ronda 6: evento final ---
RONDA6_EVENTOS = [
    {"id": "trabajo", "label": "Conseguiste un trabajo mejor pago", "monto": Decimal("8000"), "prob": Decimal("0.25")},
    {"id": "herencia", "label": "Heredaste algo de un familiar", "monto": Decimal("15000"), "prob": Decimal("0.10")},
    {"id": "nada", "label": "Un mes tranquilo, sin sobresaltos", "monto": Decimal("0"), "prob": Decimal("0.20")},
    {"id": "robo", "label": "Te robaron", "monto": Decimal("-3000"), "prob": Decimal("0.20")},
    {"id": "medico", "label": "Gasto médico imprevisto", "monto": Decimal("-5000"), "prob": Decimal("0.25")},
]

RONDAS = [
    {"numero": 1, "titulo": "Gasto inesperado",
     "descripcion": "Se te rompió algo esencial y hay que resolverlo ya.",
     "opciones": RONDA1_OPCIONES},
    {"numero": 2, "titulo": "Primera inversión",
     "descripcion": "Tenés un excedente este mes. ¿Qué hacés con él?",
     "opciones": RONDA2_OPCIONES},
    {"numero": 3, "titulo": "Oportunidad exclusiva",
     "descripcion": f"Preventa con retorno garantizado, pero pide un capital mínimo de ${RONDA3_UMBRAL:,.0f}.",
     "opciones": RONDA3_OPCIONES},
    {"numero": 4, "titulo": "Crisis económica global",
     "descripcion": "Sube todo, el dinero vale menos. Golpea a todos, pero no por igual.",
     "opciones": []},  # ronda sin decisión del jugador, es automática
    {"numero": 5, "titulo": "Apalancamiento",
     "descripcion": "Podés pedir prestado para invertir más fuerte.",
     "opciones": RONDA5_OPCIONES},
    {"numero": 6, "titulo": "Vida real",
     "descripcion": "Un evento al azar te toca, para bien o para mal.",
     "opciones": []},  # ronda sin decisión del jugador, es automática
]
TOTAL_RONDAS = len(RONDAS)
