from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date
import re
import os
from math import sin, pi
from urllib.parse import quote_plus
from xml.etree import ElementTree

import httpx
from django.core.cache import cache
from django.utils import timezone
from openai import OpenAI

from calculadora.services.portal_financiero import build_portal_context, _fetch_stooq_quotes


CACHE_KEY = "ief_world_dashboard_v6"
CACHE_SECONDS = 60 * 60 * 6
REQUEST_TIMEOUT = 4.0

COUNTRY_SET = [
    {"code": "AR", "name": "Argentina", "continent": "America", "capital": "Buenos Aires", "lat": -34.61, "lng": -58.38},
    {"code": "US", "name": "Estados Unidos", "continent": "America", "capital": "Washington", "lat": 38.9, "lng": -77.04},
    {"code": "BR", "name": "Brasil", "continent": "America", "capital": "Brasilia", "lat": -15.79, "lng": -47.88},
    {"code": "CN", "name": "China", "continent": "Asia", "capital": "Beijing", "lat": 39.9, "lng": 116.41},
    {"code": "DE", "name": "Alemania", "continent": "Europa", "capital": "Berlin", "lat": 52.52, "lng": 13.4},
    {"code": "GB", "name": "Reino Unido", "continent": "Europa", "capital": "London", "lat": 51.51, "lng": -0.13},
    {"code": "JP", "name": "Japon", "continent": "Asia", "capital": "Tokyo", "lat": 35.68, "lng": 139.76},
    {"code": "IN", "name": "India", "continent": "Asia", "capital": "New Delhi", "lat": 28.61, "lng": 77.21},
    {"code": "RU", "name": "Rusia", "continent": "Europa/Asia", "capital": "Moscow", "lat": 55.75, "lng": 37.62},
    {"code": "CL", "name": "Chile", "continent": "America", "capital": "Santiago", "lat": -33.45, "lng": -70.66},
    {"code": "UY", "name": "Uruguay", "continent": "America", "capital": "Montevideo", "lat": -34.9, "lng": -56.16},
]

BLOCK_SCOPE_OPTIONS = [
    {"code": "Mundo", "name": "Mundo"},
    {"code": "America", "name": "America"},
    {"code": "Europa", "name": "Europa"},
    {"code": "Asia", "name": "Asia"},
    {"code": "G20", "name": "G20"},
    {"code": "BRICS", "name": "BRICS"},
    {"code": "Mercosur", "name": "Mercosur"},
]

BLOCK_DEFINITIONS = {
    "Mundo": ["AR", "US", "BR", "CN", "DE", "GB", "JP", "IN", "RU", "CL", "UY"],
    "America": ["AR", "US", "BR", "CL", "UY"],
    "Europa": ["DE", "GB", "RU"],
    "Asia": ["CN", "JP", "IN", "RU"],
    "G20": ["AR", "US", "BR", "CN", "DE", "GB", "JP", "IN", "RU"],
    "BRICS": ["BR", "RU", "IN", "CN"],
    "Mercosur": ["AR", "BR", "UY"],
}

WORLD_INDICATORS = {
    "population": ("SP.POP.TOTL", "Poblacion", "personas"),
    "birth_rate": ("SP.DYN.CBRT.IN", "Natalidad", "cada 1000 hab."),
    "death_rate": ("SP.DYN.CDRT.IN", "Mortalidad", "cada 1000 hab."),
    "gdp": ("NY.GDP.MKTP.CD", "PBI", "USD"),
    "gdp_pc": ("NY.GDP.PCAP.CD", "PBI per capita", "USD"),
    "exports": ("NE.EXP.GNFS.CD", "Exportaciones", "USD"),
    "debt_gdp": ("GC.DOD.TOTL.GD.ZS", "Deuda publica", "% PBI"),
    "inflation": ("FP.CPI.TOTL.ZG", "Inflacion", "% anual"),
    "gini": ("SI.POV.GINI", "Indice Gini", "0 a 100"),
}

FALLBACK_COUNTRY_DATA = {
    "AR": {"population": 46600000, "birth_rate": 13.1, "gdp": 646000000000, "gdp_pc": 13900, "exports": 79000000000, "debt_gdp": 85.0, "inflation": 211.4, "gini": 42.0},
    "US": {"population": 335000000, "birth_rate": 11.0, "gdp": 27360000000000, "gdp_pc": 81600, "exports": 3050000000000, "debt_gdp": 122.0, "inflation": 4.1, "gini": 39.8},
    "BR": {"population": 216000000, "birth_rate": 12.9, "gdp": 2170000000000, "gdp_pc": 10040, "exports": 410000000000, "debt_gdp": 84.0, "inflation": 4.6, "gini": 52.0},
    "CN": {"population": 1410000000, "birth_rate": 6.4, "gdp": 17790000000000, "gdp_pc": 12600, "exports": 3710000000000, "debt_gdp": 77.0, "inflation": 0.2, "gini": 37.1},
    "DE": {"population": 84400000, "birth_rate": 8.3, "gdp": 4450000000000, "gdp_pc": 52700, "exports": 2100000000000, "debt_gdp": 64.0, "inflation": 5.9, "gini": 31.7},
    "GB": {"population": 68300000, "birth_rate": 10.0, "gdp": 3340000000000, "gdp_pc": 48900, "exports": 1000000000000, "debt_gdp": 101.0, "inflation": 7.3, "gini": 32.4},
    "JP": {"population": 124500000, "birth_rate": 6.3, "gdp": 4210000000000, "gdp_pc": 33800, "exports": 920000000000, "debt_gdp": 255.0, "inflation": 3.3, "gini": 32.9},
    "IN": {"population": 1429000000, "birth_rate": 16.1, "gdp": 3550000000000, "gdp_pc": 2480, "exports": 770000000000, "debt_gdp": 82.0, "inflation": 5.6, "gini": 32.8},
    "RU": {"population": 143800000, "birth_rate": 8.9, "gdp": 2020000000000, "gdp_pc": 14000, "exports": 590000000000, "debt_gdp": 21.0, "inflation": 5.9, "gini": 36.0},
    "CL": {"population": 19600000, "birth_rate": 9.9, "gdp": 335000000000, "gdp_pc": 17090, "exports": 103000000000, "debt_gdp": 40.0, "inflation": 7.6, "gini": 44.9},
    "UY": {"population": 3420000, "birth_rate": 9.6, "gdp": 77200000000, "gdp_pc": 22560, "exports": 22000000000, "debt_gdp": 61.0, "inflation": 5.9, "gini": 40.6},
}

