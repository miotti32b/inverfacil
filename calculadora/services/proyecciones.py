from decimal import Decimal


def calcular_proyecciones(diagnostico):

    """
    Calcula 3 escenarios de evolución patrimonial a 10 años:
    - positiva: mejora de criterio + sistema
    - media: continuidad del patrón actual
    - negativa: inercia + errores no corregidos

    Devuelve listas anuales (10 valores).
    """

    # =========================
    # BASE NUMÉRICA
    # =========================
    ingresos = (
        diagnostico.ingreso_trabajo +
        diagnostico.ingreso_negocio +
        diagnostico.ingreso_rentas +
        diagnostico.ingreso_inversiones +
        diagnostico.ingreso_otros
    )

    gastos = (
        diagnostico.gasto_necesarios +
        diagnostico.gasto_innecesarios +
        diagnostico.gasto_financieros +
        diagnostico.gasto_inversiones
    )

    ahorro_mensual = max(ingresos - gastos, Decimal("0"))

    patrimonio_neto = max(
        diagnostico.patrimonio_total - diagnostico.deuda_total,
        Decimal("0")
    )

    # =========================
    # FACTORES PERSONALES
    # =========================
    perfil = diagnostico.cliente
    experiencia = Decimal(getattr(perfil, "experiencia_emprendimientos", 0)) / Decimal("10")

    hijos = Decimal(getattr(perfil, "hijos_a_cargo", 0))

    # penalización suave por carga fija
    factor_riesgo = Decimal("1") - min(hijos * Decimal("0.05"), Decimal("0.2"))

    # =========================
    # TASAS (criterio > optimismo)
    # =========================
    tasa_media = Decimal("0.03") * factor_riesgo
    tasa_positiva = Decimal("0.07") + (experiencia * Decimal("0.03"))
    tasa_negativa = Decimal("-0.02")

    # =========================
    # PROYECCIÓN 10 AÑOS
    # =========================
    positiva = []
    media = []
    negativa = []

    p_pos = patrimonio_neto
    p_med = patrimonio_neto
    p_neg = patrimonio_neto

    for _ in range(10):
        p_pos = (p_pos * (1 + tasa_positiva)) + (ahorro_mensual * 12)
        p_med = (p_med * (1 + tasa_media)) + (ahorro_mensual * 12 * Decimal("0.8"))
        p_neg = (p_neg * (1 + tasa_negativa)) + (ahorro_mensual * 12 * Decimal("0.4"))

        positiva.append(round(p_pos, 2))
        media.append(round(p_med, 2))
        negativa.append(round(p_neg, 2))

    return {
        "positiva": positiva,
        "media": media,
        "negativa": negativa,
    }
