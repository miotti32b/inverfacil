from openai import OpenAI
from django.conf import settings
import math

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# --- Motor de proyección financiera ---
def calcular_proyecciones(cliente, diagnostico = None):
    # 1) si no se pasa diagnóstico, buscar el último
    if diagnostico is None:
        diagnostico = cliente.diagnosticos.order_by('-fecha').first()

    # 2) valores base: si no hay diagnóstico, todo 0
    if not diagnostico:
        ingresos = gastos = patrimonio = deudas = 0
    else:
        ingresos = float(
            diagnostico.ingreso_trabajo + diagnostico.ingreso_negocio +
            diagnostico.ingreso_rentas + diagnostico.ingreso_inversiones +
            diagnostico.ingreso_otros
        )
        gastos = float(
            diagnostico.gasto_necesarios + diagnostico.gasto_innecesarios +
            diagnostico.gasto_financieros + diagnostico.gasto_inversiones
        )
        # dependiendo de qué guardes en tu diag, podrías usar patrimonio_total y deuda_total:
        patrimonio = float(diagnostico.patrimonio_total or 0)
        deudas = float(diagnostico.deuda_total or 0)

    patrimonio_inicial = patrimonio - deudas
    ahorro_mensual = max(ingresos - gastos, 0)

    # variables personales del perfil
    educacion = getattr(cliente, "nivel_formacion", 0) / 10
    experiencia = getattr(cliente, "experiencia_emprendimientos", 0) / 10
    capacidad_crecimiento = 0.6 * educacion + 0.4 * experiencia

    tasa_media = 0.03 + capacidad_crecimiento * 0.04
    tasa_positiva = tasa_media + 0.05
    tasa_negativa = max(tasa_media - 0.05, -0.03)

    proyeccion_media = []
    proyeccion_positiva = []
    proyeccion_negativa = []

    patrimonio_actual = patrimonio_inicial

    for año in range(1, 11):
        patrimonio_actual = patrimonio_actual * (1 + tasa_media) + (ahorro_mensual * 12)
        proyeccion_media.append(round(patrimonio_actual, 2))

        patrimonio_positivo = patrimonio_inicial * (1 + tasa_positiva) ** año + (ahorro_mensual * 12 * año)
        patrimonio_negativo = patrimonio_inicial * (1 + tasa_negativa) ** año + (ahorro_mensual * 12 * año * 0.5)

        proyeccion_positiva.append(round(patrimonio_positivo, 2))
        proyeccion_negativa.append(round(patrimonio_negativo, 2))

    return {
        "positiva": proyeccion_positiva,
        "media": proyeccion_media,
        "negativa": proyeccion_negativa,
        "tasa_media": round(tasa_media * 100, 2),
        "tasa_positiva": round(tasa_positiva * 100, 2),
        "tasa_negativa": round(tasa_negativa * 100, 2),
        "ahorro_mensual": ahorro_mensual,
        "patrimonio_inicial": patrimonio_inicial,
    }

