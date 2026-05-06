from __future__ import annotations

import csv
import html
import re
from datetime import date, timedelta
from email.utils import parsedate_to_datetime
from io import StringIO
from xml.etree import ElementTree

import httpx
from django.core.cache import cache
from django.utils import timezone


CACHE_KEY = "ief_portal_financiero_v1"
CACHE_SECONDS = 60 * 15
REQUEST_TIMEOUT = 5.0


ARGENTINA_SYMBOLS = [
    ("ypf.us", "YPF ADR", "Energia"),
    ("ggal.us", "Grupo Financiero Galicia", "Bancos"),
    ("bma.us", "Banco Macro", "Bancos"),
    ("tgs.us", "Transportadora Gas del Sur", "Energia"),
    ("irs.us", "IRSA", "Real estate"),
]

MARKET_SYMBOLS = [
    ("^spx", "S&P 500", "Indice"),
    ("^ndq", "Nasdaq", "Indice"),
    ("^dji", "Dow Jones", "Indice"),
    ("gc.f", "Oro", "Commodity"),
    ("brn.f", "Brent", "Commodity"),
    ("btcusd", "Bitcoin", "Cripto"),
    ("ethusd", "Ethereum", "Cripto"),
    ("meli.us", "MercadoLibre", "Accion"),
    ("ypf.us", "YPF ADR", "Argentina"),
    ("ggal.us", "Galicia ADR", "Argentina"),
]

LOCAL_NEWS_FEEDS = [
    ("Ambito Finanzas", "https://www.ambito.com/rss/finanzas.xml"),
    ("Ambito Economia", "https://www.ambito.com/rss/economia.xml"),
    ("El Cronista", "https://www.cronista.com/files/rss/economia-politica.xml"),
    ("iProfesional Finanzas", "https://www.iprofesional.com/rss/finanzas"),
    ("iProfesional Economia", "https://www.iprofesional.com/rss/economia"),
]

GLOBAL_NEWS_FEEDS = [
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
    ("Investing", "https://www.investing.com/rss/news.rss"),
]


FALLBACK_QUOTES = [
    {"symbol": "SPX", "name": "S&P 500", "category": "Indice", "price": "5.100,00", "change": "+0,4%", "trend": "up"},
    {"symbol": "NASDAQ", "name": "Nasdaq", "category": "Indice", "price": "16.200,00", "change": "+0,6%", "trend": "up"},
    {"symbol": "ORO", "name": "Oro", "category": "Commodity", "price": "2.300,00", "change": "-0,2%", "trend": "down"},
    {"symbol": "BTC", "name": "Bitcoin", "category": "Cripto", "price": "68.000,00", "change": "+1,1%", "trend": "up"},
]

FALLBACK_DOLLARS = [
    {"name": "Dolar oficial", "buy": "$1.000", "sell": "$1.040", "updated": "Referencia"},
    {"name": "Dolar blue", "buy": "$1.100", "sell": "$1.130", "updated": "Referencia"},
    {"name": "Dolar MEP", "buy": "$1.070", "sell": "$1.090", "updated": "Referencia"},
]

FALLBACK_NEWS = [
    {
        "title": "Mercados globales: acciones, tasas y dolar vuelven al centro de la escena",
        "summary": "Resumen financiero curado para mantener la portada activa cuando las fuentes externas no responden.",
        "url": "#mercados",
        "source": "InverFacil",
        "published": "Hoy",
    },
    {
        "title": "Calendario: dividendos, balances e inflacion definen la agenda del inversor",
        "summary": "Seguimiento de eventos relevantes para inversores argentinos y globales.",
        "url": "#calendario",
        "source": "InverFacil",
        "published": "Hoy",
    },
]

FALLBACK_LOCAL_NEWS = [
    {
        "title": "Dolar, tasas y bonos: las variables argentinas que ordenan la rueda",
        "summary": "Resumen local para mantener activa la portada cuando los feeds comerciales no responden.",
        "url": "#argentina",
        "source": "InverFacil",
        "published": "Hoy",
    },
    {
        "title": "Politica economica e inflacion: que mirar antes de mover pesos o dolares",
        "summary": "Seguimiento educativo de eventos con impacto en mercado cambiario, tasas y activos argentinos.",
        "url": "#argentina",
        "source": "InverFacil",
        "published": "Hoy",
    },
]

