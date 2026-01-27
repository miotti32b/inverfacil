def construir_snapshot(diagnostico, ingresos, gastos):
    ahorro = ingresos - gastos if ingresos else 0

    patrimonio = diagnostico.patrimonio_total or 0
    deuda = diagnostico.deuda_total or 0

    # ---------- Margen de error ----------
    if ingresos <= 0 or ahorro <= 0:
        margen_error = "bajo"
    elif ahorro / ingresos < 0.15:
        margen_error = "medio"
    else:
        margen_error = "alto"

    # ---------- Dependencia ingreso ----------
    fuentes = 0
    if diagnostico.ingreso_trabajo > 0: fuentes += 1
    if diagnostico.ingreso_negocio > 0: fuentes += 1
    if diagnostico.ingreso_rentas > 0: fuentes += 1
    if diagnostico.ingreso_inversiones > 0: fuentes += 1

    if fuentes <= 1:
        dependencia_ingreso = "alta"
    elif fuentes == 2:
        dependencia_ingreso = "media"
    else:
        dependencia_ingreso = "baja"

    # ---------- Nivel de sistema ----------
    if ahorro <= 0:
        nivel_sistema = "inexistente"
    elif dependencia_ingreso == "alta":
        nivel_sistema = "basico"
    else:
        nivel_sistema = "avanzado"

    # ---------- Estado general ----------
    if margen_error == "bajo" or deuda > patrimonio:
        estado_general = "fragil"
    elif nivel_sistema == "avanzado":
        estado_general = "solido"
    else:
        estado_general = "intermedio"

    return {
        "estado_general": estado_general,
        "margen_error": margen_error,
        "dependencia_ingreso": dependencia_ingreso,
        "nivel_sistema": nivel_sistema,
    }
