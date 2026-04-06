from decimal import Decimal

def calcular_proyecciones(perfil, snapshot):
    """
    Calcula 3 escenarios de evolución patrimonial a 10 años.
    
    NUEVOS ESCENARIOS:
    - Positiva: 7% anual (optimista)
    - Media/Neutral: 5% anual (realista)
    - Negativa: -4% anual (crisis)
    """

    # =========================
    # BASE NUMÉRICA (Desde el Snapshot Seguro)
    # =========================
    ahorro_mensual = max(Decimal(str(snapshot.get("ahorro", 0))), Decimal("0"))
    
    patrimonio_total = Decimal(str(snapshot.get("patrimonio", 0)))
    deuda_total = Decimal(str(snapshot.get("deuda", 0)))
    
    # PERMITIR VALORES NEGATIVOS (no hacer max con 0)
    patrimonio_neto = patrimonio_total - deuda_total

    # =========================
    # FACTORES PERSONALES
    # =========================
    experiencia = Decimal(getattr(perfil, "experiencia_emprendimientos", 0)) / Decimal("10")
    hijos = Decimal(getattr(perfil, "hijos_a_cargo", 0))

    # Penalización suave por carga fija
    factor_riesgo = Decimal("1") - min(hijos * Decimal("0.05"), Decimal("0.2"))

    # =========================
    # TASAS (NUEVAS VERSIONES)
    # =========================
    tasa_media = Decimal("0.05") * factor_riesgo  # 5% neutral
    tasa_positiva = Decimal("0.07") + (experiencia * Decimal("0.03"))  # 7%+ optimista
    tasa_negativa = Decimal("-0.04")  # -4% crisis

    # =========================
    # PROYECCIÓN 10 AÑOS
    # =========================
    positiva = []
    media = []
    negativa = []

    p_pos = patrimonio_neto
    p_med = patrimonio_neto
    p_neg = patrimonio_neto

    # Convertimos el 1 entero a Decimal para evitar choques de tipos
    uno = Decimal("1")

    for _ in range(10):
        p_pos = (p_pos * (uno + tasa_positiva)) + (ahorro_mensual * 12)
        p_med = (p_med * (uno + tasa_media)) + (ahorro_mensual * 12 * Decimal("0.8"))
        p_neg = (p_neg * (uno + tasa_negativa)) + (ahorro_mensual * 12 * Decimal("0.4"))

        positiva.append(float(round(p_pos, 2)))
        media.append(float(round(p_med, 2)))
        negativa.append(float(round(p_neg, 2)))

    return {
        "positiva": positiva,
        "media": media,
        "negativa": negativa,
    }