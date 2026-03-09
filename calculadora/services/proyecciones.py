from decimal import Decimal

def calcular_proyecciones(perfil, snapshot):
    """
    Calcula 3 escenarios de evolución patrimonial a 10 años usando 
    los datos seguros ya calculados por el motor financiero.
    """

    # =========================
    # BASE NUMÉRICA (Desde el Snapshot Seguro)
    # =========================
    # Usamos str() antes de Decimal() para evitar errores de precisión de punto flotante
    ahorro_mensual = max(Decimal(str(snapshot.get("ahorro", 0))), Decimal("0"))
    
    patrimonio_total = Decimal(str(snapshot.get("patrimonio", 0)))
    deuda_total = Decimal(str(snapshot.get("deuda", 0)))
    
    patrimonio_neto = max(patrimonio_total - deuda_total, Decimal("0"))

    # =========================
    # FACTORES PERSONALES
    # =========================
    experiencia = Decimal(getattr(perfil, "experiencia_emprendimientos", 0)) / Decimal("10")
    hijos = Decimal(getattr(perfil, "hijos_a_cargo", 0))

    # Penalización suave por carga fija
    factor_riesgo = Decimal("1") - min(hijos * Decimal("0.05"), Decimal("0.2"))

    # =========================
    # TASAS (Criterio Conservador)
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

    # Convertimos el 1 entero a Decimal para evitar choques de tipos en Python
    uno = Decimal("1")

    for _ in range(10):
        p_pos = (p_pos * (uno + tasa_positiva)) + (ahorro_mensual * 12)
        p_med = (p_med * (uno + tasa_media)) + (ahorro_mensual * 12 * Decimal("0.8"))
        p_neg = (p_neg * (uno + tasa_negativa)) + (ahorro_mensual * 12 * Decimal("0.4"))

        positiva.append(round(p_pos, 2))
        media.append(round(p_med, 2))
        negativa.append(round(p_neg, 2))

    return {
        "positiva": positiva,
        "media": media,
        "negativa": negativa,
    }