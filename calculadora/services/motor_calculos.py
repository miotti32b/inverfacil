# calculadora/services/motor_calculos.py
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

# ----------------------------
# Helpers seguros
# ----------------------------
def D(x: Any, default: str = "0") -> Decimal:
    """
    Convierte lo que venga a Decimal de forma segura.
    - None -> 0
    - float/int/str/Decimal -> Decimal
    """
    if x is None:
        return Decimal(default)
    if isinstance(x, Decimal):
        return x
    try:
        if isinstance(x, float):
            return Decimal(str(x))
        return Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)

def safe_sum(values: Any) -> Decimal:
    """
    Suma segura para dict/list/iterables.
    - dict -> suma values()
    - list/tuple/set -> suma elementos
    - None -> 0
    """
    if values is None:
        return Decimal("0")
    if isinstance(values, dict):
        return sum((D(v) for v in values.values()), Decimal("0"))
    if isinstance(values, (list, tuple, set)):
        return sum((D(v) for v in values), Decimal("0"))
    return D(values)

def safe_div(n: Decimal, d: Decimal) -> Optional[Decimal]:
    if d is None:
        return None
    if d == 0:
        return None
    return n / d

def clamp_ratio(x: Optional[Decimal]) -> Optional[Decimal]:
    """
    Por si tu data es rara, evitamos ratios absurdos.
    (opcional, pero ayuda a no romper UI/IA)
    """
    if x is None:
        return None
    if x < Decimal("-10"):
        return Decimal("-10")
    if x > Decimal("10"):
        return Decimal("10")
    return x

# ----------------------------
# CONTRATO ÚNICO DE SNAPSHOT
# ----------------------------
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
    # --- NUEVOS RATIOS KILLER ---
    "ratio_libertad",
    "meses_supervivencia",
    "porcentaje_deuda_toxica",
    "horas_esclavas",
    "porcentaje_inmovilizado",
)

def calcular_motor_financiero(diagnostico) -> Dict[str, Any]:
    """
    Motor único de cálculo financiero.
    Devuelve un snapshot **estable** y **completo**.
    """

    # ----------------------------
    # INGRESOS / GASTOS (Decimal)
    # ----------------------------
    ingresos = (
        D(getattr(diagnostico, "ingreso_trabajo", 0)) +
        D(getattr(diagnostico, "ingreso_negocio", 0)) +
        D(getattr(diagnostico, "ingreso_rentas", 0)) +
        D(getattr(diagnostico, "ingreso_inversiones", 0)) +
        D(getattr(diagnostico, "ingreso_otros", 0))
    )

    gastos = (
        D(getattr(diagnostico, "gasto_necesarios", 0)) +
        D(getattr(diagnostico, "gasto_innecesarios", 0)) +
        D(getattr(diagnostico, "gasto_financieros", 0)) +
        D(getattr(diagnostico, "gasto_inversiones", 0))
    )

    ahorro = ingresos - gastos
    tasa_ahorro = safe_div(ahorro, ingresos) or Decimal("0")

    # ----------------------------
    # TIEMPO
    # ----------------------------
    horas_diarias = D(getattr(diagnostico, "horas_trabajadas", 0))
    horas_mensuales = horas_diarias * Decimal("30")

    ingreso_por_hora = safe_div(ingresos, horas_mensuales)

    # ----------------------------
    # PATRIMONIO / DEUDA (Totales)
    # ----------------------------
    patrimonio_comp = getattr(diagnostico, "patrimonio_comp", None)
    deuda_comp = getattr(diagnostico, "deuda_comp", None)

    patrimonio_total = safe_sum(patrimonio_comp)
    deuda_total = safe_sum(deuda_comp)

    ratio_deuda_patrimonio = safe_div(deuda_total, patrimonio_total)
    ratio_deuda_patrimonio = clamp_ratio(ratio_deuda_patrimonio)

    # ----------------------------
    # RATIOS KILLER (Psicología Financiera)
    # ----------------------------
    # 1. Ratio de Libertad (Cobertura Pasiva)
    ingresos_pasivos = D(getattr(diagnostico, "ingreso_rentas", 0)) + D(getattr(diagnostico, "ingreso_inversiones", 0))
    ratio_libertad = safe_div(ingresos_pasivos, gastos) or Decimal("0")

    # 2. Meses de Supervivencia (Liquidez Real)
    liquidez = D(getattr(diagnostico, "pat_cash", 0)) + D(getattr(diagnostico, "pat_inversiones", 0))
    meses_supervivencia = safe_div(liquidez, gastos) or Decimal("0")

    # 3. Índice de Deuda Tóxica
    deuda_toxica = (
        D(getattr(diagnostico, "deu_tarjetas", 0)) + 
        D(getattr(diagnostico, "deu_prestamos", 0)) + 
        D(getattr(diagnostico, "deu_impuestos", 0))
    )
    porcentaje_deuda_toxica = safe_div(deuda_toxica, deuda_total) or Decimal("0")

    # 4. Horas Esclavas
    if ingreso_por_hora and ingreso_por_hora > 0:
        horas_esclavas = safe_div(gastos, ingreso_por_hora) or Decimal("0")
    else:
        horas_esclavas = Decimal("0")

    # 5. Falsa Riqueza (Capital Inmovilizado)
    activos_inmovilizados = D(getattr(diagnostico, "pat_vehiculos", 0))
    if D(getattr(diagnostico, "ingreso_rentas", 0)) == 0:
        activos_inmovilizados += D(getattr(diagnostico, "pat_inmuebles", 0))
    
    porcentaje_inmovilizado = safe_div(activos_inmovilizados, patrimonio_total) or Decimal("0")

    # ----------------------------
    # DEPENDENCIA Y NIVELES (Cualitativos)
    # ----------------------------
    fuentes = 0
    if D(getattr(diagnostico, "ingreso_trabajo", 0)) > 0: fuentes += 1
    if D(getattr(diagnostico, "ingreso_negocio", 0)) > 0: fuentes += 1
    if D(getattr(diagnostico, "ingreso_rentas", 0)) > 0: fuentes += 1
    if D(getattr(diagnostico, "ingreso_inversiones", 0)) > 0: fuentes += 1

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

    if ahorro <= 0:
        nivel_sistema = "inexistente"
    elif dependencia_ingreso == "alta":
        nivel_sistema = "basico"
    else:
        nivel_sistema = "avanzado"

    if margen_error == "bajo" or (patrimonio_total > 0 and deuda_total > patrimonio_total):
        estado_general = "fragil"
    elif nivel_sistema == "avanzado":
        estado_general = "solido"
    else:
        estado_general = "intermedio"

    # ----------------------------
    # SNAPSHOT FINAL (COMPLETO)
    # ----------------------------
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

        # Los ratios nuevos
        "ratio_libertad": ratio_libertad,
        "meses_supervivencia": meses_supervivencia,
        "porcentaje_deuda_toxica": porcentaje_deuda_toxica,
        "horas_esclavas": horas_esclavas,
        "porcentaje_inmovilizado": porcentaje_inmovilizado,
    }

    # Validación dura: nunca faltan claves
    for k in SNAPSHOT_KEYS:
        snapshot.setdefault(k, None)

    return snapshot

def snapshot_to_json_safe(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte Decimal -> float para json.dumps
    """
    out = {}
    for k, v in snapshot.items():
        if isinstance(v, Decimal):
            out[k] = float(v)
        else:
            out[k] = v
    return out