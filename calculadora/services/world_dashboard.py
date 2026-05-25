from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date

import httpx
from django.core.cache import cache
from django.utils import timezone

from calculadora.services.portal_financiero import build_portal_context


CACHE_KEY = "ief_world_dashboard_v1"
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

WORLD_INDICATORS = {
    "population": ("SP.POP.TOTL", "Poblacion", "personas"),
    "birth_rate": ("SP.DYN.CBRT.IN", "Natalidad", "cada 1000 hab."),
    "gdp": ("NY.GDP.MKTP.CD", "PBI", "USD"),
    "gdp_pc": ("NY.GDP.PCAP.CD", "PBI per capita", "USD"),
    "inflation": ("FP.CPI.TOTL.ZG", "Inflacion", "% anual"),
    "gini": ("SI.POV.GINI", "Indice Gini", "0 a 100"),
}

FALLBACK_COUNTRY_DATA = {
    "AR": {"population": 46600000, "birth_rate": 13.1, "gdp": 646000000000, "gdp_pc": 13900, "inflation": 211.4, "gini": 42.0},
    "US": {"population": 335000000, "birth_rate": 11.0, "gdp": 27360000000000, "gdp_pc": 81600, "inflation": 4.1, "gini": 39.8},
    "BR": {"population": 216000000, "birth_rate": 12.9, "gdp": 2170000000000, "gdp_pc": 10040, "inflation": 4.6, "gini": 52.0},
    "CN": {"population": 1410000000, "birth_rate": 6.4, "gdp": 17790000000000, "gdp_pc": 12600, "inflation": 0.2, "gini": 37.1},
    "DE": {"population": 84400000, "birth_rate": 8.3, "gdp": 4450000000000, "gdp_pc": 52700, "inflation": 5.9, "gini": 31.7},
    "GB": {"population": 68300000, "birth_rate": 10.0, "gdp": 3340000000000, "gdp_pc": 48900, "inflation": 7.3, "gini": 32.4},
    "JP": {"population": 124500000, "birth_rate": 6.3, "gdp": 4210000000000, "gdp_pc": 33800, "inflation": 3.3, "gini": 32.9},
    "IN": {"population": 1429000000, "birth_rate": 16.1, "gdp": 3550000000000, "gdp_pc": 2480, "inflation": 5.6, "gini": 32.8},
    "RU": {"population": 143800000, "birth_rate": 8.9, "gdp": 2020000000000, "gdp_pc": 14000, "inflation": 5.9, "gini": 36.0},
    "CL": {"population": 19600000, "birth_rate": 9.9, "gdp": 335000000000, "gdp_pc": 17090, "inflation": 7.6, "gini": 44.9},
    "UY": {"population": 3420000, "birth_rate": 9.6, "gdp": 77200000000, "gdp_pc": 22560, "inflation": 5.9, "gini": 40.6},
}

FALLBACK_WORLD = {
    "population": 8119000000,
    "birth_rate": 17.0,
    "gdp": 105000000000000,
    "gdp_pc": 12900,
    "inflation": 5.8,
    "gini": 38.0,
}


def build_world_dashboard_context() -> dict:
    cached = cache.get(CACHE_KEY)
    if cached:
        return cached

    portal = build_portal_context()
    with ThreadPoolExecutor(max_workers=6) as executor:
        country_profiles = list(executor.map(_build_country_profile, COUNTRY_SET))
    world_metrics = _build_world_metrics(country_profiles)
    context = {
        "generated_at": timezone.localtime(),
        "country_profiles": country_profiles,
        "world_metrics": world_metrics,
        "continent_filters": _build_continent_filters(country_profiles),
        "global_assets": portal.get("market_quotes", []),
        "global_news": portal.get("featured_news", [])[:4],
        "space_metrics": _fetch_space_metrics(),
        "conflict_metrics": _build_conflict_metrics(),
        "default_country_code": "AR",
    }
    cache.set(CACHE_KEY, context, CACHE_SECONDS)
    return context


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
    born_year = int(population * birth_rate / 1000) if population and birth_rate else None
    born_day = int(born_year / 365) if born_year else None

    return {
        **country,
        "metrics": {
            "population": _metric("Poblacion", population, _compact_number(population), "personas"),
            "birth_rate": _metric("Tasa de natalidad", birth_rate, _decimal(birth_rate, 1), "nacimientos cada 1000 hab."),
            "births_year": _metric("Nacidos estimados", born_year, _compact_number(born_year), "personas por ano"),
            "births_day": _metric("Nacidos por dia", born_day, _compact_number(born_day), "personas por dia"),
            "gdp": _metric("PBI", metrics.get("gdp"), _money(metrics.get("gdp")), "USD"),
            "gdp_pc": _metric("PBI per capita", metrics.get("gdp_pc"), _money(metrics.get("gdp_pc")), "USD"),
            "inflation": _metric("Inflacion", metrics.get("inflation"), _percent(metrics.get("inflation")), "anual"),
            "gini": _metric("Indice Gini", metrics.get("gini"), _decimal(metrics.get("gini"), 1), "0 igualitario / 100 desigual"),
            "temperature": _metric("Temperatura", weather.get("temperature"), _temperature(weather.get("temperature")), weather.get("label", "capital")),
        },
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


def _build_world_metrics(country_profiles: list[dict]) -> list[dict]:
    world = FALLBACK_WORLD.copy()
    world.update(_fetch_world_bank_world_metrics())
    population = world.get("population") or 0
    birth_rate = world.get("birth_rate") or 0
    births_year = int(population * birth_rate / 1000) if population and birth_rate else None
    births_day = int(births_year / 365) if births_year else None
    countries_loaded = len(country_profiles)

    return [
        _metric("Poblacion mundial", population, _compact_number(population), "personas"),
        _metric("Natalidad global", birth_rate, _decimal(birth_rate, 1), "cada 1000 hab."),
        _metric("Nacimientos hoy", births_day, _compact_number(births_day), "estimacion diaria"),
        _metric("PBI mundial", world.get("gdp"), _money(world.get("gdp")), "USD"),
        _metric("Inflacion global", world.get("inflation"), _percent(world.get("inflation")), "referencia Banco Mundial"),
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

    return [
        _metric("ISS lat/lng", None, _iss_label(iss), "posicion orbital"),
        _metric("Satelites activos", active_satellites, _compact_number(active_satellites), "CelesTrak"),
        _metric("Edad espacial", date.today().year - 1957, str(date.today().year - 1957), "anos desde Sputnik"),
    ]


def _build_conflict_metrics() -> list[dict]:
    return [
        _metric("Guerras activas", 8, "8+", "conflictos mayores monitoreados"),
        _metric("Zonas criticas", 5, "5", "energia, comercio y seguridad"),
        _metric("Riesgo logistico", None, "Elevado", "Mar Rojo, Europa Oriental, Medio Oriente"),
    ]


def _build_continent_filters(country_profiles: list[dict]) -> list[str]:
    continents = sorted({country["continent"] for country in country_profiles})
    return ["Mundo", *continents]


def _metric(label: str, value, display: str, unit: str) -> dict:
    return {"label": label, "value": value, "display": display or "-", "unit": unit}


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