FALLBACK_SOCIAL_MEDIA = {
    "AR": {"users": 41000000, "daily_minutes": 195, "penetration": 88},
    "US": {"users": 302000000, "daily_minutes": 135, "penetration": 90},
    "BR": {"users": 181000000, "daily_minutes": 225, "penetration": 84},
    "CN": {"users": 1060000000, "daily_minutes": 115, "penetration": 75},
    "DE": {"users": 67000000, "daily_minutes": 95, "penetration": 79},
    "GB": {"users": 57000000, "daily_minutes": 110, "penetration": 83},
    "JP": {"users": 104000000, "daily_minutes": 55, "penetration": 83},
    "IN": {"users": 755000000, "daily_minutes": 150, "penetration": 53},
    "RU": {"users": 106000000, "daily_minutes": 150, "penetration": 74},
    "CL": {"users": 17000000, "daily_minutes": 190, "penetration": 87},
    "UY": {"users": 3000000, "daily_minutes": 175, "penetration": 86},
}

FALLBACK_WORLD = {
    "population": 8119000000,
    "birth_rate": 17.0,
    "death_rate": 7.6,
    "gdp": 105000000000000,
    "gdp_pc": 12900,
    "exports": 31500000000000,
    "debt_gdp": 95.0,
    "inflation": 5.8,
    "gini": 38.0,
}

WORLD_EXTRA_ASSET_SYMBOLS = [
    ("cl.f", "Petroleo WTI", "Commodity"),
    ("ng.f", "Gas natural", "Energia"),
    ("si.f", "Plata", "Commodity"),
    ("hg.f", "Cobre", "Commodity"),
    ("dx.f", "Dolar Index", "Moneda"),
    ("^vix", "VIX", "Volatilidad"),
    ("zs.f", "Soja", "Agro"),
    ("zw.f", "Trigo", "Agro"),
    ("zc.f", "Maiz", "Agro"),
    ("tsm.us", "TSMC", "Semiconductores"),
    ("nvda.us", "Nvidia", "IA / chips"),
    ("asml.us", "ASML", "Semiconductores"),
    ("lith.us", "Lithium ETF", "Litio"),
    ("ura.us", "Uranium ETF", "Uranio"),
]

FALLBACK_EXTRA_ASSETS = [
    {"symbol": "WTI", "name": "Petroleo WTI", "category": "Commodity", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "GAS", "name": "Gas natural", "category": "Energia", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "PLATA", "name": "Plata", "category": "Commodity", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "COBRE", "name": "Cobre", "category": "Commodity", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "DXY", "name": "Dolar Index", "category": "Moneda", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "VIX", "name": "Volatilidad", "category": "Riesgo", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "SOJA", "name": "Soja", "category": "Agro", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "TRIGO", "name": "Trigo", "category": "Agro", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "MAIZ", "name": "Maiz", "category": "Agro", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "TSM", "name": "TSMC", "category": "Semiconductores", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "NVDA", "name": "Nvidia", "category": "IA / chips", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "ASML", "name": "ASML", "category": "Semiconductores", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "LITH", "name": "Lithium ETF", "category": "Litio", "price": "Referencia", "change": "-", "trend": "flat"},
    {"symbol": "URA", "name": "Uranium ETF", "category": "Uranio", "price": "Referencia", "change": "-", "trend": "flat"},
]

CONFLICT_ZONES = [
    {"name": "Europa Oriental", "summary": "Rusia / Ucrania", "lat": 49.0, "lng": 32.0, "radius_km": 760, "severity": "high", "query": "Rusia Ucrania economia politica tecnologia"},
    {"name": "Medio Oriente", "summary": "Israel / Gaza / Iran", "lat": 31.5, "lng": 35.1, "radius_km": 520, "severity": "high", "query": "Israel Gaza Iran economia politica energia"},
    {"name": "Mar Rojo", "summary": "Ruta comercial y energia", "lat": 16.5, "lng": 41.4, "radius_km": 620, "severity": "medium", "query": "Mar Rojo comercio petroleo transporte"},
    {"name": "Sahel", "summary": "Inestabilidad regional", "lat": 15.5, "lng": 2.0, "radius_km": 900, "severity": "medium", "query": "Sahel Africa seguridad economia politica"},
    {"name": "Mar de China Meridional", "summary": "Tension comercial y naval", "lat": 13.5, "lng": 114.0, "radius_km": 820, "severity": "medium", "query": "Mar de China Meridional comercio tecnologia defensa"},
]

