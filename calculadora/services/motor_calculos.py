# calculadora/services/motor_calculos_mejorado.py
"""
Versión mejorada con:
- Detección de concentración de patrimonio
- Análisis de fuentes de ingreso
- Métricas visuales sin decimales
- Nuevos ratios para la IA
"""

from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

# ----------------------------
# Helpers seguros (igual que antes)
# ----------------------------
def D(x: Any, default: str = "0") -> Decimal:
    """Convierte lo que venga a Decimal de forma segura."""
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
    """Suma segura para dict/list/iterables."""
    if values is None:
        return Decimal("0")
    if isinstance(values, dict):
        return sum((D(v) for v in values.values()), Decimal("0"))
    if isinstance(values, (list, tuple, set)):
        return sum((D(v) for v in values), Decimal("0"))
    return D(values)

def safe_div(n: Decimal, d: Decimal) -> Optional[Decimal]:
    if d is None or d == 0:
        return None
    return n / d

def clamp_ratio(x: Optional[Decimal]) -> Optional[Decimal]:
    """Evita ratios absurdos."""
    if x is None:
        return None
    if x < Decimal("-10"):
        return Decimal("-10")
    if x > Decimal("10"):
        return Decimal("10")
    return x

# ----------------------------
# KEYS DEL SNAPSHOT MEJORADO
# ----------------------------
SNAPSHOT_KEYS = (
    # Base
    "ingresos",
    "gastos",
    "ahorro",
    "tasa_ahorro",
    
    # Tiempo
    "horas_diarias",
    "horas_mensuales",
    "ingreso_por_hora",
    
    # Patrimonio y Deuda
    "patrimonio",
    "deuda",
    "ratio_deuda_patrimonio",
    
    # Cualitativos
    "dependencia_ingreso",
    "margen_error",
    "nivel_sistema",
    "estado_general",
    
    # RATIOS KILLER
    "ratio_libertad",
    "meses_supervivencia",
    "porcentaje_deuda_toxica",
    "horas_esclavas",
    "porcentaje_inmovilizado",
    
    # 🆕 NUEVOS ANÁLISIS
    "ingreso_trabajo",
    "ingreso_negocio",
    "ingreso_rentas",
    "ingreso_inversiones",
    
    "peso_trabajo",
    "peso_negocio",
    "peso_pasivo",
    
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
)

# ----------------------------
# MOTOR DE CÁLCULO MEJORADO
# ----------------------------

