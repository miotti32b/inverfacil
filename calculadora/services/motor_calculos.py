from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional


def D(value: Any, default: str = "0") -> Decimal:
    if value is None:
        return Decimal(default)
    if isinstance(value, Decimal):
        return value
    try:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def safe_sum(values: Any) -> Decimal:
    if values is None:
        return Decimal("0")
    if isinstance(values, dict):
        return sum((D(v) for v in values.values()), Decimal("0"))
    if isinstance(values, (list, tuple, set)):
        return sum((D(v) for v in values), Decimal("0"))
    return D(values)


def safe_div(numerator: Decimal, denominator: Decimal) -> Optional[Decimal]:
    if denominator in (None, 0):
        return None
    return numerator / denominator


def clamp_ratio(value: Optional[Decimal]) -> Optional[Decimal]:
    if value is None:
        return None
    if value < Decimal("-10"):
        return Decimal("-10")
    if value > Decimal("10"):
        return Decimal("10")
    return value


SNAPSHOT_KEYS = (
    "ingresos",
    "gastos",
    "ahorro",
    "tasa_ahorro",
    "horas_diarias",
    "horas_mensuales",
    "ingreso_por_hora",
    "patrimonio",
    "deuda",
    "ratio_deuda_patrimonio",
    "dependencia_ingreso",
    "margen_error",
    "nivel_sistema",
    "estado_general",
    "ratio_libertad",
    "meses_supervivencia",
    "porcentaje_deuda_toxica",
    "horas_esclavas",
    "porcentaje_inmovilizado",
    "ingreso_trabajo",
    "ingreso_negocio",
    "ingreso_emprendimiento",
    "ingreso_rentas",
    "ingreso_inversiones",
    "peso_trabajo",
    "peso_negocio",
    "peso_emprendimiento",
    "peso_pasivo",
    "gastos_base",
    "aporte_inversion_mensual",
    "porcentaje_inversion_ingreso",
    "excedente_operativo",
    "pat_inmuebles",
    "pat_empresa",
    "pat_vehiculos",
    "pat_inversiones",
    "pat_cash",
    "porcentaje_inmuebles",
    "porcentaje_empresa",
    "porcentaje_vehiculos",
    "porcentaje_inversiones",
    "porcentaje_cash",
    "hay_trampa_inmueble",
    "hay_trampa_empresa",
    "falta_liquidez",
    "nivel_concentracion",
    "estabilidad_laboral",
    "percepcion_estabilidad",
    "conocimiento_financiero",
    "confianza_sistema",
    "indice_prejuicio",
    "nivel_prejuicio",
    "objetivo_principal",
    "palanca_principal",
    "riesgo_principal",
    "perfil_financiero",
    "bloqueos_detectados",
)


PALANCAS_POR_ESTADO = {
    "fragil": "recuperar flujo de caja y bajar fragilidad",
    "presionado": "crear margen y caja defensiva",
    "constructor": "convertir disciplina en sistema",
    "acumulador": "ordenar patrimonio y diversificar",
    "despegando": "escalar con foco y estructura",
}


def _clasificar_prejuicio(confianza_sistema: int, sesgos: list[str]) -> tuple[int, str]:
    score = max(0, len([item for item in sesgos if item and item != "sin_sesgos_relevantes"]) * 2)
    score += max(0, 3 - confianza_sistema)

    if score >= 6:
        return score, "alto"
    if score >= 3:
        return score, "medio"
    return score, "bajo"


def _detectar_bloqueos(diagnostico, excedente_operativo: Decimal, tasa_ahorro: Decimal) -> list[str]:
    bloqueos = []
    for item in getattr(diagnostico, "limitantes_crecimiento", []) or []:
        bloqueos.append(item)
    for item in getattr(diagnostico, "causas_estancamiento", []) or []:
        if item not in bloqueos:
            bloqueos.append(item)
    if excedente_operativo <= 0:
        bloqueos.append("flujo_negativo")
    if tasa_ahorro < Decimal("0.10"):
        bloqueos.append("poco_margen")
    return bloqueos[:5]