COUNTRY_NEWS_META = {
    "AR": {"gl": "AR", "query": "Argentina"},
    "US": {"gl": "US", "query": "Estados Unidos"},
    "BR": {"gl": "BR", "query": "Brasil"},
    "CN": {"gl": "CN", "query": "China"},
    "DE": {"gl": "DE", "query": "Alemania"},
    "GB": {"gl": "GB", "query": "Reino Unido"},
    "JP": {"gl": "JP", "query": "Japon"},
    "IN": {"gl": "IN", "query": "India"},
    "RU": {"gl": "RU", "query": "Rusia"},
    "CL": {"gl": "CL", "query": "Chile"},
    "UY": {"gl": "UY", "query": "Uruguay"},
}

HIGH_IMPACT_TERMS = [
    "crisis", "guerra", "ataque", "emergencia", "alerta", "conflicto", "sancion",
    "sanciones", "eleccion", "elecciones", "mercado", "bolsa", "banco central",
    "inflacion", "deuda", "default", "energia", "petroleo", "gas", "ciberataque",
    "tecnologia", "defensa", "comercio", "arancel", "aranceles", "acuerdo",
    "gobierno", "presidente", "ministro", "tasa", "tasas",
]


def build_world_dashboard_context() -> dict:
    cached = cache.get(CACHE_KEY)
    if cached:
        return cached

    portal = build_portal_context()
    with ThreadPoolExecutor(max_workers=6) as executor:
        country_profiles = list(executor.map(_build_country_profile, COUNTRY_SET))
    conflict_zones = _build_conflict_zones()
    world_metrics = _build_world_metrics(country_profiles, conflict_zones)
    global_assets = _build_global_assets(portal.get("market_quotes", []))
    stress_index = _build_stress_index(world_metrics, conflict_zones, global_assets)
    snapshot = get_or_create_world_snapshot(stress_index, world_metrics, conflict_zones)
    context = {
        "generated_at": timezone.localtime(),
        "country_profiles": country_profiles,
        "world_metrics": world_metrics,
        "stress_index": {
            **stress_index,
            "snapshot_date": snapshot.fecha.isoformat(),
        },
        "signal_cards": _build_signal_cards(stress_index, world_metrics, country_profiles, conflict_zones, global_assets),
        "scope_options": BLOCK_SCOPE_OPTIONS,
        "block_definitions": BLOCK_DEFINITIONS,
        "continent_filters": _build_continent_filters(country_profiles),
        "global_assets": global_assets,
        "global_news": portal.get("featured_news", [])[:4],
        "space_metrics": _fetch_space_metrics(),
        "conflict_metrics": _build_conflict_metrics(),
        "conflict_zones": conflict_zones,
        "default_country_code": "AR",
    }
    cache.set(CACHE_KEY, context, CACHE_SECONDS)
    return context


def get_or_create_world_snapshot(stress_index: dict, world_metrics: list[dict], conflict_zones: list[dict]):
    from calculadora.models import WorldDashboardSnapshot

    today = timezone.localdate()
    metrics = {
        metric["label"]: {
            "display": metric.get("display"),
            "unit": metric.get("unit"),
            "value": metric.get("value"),
        }
        for metric in world_metrics
    }
    metrics["conflict_zones"] = [
        {"name": zone.get("name"), "severity": zone.get("severity")}
        for zone in conflict_zones
    ]
    snapshot, _ = WorldDashboardSnapshot.objects.get_or_create(
        fecha=today,
        defaults={
            "stress_score": stress_index["score"],
            "stress_label": stress_index["label"],
            "category_scores": stress_index["categories"],
            "metrics": metrics,
        },
    )
    return snapshot


def get_or_create_ceo_brief(stress_index: dict, world_metrics: list[dict], conflict_zones: list[dict], assets: list[dict]) -> dict:
    from calculadora.models import WorldCeoBrief

    today = timezone.localdate()
    existing = WorldCeoBrief.objects.filter(fecha=today).first()
    if existing and existing.contenido:
        return {"content": existing.contenido, "model": existing.modelo or "cache", "date": existing.fecha.isoformat()}

    content, model = _generate_ceo_brief(stress_index, world_metrics, conflict_zones, assets)
    brief, _ = WorldCeoBrief.objects.update_or_create(
        fecha=today,
        defaults={"contenido": content, "modelo": model},
    )
    return {"content": brief.contenido, "model": brief.modelo, "date": brief.fecha.isoformat()}


def _generate_ceo_brief(stress_index: dict, world_metrics: list[dict], conflict_zones: list[dict], assets: list[dict]) -> tuple[str, str]:
    fallback = _deterministic_ceo_brief(stress_index, world_metrics, conflict_zones, assets)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return fallback, "deterministico"

    try:
        payload = {
            "stress_index": stress_index,
            "world_metrics": world_metrics[:9],
            "conflict_zones": [
                {"name": zone.get("name"), "severity": zone.get("severity"), "headline": (zone.get("news") or [{}])[0].get("title")}
                for zone in conflict_zones
            ],
            "assets": assets[:8],
        }
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sos InverFacil Intelligence Pro. Redacta un briefing ejecutivo en espanol neutro. "
                        "Formato: 5 bullets cortos. Tono: 'si solo tenes 60 segundos, mira esto'. "
                        "No recomiendes inversiones personalizadas ni prometas resultados."
                    ),
                },
                {"role": "user", "content": str(payload)},
            ],
            max_tokens=260,
            temperature=0.45,
        )
        return response.choices[0].message.content.strip(), "gpt-4o-mini"
    except Exception:
        return fallback, "deterministico"


