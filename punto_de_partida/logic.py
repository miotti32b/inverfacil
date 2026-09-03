"""Lógica de negocio pura del juego. Sin acceso a request/session ni escrituras a DB.

Toda la aleatoriedad recibe un random.Random explícito para que sea determinística
y testeable. Todos los montos son Decimal, nunca float.
"""
import random
import string
from decimal import ROUND_HALF_UP, Decimal

from . import constants as c

MONEY_QUANT = Decimal("0.01")
CODIGO_ALFABETO = "".join(ch for ch in string.ascii_uppercase + "23456789" if ch not in "O0I1L")


def quantize_money(value):
    return Decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def generar_codigo(longitud=6):
    return "".join(random.choice(CODIGO_ALFABETO) for _ in range(longitud))


def contar_habilidad(habilidades, clave):
    return list(habilidades or []).count(clave)


# --- Asignación de capital inicial ---

def elegir_tier_peso(rng):
    r = rng.random()
    acumulado = 0.0
    for tier in c.PESO_TIERS:
        acumulado += float(tier["prob"])
        if r <= acumulado:
            return tier["clave"], tier["peso"]
    ultimo = c.PESO_TIERS[-1]
    return ultimo["clave"], ultimo["peso"]


def elegir_habilidad(rng):
    return rng.choice(c.HABILIDADES_IDS)


def asignar_capital_inicial(pesos):
    """pesos: iterable de (id, peso_valor: Decimal). Devuelve {id: monto} sumando
    EXACTO c.POZO_TOTAL, con el resto de redondeo ajustado en la porción más grande."""
    pesos = list(pesos)
    if not pesos:
        return {}
    total_peso = sum((p for _, p in pesos), Decimal("0"))
    montos = {}
    for miembro_id, peso in pesos:
        montos[miembro_id] = quantize_money(peso / total_peso * c.POZO_TOTAL)
    diferencia = c.POZO_TOTAL - sum(montos.values(), Decimal("0"))
    if diferencia != 0:
        miembro_mayor = max(montos, key=lambda k: montos[k])
        montos[miembro_mayor] = quantize_money(montos[miembro_mayor] + diferencia)
    return montos


# --- Disponibilidad de opciones (gates) ---

def calcular_umbral_ronda3(habilidades):
    n = contar_habilidad(habilidades, "red_contactos")
    umbral = c.RONDA3_UMBRAL
    for _ in range(n):
        umbral = umbral / 2
    return quantize_money(umbral)


def opcion_disponible(ronda, opcion, capital_actual, habilidades):
    if ronda == 3 and opcion == "entrar":
        return capital_actual >= calcular_umbral_ronda3(habilidades)
    return True


# --- Consenso de equipo ---

def tally_voto_equipo(votos, total_miembros, opcion_conservadora):
    """Mayoría estricta (>50%) del total de integrantes del equipo, no solo de
    quienes votaron. Empate o sin mayoría -> opción conservadora."""
    votos = [v for v in votos if v]
    if not votos or total_miembros <= 0:
        return opcion_conservadora
    conteo = {}
    for v in votos:
        conteo[v] = conteo.get(v, 0) + 1
    opcion_top, count_top = max(conteo.items(), key=lambda kv: kv[1])
    empatados = [k for k, cnt in conteo.items() if cnt == count_top]
    if len(empatados) > 1:
        return opcion_conservadora
    if count_top > total_miembros / 2:
        return opcion_top
    return opcion_conservadora


# --- Resolución por ronda ---

def resolver_ronda1(capital_actual, opcion, habilidades):
    n_contactos = contar_habilidad(habilidades, "red_contactos")
    factor_descuento = max(Decimal("0"), Decimal("1") - Decimal("0.20") * n_contactos)
    costo = quantize_money(c.RONDA1_GASTO * factor_descuento)

    deuda_nueva_delta = Decimal("0")
    penalizacion_ronda2 = False
    capital_nuevo = capital_actual

    if opcion == "ahorros":
        capital_nuevo = capital_actual - costo
    elif opcion == "prestamo":
        deuda_nueva_delta = c.RONDA1_DEUDA_A_DEVOLVER
    elif opcion == "ignorar":
        penalizacion_ronda2 = True

    return {
        "capital_nuevo": quantize_money(capital_nuevo),
        "deuda_delta": deuda_nueva_delta,
        "delta": quantize_money(capital_nuevo - capital_actual),
        "penalizacion_ronda2": penalizacion_ronda2,
        "detalle": {"opcion": opcion, "costo": str(costo)},
    }


def resolver_ronda2(capital_actual, opcion, habilidades, penalizacion_ronda2, rng):
    n_tolerancia = contar_habilidad(habilidades, "tolerancia_riesgo")
    n_disciplina = contar_habilidad(habilidades, "disciplina_ahorro")
    multiplicador_riesgo = Decimal("1") + n_tolerancia

    if opcion == "banco":
        pct = c.RONDA2_BANCO_PCT
    elif opcion == "fondo":
        pct = Decimal(str(rng.uniform(float(c.RONDA2_FONDO_RANGO[0]), float(c.RONDA2_FONDO_RANGO[1]))))
    else:  # accion
        pct = Decimal(str(rng.uniform(float(c.RONDA2_ACCION_RANGO[0]), float(c.RONDA2_ACCION_RANGO[1]))))

    pct_final = pct * multiplicador_riesgo
    if opcion == "banco":
        pct_final += c.DISCIPLINA_AHORRO_BONUS_PP * n_disciplina
    if penalizacion_ronda2:
        pct_final -= c.RONDA1_PENALIZACION_RONDA2_PP

    delta = quantize_money(capital_actual * pct_final)
    return {
        "capital_nuevo": quantize_money(capital_actual + delta),
        "deuda_delta": Decimal("0"),
        "delta": delta,
        "penalizacion_ronda2": False,  # se consume siempre al resolver esta ronda
        "detalle": {"opcion": opcion, "pct_final": str(pct_final)},
    }