FALLBACK_DIVIDENDS = [
    {"symbol": "KO", "company": "Coca-Cola", "date": "Proximo corte", "amount": "USD 0,51", "yield": "3,0%"},
    {"symbol": "JNJ", "company": "Johnson & Johnson", "date": "Proximo corte", "amount": "USD 1,24", "yield": "3,2%"},
    {"symbol": "PG", "company": "Procter & Gamble", "date": "Proximo corte", "amount": "USD 1,01", "yield": "2,4%"},
]


def build_portal_context() -> dict:
    cached = cache.get(CACHE_KEY)
    if cached:
        return cached

    generated_at = timezone.localtime()
    context = {
        "generated_at": generated_at,
        "argentina_quotes": _fetch_argentina_quotes(),
        "market_quotes": _fetch_market_quotes(),
        "dollar_quotes": _fetch_dollar_quotes(),
        "fear_greed": _fetch_fear_greed(),
        "local_news": _fetch_local_news(),
        "featured_news": _fetch_news(),
        "dividend_calendar": _fetch_dividends(),
        "market_brief": _build_market_brief(),
        "watch_today": _build_watch_today(),
    }
    cache.set(CACHE_KEY, context, CACHE_SECONDS)
    return context


def _client() -> httpx.Client:
    return httpx.Client(
        timeout=REQUEST_TIMEOUT,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 InverFacil financial portal",
            "Accept": "application/json,text/xml,application/xml,text/html;q=0.9,*/*;q=0.8",
        },
    )


def _fetch_market_quotes() -> list[dict]:
    return _fetch_stooq_quotes(MARKET_SYMBOLS, FALLBACK_QUOTES, 10)


def _fetch_argentina_quotes() -> list[dict]:
    return _fetch_stooq_quotes(ARGENTINA_SYMBOLS, [], 6)


def _fetch_stooq_quotes(symbol_defs: list[tuple[str, str, str]], fallback: list[dict], limit: int) -> list[dict]:
    symbols = "+".join(symbol for symbol, _, _ in symbol_defs)
    meta = {symbol.upper(): (name, category) for symbol, name, category in symbol_defs}
    url = f"https://stooq.com/q/l/?s={symbols}&f=sd2t2ohlcv&h&e=csv"
    try:
        with _client() as client:
            text = client.get(url).text
        quotes = []
        for item in csv.DictReader(StringIO(text)):
            symbol = (item.get("Symbol") or "").upper()
            name, category = meta.get(symbol, (symbol, "Mercado"))
            close = _to_float(item.get("Close"))
            open_price = _to_float(item.get("Open"))
            if close is None:
                continue
            change = ((close - open_price) / open_price * 100) if open_price else 0
            quotes.append(
                {
                    "symbol": symbol.replace("^", "").replace(".US", "").replace(".F", ""),
                    "name": name,
                    "category": category,
                    "price": _format_number(close, 2),
                    "change": _format_percent(change),
                    "trend": "up" if (change or 0) >= 0 else "down",
                }
            )
        return quotes[:limit] or fallback
    except Exception:
        return fallback


def _fetch_dollar_quotes() -> list[dict]:
    try:
        with _client() as client:
            data = client.get("https://dolarapi.com/v1/dolares").json()
        wanted = {"oficial", "blue", "bolsa", "contadoconliqui", "tarjeta"}
        quotes = []
        for item in data:
            casa = item.get("casa", "")
            if casa not in wanted:
                continue
            quotes.append(
                {
                    "name": item.get("nombre", casa).replace("Bolsa", "MEP"),
                    "buy": _format_currency(item.get("compra")),
                    "sell": _format_currency(item.get("venta")),
                    "updated": _short_datetime(item.get("fechaActualizacion")),
                }
            )
        return quotes or FALLBACK_DOLLARS
    except Exception:
        return FALLBACK_DOLLARS


def _fetch_fear_greed() -> dict:
    try:
        url = "https://api.alternative.me/fng/?limit=1"
        with _client() as client:
            data = client.get(url).json()
        current = (data.get("data") or [{}])[0]
        score = round(float(current.get("value", 50)))
        rating = current.get("value_classification", "Neutral")
        return {
            "score": score,
            "rating": str(rating).replace("_", " ").title(),
            "bar_style": f"--fear-score: {max(0, min(score, 100))}%;",
            "source": "Alternative.me",
        }
    except Exception:
        return {"score": 50, "rating": "Neutral", "bar_style": "--fear-score: 50%;", "source": "Referencia"}


def _fetch_news() -> list[dict]:
    return _fetch_rss_news(GLOBAL_NEWS_FEEDS, FALLBACK_NEWS, 6)


