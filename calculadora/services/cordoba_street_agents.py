from decimal import Decimal

from django.utils import timezone

from calculadora.models import (
    CapitalOffering,
    CapitalReservation,
    Company,
    CompanyValuationReview,
    OfferingEvidence,
    OfferingQuestion,
    Transaction,
)


def _money(value):
    return f"${value:,.0f}".replace(",", ".")


def _risk_level(score):
    if score >= 75:
        return "Alta"
    if score >= 40:
        return "Media"
    return "Baja"


def _agent(name, mission, status, suggestions):
    return {
        "name": name,
        "mission": mission,
        "status": status,
        "suggestions": suggestions[:5],
    }


def build_ceo_agent_report():
    companies = Company.objects.select_related("created_by").all()
    offerings = CapitalOffering.objects.select_related("company").prefetch_related(
        "reservations",
        "evidences",
        "questions",
    )
    open_offerings = [item for item in offerings if item.status == CapitalOffering.OPEN]
    active_requests = CapitalReservation.objects.filter(status=CapitalReservation.ACTIVE).select_related("offering__company", "user")
    pending_questions = OfferingQuestion.objects.filter(answer="").select_related("offering__company", "user")
    pending_evidence = OfferingEvidence.objects.exclude(status=OfferingEvidence.VERIFIED).select_related("offering__company")
    valuation_reviews = CompanyValuationReview.objects.exclude(status=CompanyValuationReview.CLOSED).select_related("company", "requested_by")
    trades = Transaction.objects.select_related("company", "user")
    total_requested = sum((item.amount for item in active_requests), Decimal("0"))
    total_market_cap = sum((company.market_cap for company in companies), Decimal("0"))
    simulated_volume = sum((trade.total_amount for trade in trades), Decimal("0"))
    total_capital_target = sum((item.capital_target for item in open_offerings), Decimal("0"))

    valuation_alerts = []
    for company in companies:
        if company.revenue and company.market_cap / company.revenue > Decimal("25"):
            valuation_alerts.append(
                f"{company.ticker}: valuacion muy alta frente a ingresos. Pedir narrativa de crecimiento y supuestos."
            )
        if not company.revenue:
            valuation_alerts.append(f"{company.ticker}: sin ingresos declarados. Marcar como tesis temprana.")

    opening_suggestions = []
    for offering in open_offerings:
        if offering.documentation_status == CapitalOffering.DOC_SELF_DECLARED:
            opening_suggestions.append(f"{offering.company.ticker}: sigue autodeclarada. Sugerir al menos una evidencia simple.")
        if offering.instrument_stage == CapitalOffering.INSTRUMENT_PRIVATE_CONTACT:
            opening_suggestions.append(f"{offering.company.ticker}: instrumento en contacto privado. Bien para beta, explicar que no hay ejecucion automatica.")
        if offering.offered_percent > Decimal("30"):
            opening_suggestions.append(f"{offering.company.ticker}: porcentaje ofrecido alto. Pedir explicacion de dilucion y control.")

    market_suggestions = []
    hot_requests = sorted(open_offerings, key=lambda item: item.reserved_total, reverse=True)[:3]
    for offering in hot_requests:
        if offering.reserved_total:
            market_suggestions.append(
                f"{offering.company.ticker}: concentra {_money(offering.reserved_total)} en solicitudes. Priorizar seguimiento."
            )
    if not market_suggestions:
        market_suggestions.append("Todavia no hay demanda fuerte. Impulsar una apertura piloto con historia clara.")

    documentation_suggestions = []
    for evidence in pending_evidence[:5]:
        documentation_suggestions.append(
            f"{evidence.offering.company.ticker}: revisar evidencia '{evidence.title}' ({evidence.get_status_display()})."
        )
    if not documentation_suggestions:
        documentation_suggestions.append("No hay evidencias pendientes. Buen momento para pedir nuevos respaldos a aperturas activas.")

    crm_suggestions = []
    for question in pending_questions[:5]:
        crm_suggestions.append(f"{question.offering.company.ticker}: revisar consulta pendiente de {question.user.username}.")
    if not crm_suggestions:
        crm_suggestions.append("No hay contactos pendientes. Impulsar follows, likes y solicitudes de contacto.")

    risk_score = 0
    risk_score += min(len(valuation_alerts) * 15, 45)
    risk_score += min(pending_questions.count() * 8, 24)
    risk_score += min(pending_evidence.count() * 6, 30)
    risk_score += min(valuation_reviews.count() * 10, 30)
    risk_score += 20 if open_offerings and not active_requests.exists() else 0

    agents = [
        _agent(
            "CFO",
            "Defender valuaciones, facturacion, margen, capital buscado y demanda.",
            _risk_level(len(valuation_alerts) * 20),
            valuation_alerts or ["Las valuaciones no muestran alertas grandes. Mantener supuestos simples y visibles."],
        ),
        _agent(
            "Legal",
            "Cuidar disclaimers, evidencias, alcance de la ficha y servicios opcionales.",
            _risk_level(len(opening_suggestions) * 18),
            opening_suggestions or ["Las aperturas activas estan bien encuadradas para una beta de contacto."],
        ),
        _agent(
            "CMO",
            "Leer demanda, seguidores, solicitudes y narrativa comercial.",
            "Activa" if active_requests.exists() else "Inicial",
            market_suggestions,
        ),
        _agent(
            "CTO",
            "Detectar oportunidades de instrumentacion tecnica, smart contract y trazabilidad.",
            "Inicial" if not valuation_reviews.exists() else "Activa",
            [
                f"{review.company.ticker}: evaluar si la revision abre servicio de instrumentacion o datos."
                for review in valuation_reviews[:5]
            ] or ["Todavia no hay revisiones que pidan soporte tecnico o smart contract."],
        ),
        _agent(
            "Riesgo",
            "Mirar evidencias y separar autodeclarado de validado.",
            _risk_level(pending_evidence.count() * 12),
            documentation_suggestions,
        ),
        _agent(
            "Relaciones con inversores",
            "Cuidar contactos, interesados y oportunidades entre partes.",
            _risk_level(pending_questions.count() * 15),
            crm_suggestions,
        ),
        _agent(
            "Producto",
            "Simplificar el flujo de ficha IPO y reducir friccion de publicadores.",
            "Activa",
            [
                "Separar siempre actual vs objetivo futuro en formularios.",
                "Mantener la promesa: ficha, vinculo e interes; servicios opcionales aparte.",
                "Medir abandono entre crear ficha y publicar ficha publica.",
            ],
        ),
        _agent(
            "Operaciones",
            "Seguir simulacion, liquidez educativa y actividad de mercado.",
            "Activa" if trades.exists() else "Inicial",
            [
                f"Operaciones simuladas: {trades.count()} transacciones por {_money(simulated_volume)}.",
                "Cruzar empresas con mayor volumen simulado contra solicitudes reales.",
            ],
        ),
    ]

    next_actions = []
    if pending_questions.exists():
        next_actions.append("Revisar consultas pendientes antes de promocionar nuevas aperturas.")
    if open_offerings and pending_evidence.exists():
        next_actions.append("Pedir una evidencia minima por apertura activa: facturacion, foto, contrato o link.")
    if not open_offerings:
        next_actions.append("Publicar una apertura piloto para que el mercado entienda el juego.")
    if total_requested:
        next_actions.append("Contactar manualmente a los interesados de mayor monto y registrar feedback.")
    if valuation_reviews.exists():
        next_actions.append("Responder solicitudes de revision de valuacion y ofrecer servicio si corresponde.")
    next_actions.append("Mantener el mensaje: mercado demo para aprender, solicitudes reales para conectar partes.")

    return {
        "generated_at": timezone.localtime(timezone.now()),
        "metrics": {
            "companies": companies.count(),
            "open_offerings": len(open_offerings),
            "active_requests": active_requests.count(),
            "total_requested": total_requested,
            "total_capital_target": total_capital_target,
            "total_market_cap": total_market_cap,
            "simulated_trades": trades.count(),
            "simulated_volume": simulated_volume,
            "valuation_reviews": valuation_reviews.count(),
            "pending_questions": pending_questions.count(),
            "pending_evidence": pending_evidence.count(),
            "risk_level": _risk_level(risk_score),
        },
        "agents": agents,
        "next_actions": next_actions[:6],
    }