def resolver_ronda3(capital_actual, opcion, habilidades):
    if opcion == "entrar":
        delta = quantize_money(capital_actual * c.RONDA3_RETORNO_PCT)
    else:
        delta = Decimal("0")
    return {
        "capital_nuevo": quantize_money(capital_actual + delta),
        "deuda_delta": Decimal("0"),
        "delta": delta,
        "detalle": {"opcion": opcion},
    }


def resolver_ronda4(capital_actual, deuda_actual, habilidades, colchon_disponible, colchon_usado):
    n_impulsividad = contar_habilidad(habilidades, "impulsividad")
    pct = c.RONDA4_PERDIDA_PCT * (Decimal("1") + n_impulsividad)
    perdida = quantize_money(capital_actual * pct)

    colchon_aplicado = False
    if colchon_disponible and not colchon_usado:
        perdida = Decimal("0")
        colchon_aplicado = True

    deuda_pagada = deuda_actual
    capital_nuevo = capital_actual - perdida - deuda_pagada

    return {
        "capital_nuevo": quantize_money(capital_nuevo),
        "deuda_delta": -deuda_pagada,
        "delta": quantize_money(capital_nuevo - capital_actual),
        "colchon_usado": colchon_aplicado,
        "detalle": {"perdida": str(perdida), "deuda_pagada": str(deuda_pagada), "colchon_aplicado": colchon_aplicado},
    }


def resolver_ronda5(capital_actual, opcion, habilidades, rng):
    n_tolerancia = contar_habilidad(habilidades, "tolerancia_riesgo")
    n_disciplina = contar_habilidad(habilidades, "disciplina_ahorro")
    multiplicador_riesgo = Decimal("1") + n_tolerancia
    pct = Decimal(str(rng.uniform(float(c.RONDA5_RANGO[0]), float(c.RONDA5_RANGO[1]))))
    pct_final = pct * multiplicador_riesgo

    if opcion == "apalancado":
        prestado = capital_actual * c.RONDA5_MULTIPLICADOR_PRESTAMO
        invertido = capital_actual + prestado
        resultado_inversion = quantize_money(invertido * pct_final)
        a_devolver = quantize_money(prestado * (Decimal("1") + c.RONDA5_INTERES_PRESTAMO_PCT))
        capital_nuevo = capital_actual + resultado_inversion - a_devolver
        detalle = {"opcion": opcion, "prestado": str(prestado), "a_devolver": str(a_devolver), "pct_final": str(pct_final)}
    else:
        pct_final += c.DISCIPLINA_AHORRO_BONUS_PP * n_disciplina
        resultado_inversion = quantize_money(capital_actual * pct_final)
        capital_nuevo = capital_actual + resultado_inversion
        detalle = {"opcion": opcion, "pct_final": str(pct_final)}

    return {
        "capital_nuevo": quantize_money(capital_nuevo),
        "deuda_delta": Decimal("0"),
        "delta": quantize_money(capital_nuevo - capital_actual),
        "detalle": detalle,
    }


def resolver_ronda6(capital_actual, habilidades, rng):
    n_impulsividad = contar_habilidad(habilidades, "impulsividad")
    r = rng.random()
    acumulado = 0.0
    evento = c.RONDA6_EVENTOS[-1]
    for ev in c.RONDA6_EVENTOS:
        acumulado += float(ev["prob"])
        if r <= acumulado:
            evento = ev
            break

    monto_final = quantize_money(evento["monto"] * (Decimal("1") + n_impulsividad))
    return {
        "capital_nuevo": quantize_money(capital_actual + monto_final),
        "deuda_delta": Decimal("0"),
        "delta": monto_final,
        "detalle": {"evento": evento["id"], "label": evento["label"], "monto": str(monto_final)},
    }


def resolver_ronda_participante(ronda, opcion, capital_actual, deuda_actual, habilidades,
                                 colchon_disponible, colchon_usado, penalizacion_ronda2, rng):
    habilidades = habilidades or []
    if ronda == 1:
        return resolver_ronda1(capital_actual, opcion, habilidades)
    if ronda == 2:
        return resolver_ronda2(capital_actual, opcion, habilidades, penalizacion_ronda2, rng)
    if ronda == 3:
        return resolver_ronda3(capital_actual, opcion, habilidades)
    if ronda == 4:
        return resolver_ronda4(capital_actual, deuda_actual, habilidades, colchon_disponible, colchon_usado)
    if ronda == 5:
        return resolver_ronda5(capital_actual, opcion, habilidades, rng)
    if ronda == 6:
        return resolver_ronda6(capital_actual, habilidades, rng)
    raise ValueError(f"Ronda inválida: {ronda}")
