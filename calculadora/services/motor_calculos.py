# calculadora/services/motor_calculos.py


def calcular_motor_financiero(diagnostico):
    """
    Motor único de cálculo financiero.
    Devuelve un snapshot listo para:
    - IA
    - templates
    - cache
    """

    # =========================
    # INGRESOS / GASTOS
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

    ahorro = ingresos - gastos

    # =========================
    # TIEMPO
    # =========================
    horas_diarias = diagnostico.horas_diarias or 0
    horas_mensuales = horas_diarias * 22 if horas_diarias > 0 else 0

    ingreso_por_hora = (
        ingresos / horas_mensuales
        if horas_mensuales > 0 else None
    )

    # =========================
    # PATRIMONIO
    # =========================
    patrimonio_total = sum(diagnostico.patrimonio_comp.values())
    deuda_total = sum(diagnostico.deuda_comp.values())

    ratio_deuda_patrimonio = (
        deuda_total / patrimonio_total
        if patrimonio_total > 0 else None
    )

    tasa_ahorro = (
        ahorro / ingresos
        if ingresos > 0 else 0
    )

    # =========================
    # DEPENDENCIA INGRESO
    # =========================
    fuentes = sum([
        diagnostico.ingreso_trabajo > 0,
        diagnostico.ingreso_negocio > 0,
        diagnostico.ingreso_rentas > 0,
        diagnostico.ingreso_inversiones > 0,
    ])

    if fuentes <= 1:
        dependencia_ingreso = "alta"
    elif fuentes == 2:
        dependencia_ingreso = "media"
    else:
        dependencia_ingreso = "baja"

    # =========================
    # MARGEN DE ERROR
    # =========================
    if ingresos <= 0 or ahorro <= 0:
        margen_error = "bajo"
    elif tasa_ahorro < 0.15:
        margen_error = "medio"
    else:
        margen_error = "alto"

    # =========================
    # NIVEL DE SISTEMA
    # =========================
    if ahorro <= 0:
        nivel_sistema = "inexistente"
    elif dependencia_ingreso == "alta":
        nivel_sistema = "basico"
    else:
        nivel_sistema = "avanzado"

    # =========================
    # ESTADO GENERAL
    # =========================
    if margen_error == "bajo" or (patrimonio_total and deuda_total > patrimonio_total):
        estado_general = "fragil"
    elif nivel_sistema == "avanzado":
        estado_general = "solido"
    else:
        estado_general = "intermedio"

    # =========================
    # SNAPSHOT FINAL
    # =========================
    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "ahorro": ahorro,
        "tasa_ahorro": tasa_ahorro,

        "horas_diarias": horas_diarias,
        "ingreso_por_hora": ingreso_por_hora,

        "patrimonio": patrimonio_total,
        "deuda": deuda_total,
        "ratio_deuda_patrimonio": ratio_deuda_patrimonio,

        "dependencia_ingreso": dependencia_ingreso,
        "margen_error": margen_error,
        "nivel_sistema": nivel_sistema,
        "estado_general": estado_general,
    }