def _deterministic_ceo_brief(stress_index: dict, world_metrics: list[dict], conflict_zones: list[dict], assets: list[dict]) -> str:
    top_zone = next((zone for zone in conflict_zones if zone.get("severity") == "high"), conflict_zones[0] if conflict_zones else {})
    asset = assets[0] if assets else {"name": "activos globales", "change": "-"}
    return "\n".join([
        f"- Stress global en {stress_index['score']}/100: estado {stress_index['label']}.",
        f"- La presion geopolítica se concentra en {top_zone.get('name', 'zonas criticas')}.",
        f"- El radar de mercado mantiene foco en {asset.get('name')} ({asset.get('change')}).",
        "- Logistica, energia y tecnologia critica son las capas a monitorear antes de tomar decisiones.",
        "- Si solo tenes 60 segundos: mira stress global, energia, DXY, conflictos y noticia critica del pais seleccionado.",
    ])


def _client() -> httpx.Client:
    return httpx.Client(
        timeout=REQUEST_TIMEOUT,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0 InverFacil world dashboard"},
    )


def _build_country_profile(country: dict) -> dict:
    metrics = FALLBACK_COUNTRY_DATA.get(country["code"], {}).copy()
    metrics.update(_fetch_world_bank_country_metrics(country["code"]))
    weather = _fetch_weather(country["lat"], country["lng"])
    population = metrics.get("population") or 0
    birth_rate = metrics.get("birth_rate") or 0
    exports = metrics.get("exports")
    gdp = metrics.get("gdp")
    debt_gdp = metrics.get("debt_gdp")
    country_risk = _country_risk_score(metrics)
    born_year = int(population * birth_rate / 1000) if population and birth_rate else None
    born_day = int(born_year / 365) if born_year else None
    exports_detail = _exports_detail(exports, gdp, population)
    birth_detail = _birth_detail(birth_rate, born_year, born_day)
    gdp_detail = _gdp_detail(gdp, metrics.get("gdp_pc"))
    social = _social_media_metric(country["code"])

    return {
        **country,
        "metrics": {
            "population": _metric("Poblacion", population, _compact_number(population), "personas"),
            "birth_rate": _metric("Tasa de natalidad", birth_rate, _decimal(birth_rate, 1), "nacimientos cada 1000 hab.", birth_detail),
            "births_year": _metric("Nacidos estimados", born_year, _compact_number(born_year), "personas por ano"),
            "births_day": _metric("Nacidos por dia", born_day, _compact_number(born_day), "personas por dia"),
            "gdp": _metric("PBI", gdp, _money(gdp), "USD", gdp_detail),
            "gdp_pc": _metric("PBI per capita", metrics.get("gdp_pc"), _money(metrics.get("gdp_pc")), "USD"),
            "exports": _metric("Exportaciones", exports, _money(exports), "USD anuales", exports_detail),
            "social_media": _metric("Redes sociales", social["daily_minutes"], f"{social['daily_minutes']} min/dia", "uso promedio", social["detail"]),
            "debt_gdp": _metric("Deuda publica", debt_gdp, _percent(debt_gdp), "sobre PBI", "Proxy soberano: deuda bruta del gobierno central o general segun disponibilidad de World Bank. Sirve para comparar presion fiscal, no reemplaza analisis de vencimientos."),
            "country_risk": _metric("Riesgo pais", country_risk, f"{round(country_risk)}/100", "proxy soberano", "Score propio estimado con inflacion, deuda, desigualdad y PBI per capita. Es comparable entre paises del tablero, no equivale al EMBI oficial."),
            "inflation": _metric("Inflacion", metrics.get("inflation"), _percent(metrics.get("inflation")), "anual"),
            "gini": _metric("Indice Gini", metrics.get("gini"), _decimal(metrics.get("gini"), 1), "0 igualitario / 100 desigual"),
            "temperature": _metric("Temperatura", weather.get("temperature"), _temperature(weather.get("temperature")), weather.get("label", "capital")),
        },
        "news": _fetch_country_news(country["code"], country["name"]),
        "source": "World Bank, Open-Meteo y referencias internas",
    }


def _fetch_world_bank_country_metrics(code: str) -> dict:
    metrics = {}
    with _client() as client:
        for key, (indicator, _, _) in WORLD_INDICATORS.items():
            try:
                url = f"https://api.worldbank.org/v2/country/{code}/indicator/{indicator}?format=json&per_page=8"
                data = client.get(url).json()
                rows = data[1] if isinstance(data, list) and len(data) > 1 else []
                value = next((row.get("value") for row in rows if row.get("value") is not None), None)
                if value is not None:
                    metrics[key] = float(value)
            except Exception:
                continue
    return metrics


