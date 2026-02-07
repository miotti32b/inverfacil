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
        # evitar Decimal(float) directo por problemas de precisión
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
    # No clamp agresivo, solo control básico
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
)


def calcular_motor_financiero(diagnostico) -> Dict[str, Any]:
    """
    Motor único de cálculo financiero.

    Devuelve un snapshot **estable** y **completo**, listo para:
    - IA
    - templates
    - cache/hash

    Regla de oro:
    - Siempre devuelve las mismas claves (SNAPSHOT_KEYS)
    - Tipos consistentes (Decimal / str / None)
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
    # En tu modelo real el campo parece ser horas_trabajadas (no horas_diarias)
    horas_diarias = D(getattr(diagnostico, "horas_trabajadas", 0))
    horas_mensuales = horas_diarias * Decimal("30")

    ingreso_por_hora = safe_div(ingresos, horas_mensuales)  # puede ser None si horas=0

    # ----------------------------
    # PATRIMONIO / DEUDA (JSON)
    # ----------------------------
    patrimonio_comp = getattr(diagnostico, "patrimonio_comp", None)
    deuda_comp = getattr(diagnostico, "deuda_comp", None)

    patrimonio_total = safe_sum(patrimonio_comp)
    deuda_total = safe_sum(deuda_comp)

    ratio_deuda_patrimonio = safe_div(deuda_total, patrimonio_total)
    ratio_deuda_patrimonio = clamp_ratio(ratio_deuda_patrimonio)

    # ----------------------------
    # DEPENDENCIA DE INGRESO
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

    # ----------------------------
    # MARGEN DE ERROR
    # ----------------------------
    if ingresos <= 0 or ahorro <= 0:
        margen_error = "bajo"
    elif tasa_ahorro < Decimal("0.15"):
        margen_error = "medio"
    else:
        margen_error = "alto"

    # ----------------------------
    # NIVEL DE SISTEMA
    # ----------------------------
    if ahorro <= 0:
        nivel_sistema = "inexistente"
    elif dependencia_ingreso == "alta":
        nivel_sistema = "basico"
    else:
        nivel_sistema = "avanzado"

    # ----------------------------
    # ESTADO GENERAL
    # ----------------------------
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
    }

    # Validación dura: nunca faltan claves
    for k in SNAPSHOT_KEYS:
        snapshot.setdefault(k, None)

    return snapshot


def snapshot_to_json_safe(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte Decimal -> float (o str si preferís) para:
    - json.dumps
    - hashing
    - mandar a IA
    """
    out = {}
    for k, v in snapshot.items():
        if isinstance(v, Decimal):
            out[k] = float(v)
        else:
            out[k] = v
    return out