## --- Feedback IA con estilo Emiliano Miotti ---
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generar_feedback_ia(cliente, diagnostico, proyecciones):
    """
    Feedback IA premium basado en:
    - ClientePerfil (vida / decisiones)
    - DiagnosticoFinanciero (números)
    - Proyecciones 10 años (positiva/media/negativa)
    """

    # ---------- helpers ----------
    def _n(v, default=0):
        try:
            return float(v) if v is not None else float(default)
        except Exception:
            return float(default)

    def _s(v, default=""):
        return str(v).strip() if v is not None else default

    def _listify(v):
        # si viene como lista, ok; si viene como string "a,b", lo intentamos; si None, []
        if v is None:
            return []
        if isinstance(v, (list, tuple)):
            return [str(x) for x in v if str(x).strip()]
        if isinstance(v, str):
            # intenta separar por coma
            return [x.strip() for x in v.split(",") if x.strip()]
        return [str(v)]

    # ---------- cálculos ----------
    ingresos_totales = (
        _n(diagnostico.ingreso_trabajo) +
        _n(diagnostico.ingreso_negocio) +
        _n(getattr(diagnostico, "ingreso_emprendimiento", 0)) +
        _n(diagnostico.ingreso_rentas) +
        _n(diagnostico.ingreso_inversiones) +
        _n(diagnostico.ingreso_otros)
    )

    gastos_totales = (
        _n(diagnostico.gasto_necesarios) +
        _n(diagnostico.gasto_innecesarios) +
        _n(diagnostico.gasto_financieros) +
        _n(diagnostico.gasto_inversiones)
    )

    ahorro_mensual = ingresos_totales - gastos_totales
    horas = _n(getattr(diagnostico, "horas_trabajadas", 0), 0)

    patrimonio = _n(getattr(diagnostico, "patrimonio_total", 0), 0)
    deuda = _n(getattr(diagnostico, "deuda_total", 0), 0)

    # ---------- decisiones del form (ajustá según tu modelo real) ----------
    estado_financiero = _s(getattr(diagnostico, "estado_financiero", ""))  # hidden
    reaccion_perdida = _s(getattr(cliente, "reaccion_perdida", getattr(diagnostico, "reaccion_perdida", "")), "")

    # objetivos ordenados (si guardás objetivo_1..3)
    objetivos_ordenados = []
    for i in (1, 2, 3):
        val = getattr(cliente, f"objetivo_{i}", None)
        if val:
            objetivos_ordenados.append(str(val))
    if not objetivos_ordenados:
        # fallback si guardás "objetivos" como multi
        objetivos_ordenados = _listify(getattr(cliente, "objetivos", []))

    valores = _listify(getattr(cliente, "importancia_dinero", []))
    experiencia = _listify(getattr(cliente, "resultados_emprendimientos", []))

    # diagnóstico dinámico (uno de estos 3 sets puede estar completo)
    limitantes = _listify(getattr(cliente, "limitantes_crecimiento", []))
    causas_estancamiento = _listify(getattr(cliente, "causas_estancamiento", []))
    resolucion_deficit = _listify(getattr(cliente, "resolucion_deficit", []))

    # ---------- proyecciones ----------
    pos_10y = _n(proyecciones.get("positiva", [0])[-1], 0)
    med_10y = _n(proyecciones.get("media", [0])[-1], 0)
    neg_10y = _n(proyecciones.get("negativa", [0])[-1], 0)

    # ---------- prompt ----------
    # Nota: le damos números para razonar, pero le prohibimos repetirlos.
    prompt = f"""
Una persona completó el Diagnóstico Financiero de InvertirEsFácil.

Hablás como Emiliano Miotti: mentor financiero argentino, directo, reflexivo y exigente.
No sos motivador vacío. No sos vendedor. No sos académico.
Tu objetivo es generar criterio, claridad y una incomodidad productiva.

IMPORTANTE:
- NO repitas números literalmente.
- NO enumeres datos como un informe.
- NO uses bullets ni listas.
- NO recomiendes activos puntuales ni armes carteras.
- SÍ podés nombrar explícitamente inversión/negocio/formación si aplica.
- Tenés que sonar humano: como audio/video personal.

CONTEXTO (para que no sea atemporal):
Ubicá el análisis en un mundo real con incertidumbre, ciclos, presión de corto plazo,
y la diferencia entre improvisar y tener criterio. Sin números duros ni titulares.

DATOS DISPONIBLES (usarlos para razonar, NO para repetir):
Edad: {getattr(cliente, "edad", None)}
Horas trabajadas/día: {horas}
Ingresos mensuales: {ingresos_totales}
Gastos mensuales: {gastos_totales}
Ahorro mensual estimado: {ahorro_mensual}
Patrimonio: {patrimonio}
Deuda: {deuda}

Estado estructural (ingresos vs gastos): {estado_financiero}

Objetivos (en orden de elección si existe): {objetivos_ordenados}
Valores sobre el dinero (máx 3): {valores}
Reacción ante una caída fuerte del patrimonio: {reaccion_perdida}
Experiencia con dinero/proyectos (máx 2): {experiencia}

Causas/limitantes declaradas (máx 3, según bloque dinámico):
- limitantes_crecimiento: {limitantes}
- causas_estancamiento: {causas_estancamiento}
- resolucion_deficit: {resolucion_deficit}

Proyección a 10 años (para razonar, NO repetir cifras):
- Positivo: {pos_10y}
- Medio: {med_10y}
- Negativo: {neg_10y}

=========================
ESTRUCTURA OBLIGATORIA
=========================

1) Lectura del momento actual
Explicá dónde está parada la persona HOY. Sin cifras.
Hablá de estructura: equilibrio, fragilidad, potencial, dependencia del esfuerzo, margen de error.

2) Lectura psicológica y de comportamiento
Interpretá decisiones y sesgos:
- Qué prioriza realmente (no lo que “declara”)
- Qué patrón se repite
- Qué miedo/inercia aparece
Elegí UNA contradicción central si existe y nombrala explícitamente, con respeto.

3) Lectura estratégica en contexto real
Con criterio profesional:
- diferencia entre esfuerzo vs sistema
- improvisar vs plan mental
- corto plazo vs largo plazo
Podés mencionar inversión/negocio/formación como caminos conceptuales, sin recetas ni activos puntuales.

4) Proyección mental (no numérica)
Explicá qué cambia si sigue igual vs si corrige el eje central.
Hablá de libertad, desgaste, margen de error, y dirección, no de plata final.

5) Cierre con pregunta potente
Una sola pregunta, incómoda, honesta y personal.
No la respondas. Que quede resonando.

Extensión: 500–750 palabras.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Sos Emiliano Miotti, asesor financiero argentino, especialista en mercados, economía real y negocios. "
                    "Tu estilo es claro, directo, reflexivo y exigente. "
                    "No sos motivador vacío ni vendedor: sos un mentor frío pero justo. "
                    "Tu objetivo es generar criterio. "
                    "No das recetas, no prometés resultados, no armás carteras. "
                    "Nunca repetís números literalmente. "
                    "Nunca hablás como una IA."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=950
    )

    return response.choices[0].message.content



from .models import ClientePerfil

def aplicar_referido(request, user):
    ref_code = request.session.get("referral_code")

    if not ref_code:
        return

    try:
        referidor = ClientePerfil.objects.get(referral_code=ref_code)
        perfil = get_or_create_clienteperfil(user)


        # Evitar autoreferido o doble asignación
        if perfil.referido_por is None and referidor != perfil:
            perfil.referido_por = referidor
            perfil.save()

            referidor.total_referred += 1
            referidor.save()

            # Limpiar sesión
            del request.session["referral_code"]

    except ClientePerfil.DoesNotExist:
        pass


from decimal import Decimal

def pagar_comision(perfil_referido, monto_plan):
    if not perfil_referido.referido_por:
        return

    referidor = perfil_referido.referido_por

    # Ejemplo: 10% de comisión
    comision = monto_plan * Decimal("0.10")

    referidor.referral_earnings += comision
    referidor.save()