def _build_world_metrics(country_profiles: list[dict], conflict_zones: list[dict]) -> list[dict]:
    world = FALLBACK_WORLD.copy()
    world.update(_fetch_world_bank_world_metrics())
    population = world.get("population") or 0
    birth_rate = world.get("birth_rate") or 0
    death_rate = world.get("death_rate") or FALLBACK_WORLD["death_rate"]
    births_year = int(population * birth_rate / 1000) if population and birth_rate else None
    births_day = int(births_year / 365) if births_year else None
    deaths_year = int(population * death_rate / 1000) if population and death_rate else None
    deaths_day = int(deaths_year / 365) if deaths_year else None
    countries_loaded = len(country_profiles)
    missile_estimate = _estimate_missile_activity(conflict_zones)

    return [
        _metric("Poblacion mundial", population, _compact_number(population), "personas"),
        _metric("Natalidad global", birth_rate, _decimal(birth_rate, 1), "cada 1000 hab."),
        _metric("Nacimientos hoy", births_day, _compact_number(births_day), "estimacion diaria"),
        _metric("Muertes hoy", deaths_day, _compact_number(deaths_day), "estimacion demografica"),
        _metric("Misiles lanzados", missile_estimate["value"], missile_estimate["display"], missile_estimate["unit"]),
        _metric("PBI mundial", world.get("gdp"), _money(world.get("gdp")), "USD"),
        _metric("PBI per capita global", world.get("gdp_pc"), _money(world.get("gdp_pc")), "USD"),
        _metric("Exportaciones globales", world.get("exports"), _money(world.get("exports")), "USD anuales"),
        _metric("Riesgo comercio ilicito", 61, "61/100", "estimacion compliance"),
        _metric("Inflacion global", world.get("inflation"), _percent(world.get("inflation")), "referencia Banco Mundial"),
        _metric("Gini global", world.get("gini"), _decimal(world.get("gini"), 1), "0 a 100"),
        _metric("Paises monitoreados", countries_loaded, str(countries_loaded), "radar inicial"),
    ]


def _fetch_world_bank_world_metrics() -> dict:
    metrics = {}
    with _client() as client:
        for key, (indicator, _, _) in WORLD_INDICATORS.items():
            try:
                url = f"https://api.worldbank.org/v2/country/WLD/indicator/{indicator}?format=json&per_page=8"
                data = client.get(url).json()
                rows = data[1] if isinstance(data, list) and len(data) > 1 else []
                value = next((row.get("value") for row in rows if row.get("value") is not None), None)
                if value is not None:
                    metrics[key] = float(value)
            except Exception:
                continue
    return metrics


def _fetch_weather(lat: float, lng: float) -> dict:
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lng}&current=temperature_2m,wind_speed_10m"
        )
        with _client() as client:
            current = client.get(url).json().get("current", {})
        return {"temperature": current.get("temperature_2m"), "label": "capital ahora"}
    except Exception:
        return {"temperature": None, "label": "capital"}


def _fetch_space_metrics() -> list[dict]:
    iss = {"lat": None, "lng": None}
    active_satellites = None
    kp_index = None
    solar_wind = None
    asteroid = None
    try:
        with _client() as client:
            iss_data = client.get("https://api.wheretheiss.at/v1/satellites/25544").json()
            iss = {"lat": iss_data.get("latitude"), "lng": iss_data.get("longitude")}
    except Exception:
        pass

    try:
        with _client() as client:
            satellites = client.get("https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json").json()
        active_satellites = len(satellites) if isinstance(satellites, list) else None
    except Exception:
        pass

    try:
        with _client() as client:
            kp_rows = client.get("https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json").json()
        if isinstance(kp_rows, list) and len(kp_rows) > 1:
            kp_index = float(kp_rows[-1][1])
    except Exception:
        pass

    try:
        with _client() as client:
            wind_rows = client.get("https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json").json()
        for row in reversed(wind_rows[1:] if isinstance(wind_rows, list) else []):
            if len(row) > 2 and row[2] not in (None, ""):
                solar_wind = float(row[2])
                break
    except Exception:
        pass

    try:
        today = date.today().isoformat()
        url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key=DEMO_KEY"
        with _client() as client:
            neo_data = client.get(url).json()
        objects = (neo_data.get("near_earth_objects") or {}).get(today, [])
        if objects:
            closest = min(objects, key=lambda item: float(item["close_approach_data"][0]["miss_distance"]["kilometers"]))
            distance = float(closest["close_approach_data"][0]["miss_distance"]["kilometers"])
            asteroid = {"name": closest.get("name", "Asteroide"), "distance": distance}
    except Exception:
        pass

    moon_distance = _estimated_moon_distance_km()
    kp_label = _kp_risk_label(kp_index)

    return [
        _metric("ISS lat/lng", None, _iss_label(iss), "posicion orbital"),
        _metric("Satelites activos", active_satellites, _compact_number(active_satellites), "CelesTrak activos"),
        _metric("Indice Kp", kp_index, _decimal(kp_index, 1) if kp_index is not None else "Sin dato", kp_label),
        _metric("Viento solar", solar_wind, f"{_decimal(solar_wind, 0)} km/s" if solar_wind else "Sin dato", "NOAA SWPC"),
        _metric("Asteroide cercano", None, _asteroid_label(asteroid), "aprox. hoy"),
        _metric("Distancia Luna", moon_distance, f"{_compact_number(moon_distance)} km", "estimacion orbital"),
        _metric("Latencia Marte", None, "4 a 22 min", "senal ida"),
        _metric("Riesgo GPS/radio", kp_index, _space_ops_risk(kp_index), "segun clima espacial"),
    ]