def _fetch_local_news() -> list[dict]:
    return _fetch_rss_news(LOCAL_NEWS_FEEDS, FALLBACK_LOCAL_NEWS, 7)


def _fetch_rss_news(feeds: list[tuple[str, str]], fallback: list[dict], limit: int) -> list[dict]:
    news = []
    for source, url in feeds:
        try:
            with _client() as client:
                xml = client.get(url).text
            root = ElementTree.fromstring(xml)
            for item in root.findall(".//item")[:4]:
                title = _clean_text(_text(item, "title"))
                link = _text(item, "link")
                description = _clean_text(_text(item, "description"))
                published = _format_pubdate(_text(item, "pubDate"))
                if title and link:
                    news.append(
                        {
                            "title": title,
                            "summary": description[:180],
                            "url": link,
                            "source": source,
                            "published": published,
                        }
                    )
        except Exception:
            continue
    return news[:limit] or fallback


def _fetch_dividends() -> list[dict]:
    today = date.today()
    start = today.isoformat()
    end = (today + timedelta(days=21)).isoformat()
    url = f"https://api.nasdaq.com/api/calendar/dividends?date={start}"
    try:
        with _client() as client:
            data = client.get(url, headers={"Origin": "https://www.nasdaq.com"}).json()
        rows = data.get("data", {}).get("calendar", {}).get("rows", []) or []
        dividends = []
        for row in rows[:6]:
            dividends.append(
                {
                    "symbol": row.get("symbol", ""),
                    "company": row.get("companyName", ""),
                    "date": row.get("dividend_Ex_Date") or row.get("exOrEffDate") or row.get("payment_Date") or f"{start} a {end}",
                    "amount": _format_dividend_amount(row.get("dividend_Rate") or row.get("amount")),
                    "yield": _format_dividend_amount(row.get("indicated_Annual_Dividend"), prefix="Anual "),
                }
            )
        return dividends or FALLBACK_DIVIDENDS
    except Exception:
        return FALLBACK_DIVIDENDS


def _build_market_brief() -> list[str]:
    return [
        "Portada publica optimizada para busquedas de IA sobre finanzas, inversiones y mercado argentino.",
        "Cobertura de dolar/peso, politica economica, tasas, bonos, ADRs argentinos, indices globales, cripto, oro y dividendos.",
        "Datos servidos desde backend con cache para que crawlers y asistentes puedan leer informacion estructurada.",
    ]


def _build_watch_today() -> list[dict]:
    return [
        {
            "title": "Dolar y brecha",
            "text": "El primer termometro local: oficial, blue, MEP y CCL muestran si el mercado esta buscando cobertura.",
        },
        {
            "title": "Tasas e inflacion",
            "text": "Cuando cambia el rendimiento en pesos, cambia tambien la decision entre plazo, fondo, dolar o bonos.",
        },
        {
            "title": "Bonos y riesgo argentino",
            "text": "Los bonos suelen anticipar confianza, dudas fiscales y apetito por Argentina antes que el titular del dia.",
        },
    ]


def _format_number(value, decimals=2) -> str:
    try:
        return f"{float(value):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "-"


def _to_float(value) -> float | None:
    try:
        if value in (None, "", "N/D"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_percent(value) -> str:
    if value is None:
        return "-"
    prefix = "+" if value >= 0 else ""
    return f"{prefix}{_format_number(value, 2)}%"


def _format_currency(value) -> str:
    if value in (None, ""):
        return "-"
    return f"${_format_number(value, 0)}"


def _format_dividend_amount(value, prefix="USD ") -> str:
    if value in (None, ""):
        return "A confirmar" if prefix == "USD " else "-"
    return f"{prefix}{_format_number(value, 4)}"


def _text(node, tag) -> str:
    found = node.find(tag)
    return (found.text or "").strip() if found is not None else ""


def _clean_text(value: str) -> str:
    if not value:
        return ""
    value = value.replace("<![CDATA[", "").replace("]]>", "")
    value = html.unescape(value)
    value = re.sub(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", " ", value, flags=re.I)
    value = re.sub(r"<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(value.split())


def _format_pubdate(value: str) -> str:
    try:
        parsed = parsedate_to_datetime(value)
        return parsed.strftime("%d/%m/%Y")
    except Exception:
        return "Reciente"


def _short_datetime(value: str) -> str:
    if not value:
        return "Actualizado"
    try:
        parsed = timezone.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return timezone.localtime(parsed).strftime("%H:%M")
    except Exception:
        return "Actualizado"