def calcular_motor_financiero(diagnostico) -> Dict[str, Any]:
    """
    Motor completo con análisis estratégico incluido.
    """
    
    # ========================
    # INGRESOS (Segmentados)
    # ========================
    ingreso_trabajo = D(getattr(diagnostico, "ingreso_trabajo", 0))
    ingreso_negocio = D(getattr(diagnostico, "ingreso_negocio", 0))
    ingreso_rentas = D(getattr(diagnostico, "ingreso_rentas", 0))
    ingreso_inversiones = D(getattr(diagnostico, "ingreso_inversiones", 0))
    ingreso_otros = D(getattr(diagnostico, "ingreso_otros", 0))
    
    ingresos = (ingreso_trabajo + ingreso_negocio + ingreso_rentas + 
                ingreso_inversiones + ingreso_otros)
    
    # Pesos
    peso_trabajo = safe_div(ingreso_trabajo, ingresos) * 100 if ingresos > 0 else Decimal("0")
    peso_negocio = safe_div(ingreso_negocio, ingresos) * 100 if ingresos > 0 else Decimal("0")
    peso_pasivo = safe_div((ingreso_rentas + ingreso_inversiones), ingresos) * 100 if ingresos > 0 else Decimal("0")
    
    # ========================
    # GASTOS
    # ========================
    gastos = (
        D(getattr(diagnostico, "gasto_necesarios", 0)) +
        D(getattr(diagnostico, "gasto_innecesarios", 0)) +
        D(getattr(diagnostico, "gasto_financieros", 0)) +
        D(getattr(diagnostico, "gasto_inversiones", 0))
    )
    
    ahorro = ingresos - gastos
    tasa_ahorro = safe_div(ahorro, ingresos) or Decimal("0")
    
    # ========================
    # TIEMPO
    # ========================
    horas_diarias = D(getattr(diagnostico, "horas_trabajadas", 0))
    horas_mensuales = horas_diarias * Decimal("22")
    ingreso_por_hora = safe_div(ingresos, horas_mensuales)
    
    # ========================
    # PATRIMONIO (Segmentado) - LEER DE JSONFIELD patrimonio_comp
    # ========================
    patrimonio_comp = getattr(diagnostico, "patrimonio_comp", {}) or {}
    
    pat_inmuebles = D(patrimonio_comp.get("pat_inmuebles", 0))
    pat_empresa = D(patrimonio_comp.get("pat_empresa", 0))
    pat_vehiculos = D(patrimonio_comp.get("pat_vehiculos", 0))
    pat_inversiones = D(patrimonio_comp.get("pat_inversiones", 0))
    pat_cash = D(patrimonio_comp.get("pat_cash", 0))
    
    patrimonio_total = pat_inmuebles + pat_empresa + pat_vehiculos + pat_inversiones + pat_cash
    
    # Porcentajes
    porcentaje_inmuebles = safe_div(pat_inmuebles, patrimonio_total) * 100 if patrimonio_total > 0 else Decimal("0")
    porcentaje_empresa = safe_div(pat_empresa, patrimonio_total) * 100 if patrimonio_total > 0 else Decimal("0")
    porcentaje_vehiculos = safe_div(pat_vehiculos, patrimonio_total) * 100 if patrimonio_total > 0 else Decimal("0")
    porcentaje_inversiones = safe_div(pat_inversiones, patrimonio_total) * 100 if patrimonio_total > 0 else Decimal("0")
    porcentaje_cash = safe_div(pat_cash, patrimonio_total) * 100 if patrimonio_total > 0 else Decimal("0")
    
    # ========================
    # DEUDA
    # ========================
    deuda_comp = getattr(diagnostico, "deuda_comp", None)
    deuda_total = safe_sum(deuda_comp)
    ratio_deuda_patrimonio = safe_div(deuda_total, patrimonio_total)
    ratio_deuda_patrimonio = clamp_ratio(ratio_deuda_patrimonio)
    
    # ========================
    # RATIOS KILLER
    # ========================
    ingresos_pasivos = ingreso_rentas + ingreso_inversiones
    ratio_libertad = safe_div(ingresos_pasivos, gastos) or Decimal("0")
    
    liquidez = pat_cash + pat_inversiones
    meses_supervivencia = safe_div(liquidez, gastos) or Decimal("0")
    
    # Leer deuda tóxica desde JSONField deuda_comp
    deuda_tarjetas = D(deuda_comp.get("deu_tarjetas", 0) if deuda_comp else 0)
    deuda_prestamos = D(deuda_comp.get("deu_prestamos", 0) if deuda_comp else 0)
    deuda_impuestos = D(deuda_comp.get("deu_impuestos", 0) if deuda_comp else 0)
    
    deuda_toxica = deuda_tarjetas + deuda_prestamos + deuda_impuestos
    porcentaje_deuda_toxica = (safe_div(deuda_toxica, deuda_total) or Decimal("0")) * 100
    
    if ingreso_por_hora and ingreso_por_hora > 0:
        horas_esclavas = safe_div(gastos, ingreso_por_hora) or Decimal("0")
    else:
        horas_esclavas = Decimal("0")
    
    # Capital inmovilizado
    activos_inmovilizados = pat_vehiculos
    if ingreso_rentas == 0:
        activos_inmovilizados += pat_inmuebles
    
    porcentaje_inmovilizado = safe_div(activos_inmovilizados, patrimonio_total) or Decimal("0")
    
    # ========================
    # ANÁLISIS ESTRATÉGICO
    # ========================
    es_emprendedor = peso_negocio > Decimal("40")
    
    hay_trampa_inmueble = (porcentaje_inmuebles > Decimal("80") and 
                          ratio_libertad < Decimal("0.15"))
    
    hay_trampa_empresa = (porcentaje_empresa > Decimal("60") and 
                         es_emprendedor and 
                         pat_empresa > 0)
    
    falta_liquidez = (porcentaje_cash + porcentaje_inversiones < Decimal("10") and 
                     patrimonio_total > 0)
    
    # Nivel de concentración
    concentracion_max = max(
        porcentaje_inmuebles,
        porcentaje_empresa,
        porcentaje_vehiculos,
        porcentaje_inversiones,
        porcentaje_cash
    )
    
    if concentracion_max > Decimal("80"):
        nivel_concentracion = "extrema"
    elif concentracion_max > Decimal("60"):
        nivel_concentracion = "alta"
    elif concentracion_max > Decimal("40"):
        nivel_concentracion = "media"
    else:
        nivel_concentracion = "baja"
    
    # ========================
    # DEPENDENCIA Y NIVELES
    # ========================
    fuentes = 0
    if ingreso_trabajo > 0: fuentes += 1
    if ingreso_negocio > 0: fuentes += 1
    if ingreso_rentas > 0: fuentes += 1
    if ingreso_inversiones > 0: fuentes += 1
    
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
    
    # ========================
    # SNAPSHOT FINAL COMPLETO
    # ========================
    snapshot: Dict[str, Any] = {
        # Base
        "ingresos": ingresos,
        "gastos": gastos,
        "ahorro": ahorro,
        "tasa_ahorro": tasa_ahorro,
        
        # Tiempo
        "horas_diarias": horas_diarias,
        "horas_mensuales": horas_mensuales,
        "ingreso_por_hora": ingreso_por_hora,
        
        # Patrimonio y Deuda
        "patrimonio": patrimonio_total,
        "deuda": deuda_total,
        "ratio_deuda_patrimonio": ratio_deuda_patrimonio,
        
        # Cualitativos
        "dependencia_ingreso": dependencia_ingreso,
        "margen_error": margen_error,
        "nivel_sistema": nivel_sistema,
        "estado_general": estado_general,
        
        # Ratios killer
        "ratio_libertad": ratio_libertad,
        "meses_supervivencia": meses_supervivencia,
        "porcentaje_deuda_toxica": porcentaje_deuda_toxica,
        "horas_esclavas": horas_esclavas,
        "porcentaje_inmovilizado": porcentaje_inmovilizado,
        
        # 🆕 Desglose de ingresos
        "ingreso_trabajo": ingreso_trabajo,
        "ingreso_negocio": ingreso_negocio,
        "ingreso_rentas": ingreso_rentas,
        "ingreso_inversiones": ingreso_inversiones,
        
        "peso_trabajo": peso_trabajo,
        "peso_negocio": peso_negocio,
        "peso_pasivo": peso_pasivo,
        
        # 🆕 Desglose de patrimonio
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
        
        # 🆕 Análisis estratégico
        "hay_trampa_inmueble": hay_trampa_inmueble,
        "hay_trampa_empresa": hay_trampa_empresa,
        "falta_liquidez": falta_liquidez,
        "nivel_concentracion": nivel_concentracion,
    }
    
    # Validación: nunca faltan claves
    for k in SNAPSHOT_KEYS:
        snapshot.setdefault(k, None)
    
    return snapshot