def calcular_motor_financiero(diagnostico) -> Dict[str, Any]:
    ingreso_trabajo = D(getattr(diagnostico, "ingreso_trabajo", 0))
    ingreso_negocio = D(getattr(diagnostico, "ingreso_negocio", 0))
    ingreso_emprendimiento = D(getattr(diagnostico, "ingreso_emprendimiento", 0))
    ingreso_rentas = D(getattr(diagnostico, "ingreso_rentas", 0))
    ingreso_inversiones = D(getattr(diagnostico, "ingreso_inversiones", 0))
    ingreso_otros = D(getattr(diagnostico, "ingreso_otros", 0))

    ingresos = (
        ingreso_trabajo
        + ingreso_negocio
        + ingreso_emprendimiento
        + ingreso_rentas
        + ingreso_inversiones
        + ingreso_otros
    )

    peso_trabajo = (safe_div(ingreso_trabajo, ingresos) or Decimal("0")) * 100
    peso_negocio = (safe_div(ingreso_negocio, ingresos) or Decimal("0")) * 100
    peso_emprendimiento = (safe_div(ingreso_emprendimiento, ingresos) or Decimal("0")) * 100
    peso_pasivo = (safe_div((ingreso_rentas + ingreso_inversiones), ingresos) or Decimal("0")) * 100

    gastos_base = (
        D(getattr(diagnostico, "gasto_necesarios", 0))
        + D(getattr(diagnostico, "gasto_innecesarios", 0))
        + D(getattr(diagnostico, "gasto_financieros", 0))
    )
    porcentaje_inversion_ingreso = D(getattr(diagnostico, "gasto_inversiones", 0))
    if porcentaje_inversion_ingreso < 0:
        porcentaje_inversion_ingreso = Decimal("0")
    if porcentaje_inversion_ingreso > 100:
        porcentaje_inversion_ingreso = Decimal("100")
    aporte_inversion_mensual = ingresos * porcentaje_inversion_ingreso / Decimal("100")
    excedente_operativo = ingresos - gastos_base
    ahorro = excedente_operativo - aporte_inversion_mensual
    tasa_ahorro = safe_div(excedente_operativo, ingresos) or Decimal("0")
    gastos = gastos_base

    horas_diarias = D(getattr(diagnostico, "horas_trabajadas", 0))
    horas_mensuales = horas_diarias * Decimal("30")
    ingreso_por_hora = safe_div(ingresos, Decimal("160")) or Decimal("0")

    patrimonio_comp = getattr(diagnostico, "patrimonio_comp", {}) or {}
    pat_inmuebles = D(patrimonio_comp.get("inmuebles", 0))
    pat_empresa = D(patrimonio_comp.get("empresa", 0))
    pat_vehiculos = D(patrimonio_comp.get("vehiculos", 0))
    pat_inversiones = D(patrimonio_comp.get("inversiones", 0))
    pat_cash = D(patrimonio_comp.get("cash", patrimonio_comp.get("efectivo", 0)))

    patrimonio_total = D(getattr(diagnostico, "patrimonio_total", 0))
    patrimonio_calculado = pat_inmuebles + pat_empresa + pat_vehiculos + pat_inversiones + pat_cash
    patrimonio_total = patrimonio_total if patrimonio_total > 0 else patrimonio_calculado

    porcentaje_inmuebles = (safe_div(pat_inmuebles, patrimonio_total) or Decimal("0")) * 100
    porcentaje_empresa = (safe_div(pat_empresa, patrimonio_total) or Decimal("0")) * 100
    porcentaje_vehiculos = (safe_div(pat_vehiculos, patrimonio_total) or Decimal("0")) * 100
    porcentaje_inversiones = (safe_div(pat_inversiones, patrimonio_total) or Decimal("0")) * 100
    porcentaje_cash = (safe_div(pat_cash, patrimonio_total) or Decimal("0")) * 100

    deuda_comp = getattr(diagnostico, "deuda_comp", {}) or {}
    deuda_total = D(getattr(diagnostico, "deuda_total", 0))
    deuda_total = deuda_total if deuda_total > 0 else safe_sum(deuda_comp)
    ratio_deuda_patrimonio = clamp_ratio(safe_div(deuda_total, patrimonio_total))

    deuda_tarjetas = D(deuda_comp.get("tarjetas", deuda_comp.get("deu_tarjetas", 0)))
    deuda_prestamos = D(deuda_comp.get("prestamos", deuda_comp.get("deu_prestamos", 0)))
    deuda_impuestos = D(deuda_comp.get("impuestos", deuda_comp.get("deu_impuestos", 0)))
    deuda_toxica = deuda_tarjetas + deuda_prestamos + deuda_impuestos
    porcentaje_deuda_toxica = (safe_div(deuda_toxica, deuda_total) or Decimal("0")) * 100

    ingresos_pasivos = ingreso_rentas + ingreso_inversiones
    ratio_libertad = safe_div(ingresos_pasivos, gastos) or Decimal("0")
    liquidez = pat_cash + pat_inversiones
    meses_supervivencia = safe_div(liquidez, gastos) or Decimal("0")
    horas_esclavas = safe_div(gastos, ingreso_por_hora) or Decimal("0")

    activos_inmovilizados = pat_vehiculos
    if ingreso_rentas == 0:
        activos_inmovilizados += pat_inmuebles
    porcentaje_inmovilizado = (safe_div(activos_inmovilizados, patrimonio_total) or Decimal("0")) * 100

    concentracion_max = max(
        porcentaje_inmuebles,
        porcentaje_empresa,
        porcentaje_vehiculos,
        porcentaje_inversiones,
        porcentaje_cash,
    )
    if concentracion_max > Decimal("80"):
        nivel_concentracion = "extrema"
    elif concentracion_max > Decimal("60"):
        nivel_concentracion = "alta"
    elif concentracion_max > Decimal("40"):
        nivel_concentracion = "media"
    else:
        nivel_concentracion = "baja"

    fuentes = sum(
        1
        for value in (
            ingreso_trabajo,
            ingreso_negocio,
            ingreso_emprendimiento,
            ingreso_rentas,
            ingreso_inversiones,
        )
        if value > 0
    )
    if fuentes <= 1:
        dependencia_ingreso = "alta"
    elif fuentes == 2:
        dependencia_ingreso = "media"
    else:
        dependencia_ingreso = "baja"

    if ingresos <= 0 or ahorro <= 0:
        margen_error = "bajo"
    elif tasa_ahorro < Decimal("0.15"):
        margen_error = "medio"
    else:
        margen_error = "alto"

    estabilidad_laboral = getattr(diagnostico, "estabilidad_laboral", "") or "sin_definir"
    percepcion_estabilidad = int(getattr(diagnostico, "percepcion_estabilidad", 0) or 0)
    conocimiento_financiero = int(getattr(diagnostico, "conocimiento_financiero", 0) or 0)
    confianza_sistema = int(getattr(diagnostico, "confianza_sistema", 0) or 0)
    sesgos_sistema = list(getattr(diagnostico, "sesgos_sistema", []) or [])
    indice_prejuicio, nivel_prejuicio = _clasificar_prejuicio(confianza_sistema, sesgos_sistema)

    if excedente_operativo <= 0 or meses_supervivencia < Decimal("1"):
        estado_general = "fragil"
    elif tasa_ahorro < Decimal("0.10") or percepcion_estabilidad <= 2:
        estado_general = "presionado"
    elif tasa_ahorro >= Decimal("0.25") and peso_pasivo >= Decimal("15"):
        estado_general = "acumulador"
    elif tasa_ahorro >= Decimal("0.15"):
        estado_general = "constructor"
    else:
        estado_general = "despegando"

    if indice_prejuicio >= 6 or confianza_sistema <= 2:
        nivel_sistema = "rechazo"
    elif conocimiento_financiero <= 2:
        nivel_sistema = "novato"
    elif conocimiento_financiero >= 4 and confianza_sistema >= 4:
        nivel_sistema = "estrategico"
    else:
        nivel_sistema = "aprendiendo"

    hay_trampa_inmueble = porcentaje_inmuebles > Decimal("70") and ratio_libertad < Decimal("0.20")
    hay_trampa_empresa = porcentaje_empresa > Decimal("60") and (peso_negocio + peso_emprendimiento) > Decimal("35")
    falta_liquidez = (porcentaje_cash + porcentaje_inversiones) < Decimal("10") and patrimonio_total > 0

    objetivos = list(getattr(diagnostico, "objetivos_ordenados", []) or [])
    objetivo_principal = objetivos[0] if objetivos else "independencia_financiera"

    if excedente_operativo <= 0:
        riesgo_principal = "quedarte sin margen operativo"
    elif ahorro < 0:
        riesgo_principal = "invertir por encima de la caja que hoy puedes sostener"
    elif porcentaje_deuda_toxica >= Decimal("40"):
        riesgo_principal = "que la deuda cara te siga frenando"
    elif falta_liquidez:
        riesgo_principal = "tener patrimonio pero sin caja real"
    elif indice_prejuicio >= 6:
        riesgo_principal = "quedarte inmovilizado por desconfianza"
    else:
        riesgo_principal = "crecer sin sistema claro"

    bloqueos_detectados = _detectar_bloqueos(diagnostico, excedente_operativo, tasa_ahorro)
    perfil_financiero = f"{estado_general}_{nivel_sistema}"
    palanca_principal = PALANCAS_POR_ESTADO.get(estado_general, "ordenar tu sistema financiero")

    snapshot: Dict[str, Any] = {
        "ingresos": ingresos,
        "gastos": gastos,
        "ahorro": ahorro,
        "tasa_ahorro": tasa_ahorro,
        "horas_diarias": horas_diarias,
        "horas_mensuales": horas_mensuales,
        "ingreso_por_hora": ingreso_por_hora,
        "patrimonio": patrimonio_total,
        "deuda": deuda_total,
        "ratio_deuda_patrimonio": ratio_deuda_patrimonio,
        "dependencia_ingreso": dependencia_ingreso,
        "margen_error": margen_error,
        "nivel_sistema": nivel_sistema,
        "estado_general": estado_general,
        "ratio_libertad": ratio_libertad,
        "meses_supervivencia": meses_supervivencia,
        "porcentaje_deuda_toxica": porcentaje_deuda_toxica,
        "horas_esclavas": horas_esclavas,
        "porcentaje_inmovilizado": porcentaje_inmovilizado,
        "ingreso_trabajo": ingreso_trabajo,
        "ingreso_negocio": ingreso_negocio,
        "ingreso_emprendimiento": ingreso_emprendimiento,
        "ingreso_rentas": ingreso_rentas,
        "ingreso_inversiones": ingreso_inversiones,
        "peso_trabajo": peso_trabajo,
        "peso_negocio": peso_negocio,
        "peso_emprendimiento": peso_emprendimiento,
        "peso_pasivo": peso_pasivo,
        "gastos_base": gastos_base,
        "aporte_inversion_mensual": aporte_inversion_mensual,
        "porcentaje_inversion_ingreso": porcentaje_inversion_ingreso,
        "excedente_operativo": excedente_operativo,
        "pat_inmuebles": pat_inmuebles,
        "pat_empresa": pat_empresa,
        "pat_vehiculos": pat_vehiculos,
        "pat_inversiones": pat_inversiones,
        "pat_cash": pat_cash,
        "porcentaje_inmuebles": porcentaje_inmuebles,
        "porcentaje_empresa": porcentaje_empresa,
        "porcentaje_vehiculos": porcentaje_vehiculos,
        "porcentaje_inversiones": porcentaje_inversiones,
        "porcentaje_cash": porcentaje_cash,
        "hay_trampa_inmueble": hay_trampa_inmueble,
        "hay_trampa_empresa": hay_trampa_empresa,
        "falta_liquidez": falta_liquidez,
        "nivel_concentracion": nivel_concentracion,
        "estabilidad_laboral": estabilidad_laboral,
        "percepcion_estabilidad": percepcion_estabilidad,
        "conocimiento_financiero": conocimiento_financiero,
        "confianza_sistema": confianza_sistema,
        "indice_prejuicio": indice_prejuicio,
        "nivel_prejuicio": nivel_prejuicio,
        "objetivo_principal": objetivo_principal,
        "palanca_principal": palanca_principal,
        "riesgo_principal": riesgo_principal,
        "perfil_financiero": perfil_financiero,
        "bloqueos_detectados": bloqueos_detectados,
    }

    for key in SNAPSHOT_KEYS:
        snapshot.setdefault(key, None)

    return snapshot