def _build_global_assets(portal_assets: list[dict]) -> list[dict]:
    extra_assets = _fetch_stooq_quotes(WORLD_EXTRA_ASSET_SYMBOLS, FALLBACK_EXTRA_ASSETS, 6)
    assets = []
    seen = set()
    for asset in [*(portal_assets or []), *extra_assets]:
        symbol = asset.get("symbol")
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        assets.append(asset)
    return assets[:22]


def _build_conflict_metrics() -> list[dict]:
    return [
        _metric("Guerras activas", 8, "8+", "conflictos mayores monitoreados"),
        _metric("Zonas criticas", 5, "5", "energia, comercio y seguridad"),
        _metric("Riesgo logistico", None, "Elevado", "Mar Rojo, Europa Oriental, Medio Oriente"),
    ]


def _build_stress_index(world_metrics: list[dict], conflict_zones: list[dict], assets: list[dict]) -> dict:
    metric_map = {metric["label"]: metric for metric in world_metrics}
    inflation = float(metric_map.get("Inflacion global", {}).get("value") or 5.8)
    missiles = float(metric_map.get("Misiles lanzados", {}).get("value") or 0)
    high_conflicts = sum(1 for zone in conflict_zones if zone.get("severity") == "high")
    medium_conflicts = sum(1 for zone in conflict_zones if zone.get("severity") == "medium")
    vix_asset = next((asset for asset in assets if asset.get("symbol") == "VIX"), {})
    dxy_asset = next((asset for asset in assets if asset.get("symbol") in {"DX", "DXY"}), {})
    vix = _asset_price_float(vix_asset)
    dxy = _asset_price_float(dxy_asset)

    macro = _clamp(inflation * 7.5)
    energy = _asset_stress(assets, ["BRENT", "WTI", "NG", "GAS", "CL"])
    geopolitical = _clamp(high_conflicts * 28 + medium_conflicts * 12 + missiles * 0.55)
    logistics = _clamp(35 + medium_conflicts * 8 + high_conflicts * 6)
    technology = _clamp(32 + _headline_term_count(conflict_zones, ["chip", "semiconductor", "tecnologia", "ciber"]) * 8)
    markets = _clamp((vix or 18) * 2 + max((dxy or 103) - 100, 0) * 4)

    categories = {
        "Macro": round(macro),
        "Energia": round(energy),
        "Geopolitica": round(geopolitical),
        "Logistica": round(logistics),
        "Tecnologia critica": round(technology),
        "Mercados": round(markets),
    }
    weights = {
        "Macro": 0.25,
        "Energia": 0.2,
        "Geopolitica": 0.25,
        "Logistica": 0.15,
        "Tecnologia critica": 0.15,
        "Mercados": 0.0,
    }
    score = round(sum(categories[key] * weight for key, weight in weights.items()))
    return {
        "score": score,
        "label": _stress_label(score),
        "categories": categories,
        "bar_style": f"--stress-score: {score}%;",
    }


def _build_signal_cards(stress_index: dict, world_metrics: list[dict], country_profiles: list[dict], conflict_zones: list[dict], assets: list[dict]) -> list[dict]:
    metric_map = {metric["label"]: metric for metric in world_metrics}
    population = metric_map.get("Poblacion mundial", {})
    energy_score = stress_index.get("categories", {}).get("Energia", 0)
    technology_score = stress_index.get("categories", {}).get("Tecnologia critica", 0)
    geopolitical_score = stress_index.get("categories", {}).get("Geopolitica", 0)
    markets_score = stress_index.get("categories", {}).get("Mercados", 0)
    dangerous_conflicts = sum(1 for zone in conflict_zones if zone.get("severity") == "high")
    active_conflicts = sum(1 for zone in conflict_zones if zone.get("severity") in {"high", "medium"})
    vix_asset = next((asset for asset in assets if asset.get("symbol") == "VIX"), {})
    dxy_asset = next((asset for asset in assets if asset.get("symbol") in {"DX", "DXY"}), {})
    return [
        {
            "label": "Mercados",
            "display": f"{markets_score}/100",
            "unit": f"VIX {vix_asset.get('price') or 'N/D'}",
            "tone": "stress",
            "detail": f"Pulso financiero global. Combina volatilidad, dolar global y tono de activos. DXY: {dxy_asset.get('price') or 'sin dato'}.",
        },
        {
            "label": "Geopolitica",
            "display": f"{geopolitical_score}/100",
            "unit": f"{active_conflicts} zonas activas",
            "tone": "fear",
            "detail": f"Radar de conflicto y tension operativa. Hay {dangerous_conflicts} zonas de alta severidad y {active_conflicts} zonas activas monitoreadas.",
        },
        {
            "label": "Demografia",
            "display": population.get("display") or "-",
            "unit": "habitantes",
            "tone": "dxy",
            "detail": "Escala humana global. Sirve para leer consumo, natalidad, urbanizacion, demanda energetica y tension social.",
        },
        {
            "label": "Energia",
            "display": f"{energy_score}/100",
            "unit": "stress energia",
            "tone": "geo",
            "detail": "Lectura de presion energetica: petroleo, gas, rutas comerciales y zonas de conflicto que pueden afectar oferta o transporte.",
        },
        {
            "label": "Tecnologia",
            "display": f"{technology_score}/100",
            "unit": "chips / IA / ciber",
            "tone": "vix",
            "detail": "Capa de riesgo tecnologico: semiconductores, IA, ciberseguridad, restricciones comerciales y bifurcacion tecnologica.",
        },
        {
            "label": "Clima / Espacio",
            "display": "Online",
            "unit": "NOAA / orbita",
            "tone": "space",
            "detail": "Capa operativa para clima espacial, GPS/radio, satelites, ISS y eventos orbitales. Se mantiene compacta para no saturar el tablero.",
        },
    ]