# ========================
# FORMATEO PARA DISPLAY
# ========================

def format_currency(value: Decimal, decimals: int = 0) -> str:
    """
    Formatea un valor Decimal a string de moneda.
    
    Ejemplos:
    - 1234.56 → "$1.235" (sin decimales)
    - 1234.56 → "$1.234,56" (con 2 decimales)
    """
    if value is None:
        return "$0"
    
    f = float(value)
    
    if decimals == 0:
        return f"${int(round(f)):,}".replace(",", ".")
    else:
        return f"${f:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def snapshot_to_display(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte snapshot a formato display (sin decimales, strings)
    para mostrar en frontend.
    """
    display = {}
    
    # Keys que deben mostrarse como moneda (sin decimales)
    currency_keys = [
        "ingresos", "gastos", "ahorro", "patrimonio", "deuda",
        "ingreso_trabajo", "ingreso_negocio", "ingreso_rentas",
        "ingreso_inversiones", "ingreso_por_hora",
        "pat_inmuebles", "pat_empresa", "pat_vehiculos",
        "pat_inversiones", "pat_cash"
    ]
    
    # Keys que deben mostrarse como porcentaje
    percentage_keys = [
        "tasa_ahorro", "ratio_deuda_patrimonio", "ratio_libertad",
        "porcentaje_deuda_toxica", "porcentaje_inmovilizado",
        "peso_trabajo", "peso_negocio", "peso_pasivo",
        "porcentaje_inmuebles", "porcentaje_empresa",
        "porcentaje_vehiculos", "porcentaje_inversiones", "porcentaje_cash"
    ]
    
    for k, v in snapshot.items():
        if k in currency_keys:
            display[k] = format_currency(D(v))
        elif k in percentage_keys:
            val = float(v) if isinstance(v, (Decimal, int, float)) else 0
            display[k] = f"{val:.1f}%"
        elif k in ["horas_diarias", "horas_mensuales", "horas_esclavas", "meses_supervivencia"]:
            display[k] = f"{float(v):.1f}" if v else "0"
        else:
            display[k] = v  # string o bool
    
    return display


def snapshot_to_json_safe(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte Decimal → float para json.dumps
    """
    out = {}
    for k, v in snapshot.items():
        if isinstance(v, Decimal):
            out[k] = float(v)
        else:
            out[k] = v
    return out