def format_currency(value: Decimal, decimals: int = 0) -> str:
    if value is None:
        return "$0"

    amount = float(value)
    if decimals == 0:
        return f"${int(round(amount)):,}".replace(",", ".")
    return f"${amount:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def snapshot_to_display(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    display = {}

    currency_keys = [
        "ingresos",
        "gastos",
        "ahorro",
        "patrimonio",
        "deuda",
        "ingreso_trabajo",
        "ingreso_negocio",
        "ingreso_emprendimiento",
        "ingreso_rentas",
        "ingreso_inversiones",
        "ingreso_por_hora",
        "gastos_base",
        "aporte_inversion_mensual",
        "pat_inmuebles",
        "pat_empresa",
        "pat_vehiculos",
        "pat_inversiones",
        "pat_cash",
    ]
    percentage_keys = [
        "tasa_ahorro",
        "ratio_deuda_patrimonio",
        "ratio_libertad",
        "porcentaje_deuda_toxica",
        "porcentaje_inmovilizado",
        "peso_trabajo",
        "peso_negocio",
        "peso_emprendimiento",
        "peso_pasivo",
        "porcentaje_inmuebles",
        "porcentaje_empresa",
        "porcentaje_vehiculos",
        "porcentaje_inversiones",
        "porcentaje_cash",
        "porcentaje_inversion_ingreso",
    ]

    for key, value in snapshot.items():
        if key in currency_keys:
            display[key] = format_currency(D(value))
        elif key in percentage_keys:
            display[key] = f"{float(value):.1f}%"
        elif key in ["horas_diarias", "horas_mensuales", "horas_esclavas", "meses_supervivencia"]:
            display[key] = f"{float(value):.1f}" if value else "0"
        else:
            display[key] = value

    return display


def snapshot_to_json_safe(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for key, value in snapshot.items():
        if isinstance(value, Decimal):
            out[key] = float(value)
        else:
            out[key] = value
    return out