def _asset_price_float(asset: dict) -> float | None:
    raw = str(asset.get("price") or "").replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _asset_stress(assets: list[dict], symbols: list[str]) -> float:
    selected = [asset for asset in assets if asset.get("symbol") in symbols]
    stress = 38
    for asset in selected:
        change = str(asset.get("change") or "")
        if change.startswith("+"):
            stress += 5
        elif change.startswith("-"):
            stress -= 2
    return _clamp(stress)


def _headline_term_count(conflict_zones: list[dict], terms: list[str]) -> int:
    count = 0
    for zone in conflict_zones:
        for item in zone.get("news", []):
            title = (item.get("title") or "").lower()
            if any(term in title for term in terms):
                count += 1
    return count


def _clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def _stress_label(score: int) -> str:
    if score >= 80:
        return "Shock"
    if score >= 65:
        return "Estres"
    if score >= 50:
        return "Tension"
    if score >= 35:
        return "Vigilancia"
    return "Calma"


def _build_conflict_zones() -> list[dict]:
    zones = []
    for zone in CONFLICT_ZONES:
        item = zone.copy()
        item["news"] = _fetch_news_items(zone["query"], "AR")
        zones.append(item)
    return zones


def _estimate_missile_activity(conflict_zones: list[dict]) -> dict:
    terms = ("misil", "misiles", "cohete", "cohetes", "drone", "drones", "bombardeo", "ataque aereo", "aereo")
    hits = 0
    high_severity_hits = 0
    for zone in conflict_zones:
        for news in zone.get("news", []):
            title = (news.get("title") or "").lower()
            if any(term in title for term in terms):
                hits += 1
                if zone.get("severity") == "high":
                    high_severity_hits += 1
    estimate = hits * 12 + high_severity_hits * 8
    if estimate <= 0:
        estimate = sum(10 if zone.get("severity") == "high" else 4 for zone in conflict_zones)
        return {"value": estimate, "display": f"~{estimate}+", "unit": "estimacion por zonas activas"}
    return {"value": estimate, "display": f"~{estimate}+", "unit": "estimacion por reportes"}


def _fetch_country_news(code: str, name: str) -> list[dict]:
    meta = COUNTRY_NEWS_META.get(code, {"gl": code, "query": name})
    return _fetch_news_items(meta["query"], meta["gl"])


def _fetch_news_items(query: str, gl: str, limit: int = 3) -> list[dict]:
    encoded_query = quote_plus(
        f"{query} crisis OR mercado OR guerra OR emergencia OR elecciones OR "
        f"banco central OR energia OR tecnologia when:2d"
    )
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=es-419&gl={gl}&ceid={gl}:es-419"
    try:
        with _client() as client:
            xml = client.get(url).text
        root = ElementTree.fromstring(xml)
        items = []
        for item in root.findall(".//item")[:12]:
            title = _clean_news_title(_xml_text(item, "title"))
            link = _xml_text(item, "link")
            source = _xml_text(item, "source") or "Google News"
            published = _short_pubdate(_xml_text(item, "pubDate"))
            image = _extract_news_image(item)
            if title:
                items.append({
                    "title": title,
                    "url": link,
                    "source": source,
                    "published": published,
                    "image": image,
                    "impact_score": _impact_score(title),
                })
        ranked = sorted(items, key=lambda news: news["impact_score"], reverse=True)
        return ranked[:limit] or _fallback_news(query)
    except Exception:
        return _fallback_news(query)


def _build_continent_filters(country_profiles: list[dict]) -> list[str]:
    continents = sorted({country["continent"] for country in country_profiles})
    return ["Mundo", *continents]


def _metric(label: str, value, display: str, unit: str, detail: str = "") -> dict:
    return {"label": label, "value": value, "display": display or "-", "unit": unit, "detail": detail}


def _exports_detail(exports, gdp, population) -> str:
    if not exports:
        return "Dato anual de bienes y servicios exportados. Fuente principal: World Bank."
    parts = ["Monto anual estimado de bienes y servicios vendidos al exterior."]
    if gdp:
        parts.append(f"Equivale aproximadamente al {_percent(float(exports) / float(gdp) * 100)} del PBI.")
    if population:
        parts.append(f"Exportaciones per capita: {_money(float(exports) / float(population))}.")
    return " ".join(parts)


def _birth_detail(birth_rate, born_year, born_day) -> str:
    parts = ["Pulso demografico: nacimientos cada 1000 habitantes por ano."]
    if born_year:
        parts.append(f"Nacidos estimados por ano: {_compact_number(born_year)} personas.")
    if born_day:
        parts.append(f"Nacidos estimados por dia: {_compact_number(born_day)} personas.")
    if birth_rate:
        rate = float(birth_rate)
        if rate >= 15:
            parts.append("Lectura: poblacion joven y demanda futura de educacion, vivienda y empleo.")
        elif rate <= 8:
            parts.append("Lectura: envejecimiento relativo y presion futura sobre productividad y sistemas previsionales.")
        else:
            parts.append("Lectura: crecimiento demografico moderado.")
    return " ".join(parts)


def _gdp_detail(gdp, gdp_pc) -> str:
    parts = ["Tamano economico total. Sirve para medir peso macro, mercado interno y relevancia global."]
    if gdp_pc:
        parts.append(f"PBI per capita estimado: {_money(gdp_pc)}.")
    if gdp and gdp_pc:
        parts.append("Comparalo con inflacion, deuda y desigualdad para evitar una lectura superficial.")
    return " ".join(parts)


def _social_media_metric(code: str) -> dict:
    social = FALLBACK_SOCIAL_MEDIA.get(code, {"users": None, "daily_minutes": 140, "penetration": None})
    users = social.get("users")
    minutes = social.get("daily_minutes") or 0
    penetration = social.get("penetration")
    detail = [
        "Estimacion ejecutiva de uso social digital basada en referencias publicas agregadas.",
        f"Usuarios totales estimados: {_compact_number(users)}." if users else "Usuarios totales: sin estimacion estable.",
        f"Uso promedio diario: {minutes} minutos por usuario.",
    ]
    if penetration:
        detail.append(f"Penetracion aproximada: {penetration}% de la poblacion.")
    if minutes >= 180:
        detail.append("Comentario: alta atencion digital; relevante para consumo, politica, marca y opinion publica.")
    elif minutes <= 90:
        detail.append("Comentario: uso mas sobrio; el impacto social digital puede ser menos dominante que en mercados hiperconectados.")
    else:
        detail.append("Comentario: actividad digital media, util como termometro de consumo e influencia.")
    return {"users": users, "daily_minutes": minutes, "penetration": penetration, "detail": " ".join(detail)}


def _country_risk_score(metrics: dict) -> int:
    inflation = float(metrics.get("inflation") or 5.0)
    debt = float(metrics.get("debt_gdp") or 70.0)
    gini = float(metrics.get("gini") or 38.0)
    gdp_pc = float(metrics.get("gdp_pc") or 12000)
    inflation_component = _clamp(inflation * 0.33, 0, 35)
    debt_component = _clamp((debt - 35) * 0.28, 0, 28)
    gini_component = _clamp((gini - 30) * 0.7, 0, 18)
    income_component = _clamp((18000 - gdp_pc) / 900, 0, 19)
    return round(inflation_component + debt_component + gini_component + income_component)


def _xml_text(item, tag: str) -> str:
    found = item.find(tag)
    if found is not None and found.text:
        return found.text.strip()
    return ""


def _clean_news_title(title: str) -> str:
    return " ".join((title or "").replace("\n", " ").split())


def _extract_news_image(item) -> str:
    for child in item.iter():
        tag = child.tag.lower()
        if tag.endswith("content") or tag.endswith("thumbnail"):
            url = child.attrib.get("url")
            if url:
                return url
    description = _xml_text(item, "description")
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', description or "", re.IGNORECASE)
    return match.group(1) if match else ""


def _estimated_moon_distance_km() -> int:
    day_of_year = date.today().timetuple().tm_yday
    return int(384_400 + 21_000 * sin(2 * pi * day_of_year / 27.3))


def _asteroid_label(asteroid: dict | None) -> str:
    if not asteroid:
        return "Sin alerta"
    name = re.sub(r"[()]", "", asteroid.get("name", "Asteroide")).strip()
    return f"{name[:18]} / {_compact_number(asteroid.get('distance'))} km"


def _kp_risk_label(kp_index) -> str:
    if kp_index is None:
        return "sin lectura NOAA"
    if kp_index >= 7:
        return "tormenta fuerte"
    if kp_index >= 5:
        return "tormenta geomagnetica"
    if kp_index >= 4:
        return "vigilancia"
    return "normal"


def _space_ops_risk(kp_index) -> str:
    if kp_index is None:
        return "Sin dato"
    if kp_index >= 7:
        return "Alto"
    if kp_index >= 5:
        return "Medio"
    if kp_index >= 4:
        return "Vigilancia"
    return "Normal"


def _impact_score(title: str) -> int:
    normalized = (title or "").lower()
    score = 0
    for term in HIGH_IMPACT_TERMS:
        if term in normalized:
            score += 4 if term in {"crisis", "guerra", "ataque", "emergencia", "sanciones", "default"} else 2
    if any(char.isdigit() for char in normalized):
        score += 1
    return score


def _short_pubdate(value: str) -> str:
    if not value:
        return "Hoy"
    parts = value.split()
    if len(parts) >= 5:
        return " ".join(parts[:5])
    return value


def _fallback_news(query: str) -> list[dict]:
    return [
        {
            "title": f"Radar activo: {query}",
            "url": "",
            "source": "InverFacil",
            "published": "Hoy",
            "image": "",
            "impact_score": 0,
        }
    ]


def _compact_number(value) -> str:
    if value in (None, ""):
        return "-"
    value = float(value)
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.1f}T"
    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}".replace(",", ".")


def _money(value) -> str:
    if value in (None, ""):
        return "-"
    return f"USD {_compact_number(value)}"


def _percent(value) -> str:
    if value in (None, ""):
        return "-"
    return f"{float(value):.1f}%"


def _decimal(value, decimals: int) -> str:
    if value in (None, ""):
        return "-"
    return f"{float(value):.{decimals}f}"


def _temperature(value) -> str:
    if value in (None, ""):
        return "-"
    return f"{float(value):.1f} C"


def _iss_label(iss: dict) -> str:
    if iss.get("lat") is None or iss.get("lng") is None:
        return "En orbita"
    return f"{float(iss['lat']):.1f}, {float(iss['lng']):.1f}"
