"""ERP El Flete de Dibu - logistica, mudanzas y fletes.

Mismo patron que los ERP de Naif y Distribuidora Rodriguez: login propio con
usuario unico, vista monolitica y template autocontenido. La diferencia es que
este vive en su propio modulo para no seguir engordando views.py.
"""

import base64
import logging
import os
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from urllib.parse import quote

import requests
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from .models import (
    BlueDollarRate,
    DibuBudget,
    DibuClient,
    DibuCost,
    DibuCostCategory,
    DibuCostItem,
    DibuExpenseCategory,
    DibuFuelLoad,
    DibuHelper,
    DibuQuote,
    DibuServiceType,
    DibuTrip,
    DibuTripHelper,
    DibuVehicle,
    DibuWalletMovement,
    DibuWalletSettings,
)
from .views import _add_months, _display_money, _money_from_post

logger = logging.getLogger(__name__)

ZERO = Decimal("0")

DIBU_USERNAME = "dibu"
# Para cambiarla en produccion basta con definir DIBU_PASSWORD en el .env,
# sin tocar el codigo: en el proximo request la clave del usuario se resincroniza.
DIBU_PASSWORD = os.getenv("DIBU_PASSWORD", "fletes")

MONTH_NAMES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
]
WEEKDAY_LABELS = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]

DIBU_DEFAULT_VEHICLES = [
    {
        "code": "foton",
        "name": "Kia 2500",
        "kind": DibuVehicle.TRUCK,
        "image": "dibu_kia.png",
        "capacity_kg": 1500,
        "tires_interval_km": 40000,
        "belt_interval_km": 60000,
        "notes": "Kia K2500 2.5L Turbo Diesel - caja 3.11m x 1.63m - mudanzas y cargas grandes",
    },
    {
        "code": "strada",
        "name": "Fiat Strada",
        "kind": DibuVehicle.PICKUP,
        "image": "dibu_strada.png",
        "capacity_kg": 700,
        "tires_interval_km": 40000,
        "belt_interval_km": 100000,
        "notes": "Pickup - fletes chicos y entregas rapidas",
    },
]

DIBU_DEFAULT_SERVICES = [
    {"code": "flete-simple", "name": "Flete simple", "base_price": 0, "price_per_km": 0},
    {"code": "mudanza-chica", "name": "Mudanza chica (monoambiente)", "base_price": 0, "price_per_km": 0},
    {"code": "mudanza-casa", "name": "Mudanza casa / departamento", "base_price": 0, "price_per_km": 0},
    {"code": "traslado-muebles", "name": "Traslado de muebles", "base_price": 0, "price_per_km": 0},
    {"code": "escombros", "name": "Retiro de escombros", "base_price": 0, "price_per_km": 0},
    {"code": "envio-express", "name": "Envio express", "base_price": 0, "price_per_km": 0},
]

DIBU_COST_CATEGORY_ITEMS = {
    "Mantenimiento": ["Service", "Cubiertas", "Correa", "Chapa y pintura", "Repuestos", "Lavado"],
    "Peajes y estacionamiento": ["Peaje", "Estacionamiento", "Multa"],
    "Seguros e impuestos": ["Seguro", "Patente", "VTV", "Municipal", "Monotributo"],
    "Equipamiento": ["Fajas y sogas", "Mantas", "Carro / zorra", "Film y carton", "Herramientas"],
    "Administrativo": ["Telefonia", "Publicidad", "Contador", "Bancarios"],
    "Otros": ["Varios"],
}

DIBU_WALLET_DEFAULT_CATEGORIES = [
    ("Supermercado", "#e6531f"),
    ("Alquiler", "#b73512"),
    ("Servicios", "#f7b526"),
    ("Salud", "#087443"),
    ("Transporte", "#7b6254"),
    ("Ocio", "#d4b73c"),
    ("Educacion", "#2563eb"),
    ("Ahorro / inversion", "#22a06b"),
    ("Otros", "#776b5e"),
]


# ---------------------------------------------------------------- helpers


def _ensure_dibu_user():
    from django.contrib.auth.models import User

    user, created = User.objects.get_or_create(
        username=DIBU_USERNAME,
        defaults={"first_name": "Dibu", "email": "dibu@elfletededibu.local"},
    )
    if created or not user.check_password(DIBU_PASSWORD):
        user.set_password(DIBU_PASSWORD)
        user.save(update_fields=["password"])
    return user


def _dibu_required(request):
    return (
        request.session.get("dibu_pymes_auth")
        and request.user.is_authenticated
        and request.user.username == DIBU_USERNAME
    )


def _dibu_date(value):
    return parse_date(value or "") or timezone.localdate()


def _decimal_from_post(value):
    return _money_from_post(value)


def _ensure_dibu_defaults():
    """Crea vehiculos, servicios y rubros base la primera vez."""
    for spec in DIBU_DEFAULT_VEHICLES:
        DibuVehicle.objects.get_or_create(code=spec["code"], defaults=spec)
    for spec in DIBU_DEFAULT_SERVICES:
        DibuServiceType.objects.get_or_create(code=spec["code"], defaults=spec)
    for category_name, items in DIBU_COST_CATEGORY_ITEMS.items():
        category, _created = DibuCostCategory.objects.get_or_create(
            name=category_name, defaults={"active": True, "show_in_metrics": True}
        )
        for item_name in items:
            DibuCostItem.objects.get_or_create(category=category, name=item_name, defaults={"active": True})


def _period_bounds(request):
    """Rango de analisis para las metricas del ERP."""
    today = timezone.localdate()
    period_range = request.GET.get("rango") or "month"
    if period_range == "day":
        start = end = today
    elif period_range == "7d":
        start, end = today - timedelta(days=6), today
    elif period_range == "30d":
        start, end = today - timedelta(days=29), today
    elif period_range == "year":
        start, end = date(today.year, 1, 1), today
    else:
        period_range = "month"
        start = date(today.year, today.month, 1)
        end = _add_months(start, 1) - timedelta(days=1)
    custom_from = parse_date(request.GET.get("desde") or "")
    custom_to = parse_date(request.GET.get("hasta") or "")
    if custom_from and custom_to and custom_from <= custom_to:
        period_range, start, end = "custom", custom_from, custom_to
    return period_range, start, end


def _percent_of(value, maximum):
    if not maximum:
        return 0
    return int((Decimal(str(value)) / Decimal(str(maximum))) * Decimal("100"))


def _fuel_stats(vehicle, loads):
    """Consumo real y precio de nafta a partir de cargas con tanque lleno.

    Se compara cada carga full contra la anterior full: los litros de la carga
    actual son los que se gastaron para recorrer ese tramo.
    """
    ordered = sorted(
        [load for load in loads if load.vehicle_id == vehicle.id and load.odometer_km],
        key=lambda load: (load.odometer_km, load.date),
    )
    segments = []
    previous_full = None
    for load in ordered:
        if previous_full and load.full_tank and load.liters:
            distance = Decimal(str(load.odometer_km)) - Decimal(str(previous_full.odometer_km))
            if distance > 0:
                segments.append({"km": distance, "liters": Decimal(str(load.liters))})
        if load.full_tank:
            previous_full = load
    total_km = sum((row["km"] for row in segments), ZERO)
    total_liters = sum((row["liters"] for row in segments), ZERO)
    km_per_liter = (total_km / total_liters) if total_liters else ZERO
    vehicle_loads = [load for load in loads if load.vehicle_id == vehicle.id]
    liters_period = sum((Decimal(str(load.liters or 0)) for load in vehicle_loads), ZERO)
    amount_period = sum((Decimal(str(load.amount or 0)) for load in vehicle_loads), ZERO)
    return {
        "km_per_liter": km_per_liter,
        "price_per_liter": (amount_period / liters_period) if liters_period else ZERO,
        "liters": liters_period,
        "amount": amount_period,
        "measured_km": total_km,
    }


def _sync_trip_helpers(trip, request):
    """Guarda los ayudantes del viaje y recalcula cuanto se les paga."""
    trip.helper_rows.all().delete()
    names = request.POST.getlist("helper_name")
    fees = request.POST.getlist("helper_fee")
    total = ZERO
    for index, raw_name in enumerate(names):
        name = (raw_name or "").strip()
        if not name:
            continue
        fee = _decimal_from_post(fees[index] if index < len(fees) else "0")
        if fee <= 0:
            helper = DibuHelper.objects.filter(name__iexact=name).first()
            fee = helper.default_fee if helper else ZERO
        DibuTripHelper.objects.create(trip=trip, helper_name=name, fee=fee)
        DibuHelper.objects.get_or_create(name=name, defaults={"default_fee": fee, "active": True})
        total += fee
    trip.helpers_cost = total
    trip.save(update_fields=["helpers_cost"])
    return total


def _apply_trip_fields(trip, request):
    """Carga el POST del formulario de viaje sobre la instancia."""
    service_code = (request.POST.get("service_code") or "").strip()
    service = DibuServiceType.objects.filter(code=service_code).first()
    client_name = (request.POST.get("client") or "").strip() or "Particular"
    phone = (request.POST.get("client_phone") or "").strip()

    client_obj, _created = DibuClient.objects.get_or_create(name=client_name)
    if phone and client_obj.phone != phone:
        client_obj.phone = phone
        client_obj.save(update_fields=["phone"])

    km = _decimal_from_post(request.POST.get("km"))
    base_price = _decimal_from_post(request.POST.get("base_price"))
    price_per_km = _decimal_from_post(request.POST.get("price_per_km"))
    extra = _decimal_from_post(request.POST.get("extra"))
    if service:
        if base_price <= 0:
            base_price = service.base_price
        if price_per_km <= 0:
            price_per_km = service.price_per_km

    price = _decimal_from_post(request.POST.get("price"))
    if price <= 0:
        price = base_price + price_per_km * km + extra

    trip.date = _dibu_date(request.POST.get("date"))
    trip.client = client_name
    trip.client_phone = phone
    trip.vehicle = DibuVehicle.objects.filter(pk=request.POST.get("vehicle") or 0).first()
    trip.service_code = service.code if service else service_code
    trip.service_name = service.name if service else (request.POST.get("service_name") or "").strip()
    trip.origin = (request.POST.get("origin") or "").strip()
    trip.destination = (request.POST.get("destination") or "").strip()
    trip.km = km
    trip.base_price = base_price
    trip.price_per_km = price_per_km
    trip.extra = extra
    trip.price = price
    trip.paid = request.POST.get("paid") == "on"
    trip.notes = (request.POST.get("notes") or "").strip()
    return trip


# ---------------------------------------------------------------- ruteo / mapa
#
# Usa Geoapify (geocoding + ruteo + mapa estatico en un solo proveedor,
# free tier sin tarjeta: https://myprojects.geoapify.com). La API key vive
# solo en el servidor via GEOAPIFY_API_KEY en el .env; el navegador nunca
# la ve, porque este mismo view arma el mapa y lo devuelve embebido.

GEOAPIFY_BASE = "https://api.geoapify.com/v1"
GEOAPIFY_MAPS_BASE = "https://maps.geoapify.com/v1"


def _geoapify_key():
    return os.getenv("GEOAPIFY_API_KEY", "")


def _geocode_address(address, api_key):
    """Direccion de texto -> (lat, lon) usando el geocoder de Geoapify."""
    response = requests.get(
        f"{GEOAPIFY_BASE}/geocode/search",
        params={"text": address, "filter": "countrycode:ar", "limit": 1, "apiKey": api_key},
        timeout=8,
    )
    response.raise_for_status()
    features = response.json().get("features") or []
    if not features:
        return None
    longitude, latitude = features[0]["geometry"]["coordinates"]
    return latitude, longitude


def _route_between(origin_point, destination_point, api_key):
    """Ruta por calles entre dos puntos: distancia en km, minutos y geometria."""
    waypoints = f"{origin_point[0]},{origin_point[1]}|{destination_point[0]},{destination_point[1]}"
    response = requests.get(
        f"{GEOAPIFY_BASE}/routing",
        params={"waypoints": waypoints, "mode": "drive", "apiKey": api_key},
        timeout=10,
    )
    response.raise_for_status()
    features = response.json().get("features") or []
    if not features:
        return None
    feature = features[0]
    properties = feature["properties"]
    geometry = feature["geometry"]
    coordinate_lines = geometry["coordinates"] if geometry["type"] == "MultiLineString" else [geometry["coordinates"]]
    points = [point for line in coordinate_lines for point in line]
    return {
        "km": Decimal(str(properties["distance"])) / Decimal("1000"),
        "minutes": int(properties["time"] / 60),
        "points": points,  # lista de [lon, lat]
    }


def _encode_polyline(points):
    """Codifica una lista de puntos [lon, lat] al formato Google Polyline
    que usa Geoapify para dibujar la ruta en el mapa estatico."""
    encoded = []
    last_lat = last_lon = 0
    for longitude, latitude in points:
        lat_i, lon_i = round(latitude * 1e5), round(longitude * 1e5)
        for value, last in ((lat_i, last_lat), (lon_i, last_lon)):
            delta = value - last
            delta = ~(delta << 1) if delta < 0 else (delta << 1)
            while delta >= 0x20:
                encoded.append(chr((0x20 | (delta & 0x1F)) + 63))
                delta >>= 5
            encoded.append(chr(delta + 63))
        last_lat, last_lon = lat_i, lon_i
    return "".join(encoded)


def _static_map_image(origin_point, destination_point, points, api_key):
    """PNG del mapa con la ruta trazada, devuelto como bytes."""
    polyline = _encode_polyline(points)
    # Los colores van con # literal (no %23): requests ya codifica el valor
    # completo del parametro al armar la URL, asi que pre-codificarlo a mano
    # termina codificando el % de nuevo y Geoapify recibe "%23087443" literal.
    params = {
        "style": "osm-bright",
        "width": "640",
        "height": "360",
        "geometry": f"polyline5:{polyline};linewidth:4;linecolor:#e1251b",
        "marker": (
            f"lonlat:{origin_point[1]},{origin_point[0]};type:material;color:#087443;icon:home|"
            f"lonlat:{destination_point[1]},{destination_point[0]};type:material;color:#e1251b;icon:flag"
        ),
        "apiKey": api_key,
    }
    response = requests.get(f"{GEOAPIFY_MAPS_BASE}/staticmap", params=params, timeout=10)
    response.raise_for_status()
    return response.content


@require_POST
def dibu_route_lookup(request):
    """Endpoint AJAX del cotizador: calcula distancia real y arma el mapa.

    Devuelve JSON con km, minutos y el mapa como data-URI base64, asi el
    navegador nunca ve la API key (solo pasa origen/destino en texto).
    """
    if not _dibu_required(request):
        return JsonResponse({"error": "No autorizado."}, status=403)

    api_key = _geoapify_key()
    if not api_key:
        return JsonResponse(
            {"error": "Falta configurar GEOAPIFY_API_KEY en el .env para usar el calculo de ruta."},
            status=400,
        )

    origin_text = (request.POST.get("origin") or "").strip()
    destination_text = (request.POST.get("destination") or "").strip()
    if not origin_text or not destination_text:
        return JsonResponse({"error": "Cargá origen y destino primero."}, status=400)

    try:
        origin_point = _geocode_address(origin_text, api_key)
        if not origin_point:
            return JsonResponse({"error": f"No encontré la dirección de origen: {origin_text}"}, status=404)
        destination_point = _geocode_address(destination_text, api_key)
        if not destination_point:
            return JsonResponse({"error": f"No encontré la dirección de destino: {destination_text}"}, status=404)

        route = _route_between(origin_point, destination_point, api_key)
        if not route:
            return JsonResponse({"error": "No pude calcular una ruta entre esos dos puntos."}, status=404)

        map_bytes = _static_map_image(origin_point, destination_point, route["points"], api_key)
        map_data_uri = "data:image/png;base64," + base64.b64encode(map_bytes).decode("ascii")
    except requests.HTTPError as error:
        body = error.response.text[:300] if error.response is not None else ""
        status = error.response.status_code if error.response is not None else "?"
        logger.error("Geoapify devolvio HTTP %s en dibu_route_lookup: %s", status, body)
        return JsonResponse({"error": f"El servicio de mapas devolvió un error ({status}). Probá de nuevo."}, status=502)
    except requests.RequestException as error:
        logger.exception("Fallo de red en dibu_route_lookup: %s", error)
        return JsonResponse({"error": "No pude conectarme al servicio de mapas. Probá de nuevo."}, status=502)

    return JsonResponse({
        "km": float(route["km"].quantize(Decimal("0.1"))),
        "minutes": route["minutes"],
        "map": map_data_uri,
    })


def dibu_address_autocomplete(request):
    """Sugerencias de direccion mientras se escribe (Desde/Hasta).

    Devuelve una lista vacia en cualquier escenario "no bloqueante" (sin
    key configurada, texto corto, o falla de red) para que el JS del
    formulario nunca tenga que mostrar un error por esto - es una ayuda,
    no algo critico para poder seguir cargando el viaje o presupuesto.
    """
    if not _dibu_required(request):
        return JsonResponse({"error": "No autorizado."}, status=403)

    api_key = _geoapify_key()
    text = (request.GET.get("q") or "").strip()
    if not api_key or len(text) < 3:
        return JsonResponse({"results": []})

    try:
        response = requests.get(
            f"{GEOAPIFY_BASE}/geocode/autocomplete",
            params={"text": text, "filter": "countrycode:ar", "limit": 5, "apiKey": api_key},
            timeout=6,
        )
        response.raise_for_status()
        features = response.json().get("features") or []
    except requests.RequestException as error:
        logger.warning("Fallo el autocompletado de Geoapify: %s", error)
        return JsonResponse({"results": []})

    results = [
        formatted
        for feature in features
        if (formatted := feature.get("properties", {}).get("formatted"))
    ]
    return JsonResponse({"results": results})


def _quote_message(quote_obj):
    """Texto listo para pegar en WhatsApp."""
    lines = [
        "*EL FLETE DE DIBU*",
        "",
        f"Hola {quote_obj.client}! Te paso el presupuesto:",
        "",
    ]
    if quote_obj.service_name:
        lines.append(f"Servicio: {quote_obj.service_name}")
    if quote_obj.origin:
        lines.append(f"Desde: {quote_obj.origin}")
    if quote_obj.destination:
        lines.append(f"Hasta: {quote_obj.destination}")
    if quote_obj.km:
        lines.append(f"Distancia: {quote_obj.km} km")
    price_text = f"{int(quote_obj.price):,}".replace(",", ".")
    lines += ["", f"*TOTAL: $ {price_text}*", ""]
    if quote_obj.notes:
        lines += [quote_obj.notes, ""]
    lines.append("Presupuesto valido por 7 dias. Cualquier duda me escribis!")
    return "\n".join(lines)


# ---------------------------------------------------------------- ERP


def flete_dibu(request):
    _ensure_dibu_user()

    if request.GET.get("salir") == "1":
        request.session.pop("dibu_pymes_auth", None)
        logout(request)
        return redirect("flete_dibu")

    if not _dibu_required(request):
        context = {"login_error": ""}
        if request.method == "POST":
            username = (request.POST.get("username") or "").strip().lower()
            password = request.POST.get("password") or ""
            user = _ensure_dibu_user()
            if username == DIBU_USERNAME and user.check_password(password):
                user.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, user)
                request.session["dibu_pymes_auth"] = True
                return redirect("flete_dibu")
            context["login_error"] = "Usuario o contrasena incorrectos."
        return render(request, "calculadora/flete_dibu.html", context)

    _ensure_dibu_defaults()
    period_range, period_start, period_end = _period_bounds(request)

    def back(section="viajes"):
        base = f"{request.path}?rango={period_range}&seccion={section}"
        if period_range == "custom":
            base += f"&desde={period_start.isoformat()}&hasta={period_end.isoformat()}"
        return redirect(base)

    # ------------------------------------------------------------ acciones
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "trip":
            trip = _apply_trip_fields(DibuTrip(created_by=request.user), request)
            trip.save()
            _sync_trip_helpers(trip, request)
            messages.success(request, "Viaje guardado.")
            return back("viajes")

        if action == "trip_update":
            trip = get_object_or_404(DibuTrip, pk=request.POST.get("trip_id"))
            _apply_trip_fields(trip, request).save()
            _sync_trip_helpers(trip, request)
            messages.success(request, "Viaje actualizado.")
            return back("viajes")

        if action == "trip_toggle_paid":
            trip = get_object_or_404(DibuTrip, pk=request.POST.get("trip_id"))
            trip.paid = not trip.paid
            trip.save(update_fields=["paid"])
            return back(request.POST.get("return_section") or "viajes")

        if action == "trip_delete":
            get_object_or_404(DibuTrip, pk=request.POST.get("trip_id")).delete()
            messages.success(request, "Viaje eliminado.")
            return back("viajes")

        if action == "cost":
            DibuCost.objects.create(
                created_by=request.user,
                date=_dibu_date(request.POST.get("date")),
                vehicle=DibuVehicle.objects.filter(pk=request.POST.get("vehicle") or 0).first(),
                category=(request.POST.get("category") or "").strip(),
                item=(request.POST.get("item") or "").strip() or "Sin detalle",
                amount=_decimal_from_post(request.POST.get("amount")),
                supplier=(request.POST.get("supplier") or "").strip(),
                paid=request.POST.get("paid") == "on",
                notes=(request.POST.get("notes") or "").strip(),
            )
            messages.success(request, "Costo guardado.")
            return back("viajes")

        if action == "cost_update":
            cost = get_object_or_404(DibuCost, pk=request.POST.get("cost_id"))
            cost.date = _dibu_date(request.POST.get("date"))
            cost.vehicle = DibuVehicle.objects.filter(pk=request.POST.get("vehicle") or 0).first()
            cost.category = (request.POST.get("category") or "").strip()
            cost.item = (request.POST.get("item") or "").strip() or "Sin detalle"
            cost.amount = _decimal_from_post(request.POST.get("amount"))
            cost.supplier = (request.POST.get("supplier") or "").strip()
            cost.paid = request.POST.get("paid") == "on"
            cost.notes = (request.POST.get("notes") or "").strip()
            cost.save()
            messages.success(request, "Costo actualizado.")
            return back("viajes")

        if action == "cost_delete":
            get_object_or_404(DibuCost, pk=request.POST.get("cost_id")).delete()
            messages.success(request, "Costo eliminado.")
            return back("viajes")

        if action == "fuel":
            vehicle = get_object_or_404(DibuVehicle, pk=request.POST.get("vehicle"))
            odometer = _decimal_from_post(request.POST.get("odometer_km"))
            DibuFuelLoad.objects.create(
                created_by=request.user,
                date=_dibu_date(request.POST.get("date")),
                vehicle=vehicle,
                liters=_decimal_from_post(request.POST.get("liters")),
                amount=_decimal_from_post(request.POST.get("amount")),
                odometer_km=odometer,
                station=(request.POST.get("station") or "").strip(),
                full_tank=request.POST.get("full_tank") == "on",
                notes=(request.POST.get("notes") or "").strip(),
            )
            if odometer > Decimal(str(vehicle.odometer_km or 0)):
                vehicle.odometer_km = odometer
                vehicle.save(update_fields=["odometer_km"])
            messages.success(request, "Carga de combustible guardada.")
            return back("vehiculos")

        if action == "fuel_delete":
            get_object_or_404(DibuFuelLoad, pk=request.POST.get("fuel_id")).delete()
            messages.success(request, "Carga eliminada.")
            return back("vehiculos")

        if action == "vehicle_update":
            vehicle = get_object_or_404(DibuVehicle, pk=request.POST.get("vehicle_id"))
            vehicle.name = (request.POST.get("name") or vehicle.name).strip()
            vehicle.plate = (request.POST.get("plate") or "").strip()
            vehicle.capacity_kg = int(_decimal_from_post(request.POST.get("capacity_kg")))
            vehicle.odometer_km = _decimal_from_post(request.POST.get("odometer_km"))
            vehicle.tires_last_km = _decimal_from_post(request.POST.get("tires_last_km"))
            vehicle.tires_interval_km = int(_decimal_from_post(request.POST.get("tires_interval_km")))
            vehicle.belt_last_km = _decimal_from_post(request.POST.get("belt_last_km"))
            vehicle.belt_interval_km = int(_decimal_from_post(request.POST.get("belt_interval_km")))
            vehicle.notes = (request.POST.get("notes") or "").strip()
            vehicle.save()
            messages.success(request, f"{vehicle.name} actualizado.")
            return back("vehiculos")

        if action == "maintenance_done":
            vehicle = get_object_or_404(DibuVehicle, pk=request.POST.get("vehicle_id"))
            kind = request.POST.get("kind")
            if kind == "tires":
                vehicle.tires_last_km = vehicle.odometer_km
                vehicle.save(update_fields=["tires_last_km"])
                messages.success(request, f"Cubiertas de {vehicle.name} marcadas como nuevas.")
            elif kind == "belt":
                vehicle.belt_last_km = vehicle.odometer_km
                vehicle.save(update_fields=["belt_last_km"])
                messages.success(request, f"Correa de {vehicle.name} marcada como nueva.")
            return back("vehiculos")

        if action == "service_save":
            code = (request.POST.get("service_code") or "").strip()
            name = (request.POST.get("name") or "").strip()
            if name:
                slug = code or name.lower().replace(" ", "-")[:32]
                DibuServiceType.objects.update_or_create(
                    code=slug,
                    defaults={
                        "name": name,
                        "base_price": _decimal_from_post(request.POST.get("base_price")),
                        "price_per_km": _decimal_from_post(request.POST.get("price_per_km")),
                        "active": True,
                    },
                )
                messages.success(request, "Servicio guardado.")
            return back("config")

        if action == "service_delete":
            get_object_or_404(DibuServiceType, pk=request.POST.get("service_id")).delete()
            messages.success(request, "Servicio eliminado.")
            return back("config")

        if action == "client_save":
            name = (request.POST.get("name") or "").strip()
            if name:
                DibuClient.objects.update_or_create(
                    name=name,
                    defaults={
                        "phone": (request.POST.get("phone") or "").strip(),
                        "address": (request.POST.get("address") or "").strip(),
                        "notes": (request.POST.get("notes") or "").strip(),
                        "active": True,
                    },
                )
                messages.success(request, "Cliente guardado.")
            return back("clientes")

        if action == "client_delete":
            get_object_or_404(DibuClient, pk=request.POST.get("client_id")).delete()
            messages.success(request, "Cliente eliminado.")
            return back("clientes")

        if action == "helper_save":
            name = (request.POST.get("name") or "").strip()
            if name:
                DibuHelper.objects.update_or_create(
                    name=name,
                    defaults={
                        "phone": (request.POST.get("phone") or "").strip(),
                        "default_fee": _decimal_from_post(request.POST.get("default_fee")),
                        "active": True,
                    },
                )
                messages.success(request, "Ayudante guardado.")
            return back("config")

        if action == "helper_delete":
            get_object_or_404(DibuHelper, pk=request.POST.get("helper_id")).delete()
            messages.success(request, "Ayudante eliminado.")
            return back("config")

        if action == "cost_category":
            name = (request.POST.get("category_name") or "").strip()
            if name:
                DibuCostCategory.objects.get_or_create(name=name, defaults={"active": True})
                messages.success(request, "Rubro agregado.")
            return back("config")

        if action == "cost_item":
            category = get_object_or_404(DibuCostCategory, pk=request.POST.get("category_id"))
            name = (request.POST.get("item_name") or "").strip()
            if name:
                DibuCostItem.objects.get_or_create(category=category, name=name, defaults={"active": True})
                messages.success(request, "Item agregado.")
            return back("config")

        if action == "cost_item_delete":
            get_object_or_404(DibuCostItem, pk=request.POST.get("item_id")).delete()
            return back("config")

        if action == "category_metric_toggle":
            category = get_object_or_404(DibuCostCategory, pk=request.POST.get("category_id"))
            category.show_in_metrics = not category.show_in_metrics
            category.save(update_fields=["show_in_metrics"])
            return back("metricas")

        if action == "quote_save":
            service = DibuServiceType.objects.filter(code=request.POST.get("service_code") or "").first()
            km = _decimal_from_post(request.POST.get("km"))
            price = _decimal_from_post(request.POST.get("price"))
            if price <= 0 and service:
                price = service.quote_for(km)
            price += _decimal_from_post(request.POST.get("extra"))
            DibuQuote.objects.create(
                created_by=request.user,
                date=timezone.localdate(),
                client=(request.POST.get("client") or "").strip() or "Sin nombre",
                phone=(request.POST.get("phone") or "").strip(),
                service_name=service.name if service else (request.POST.get("service_name") or "").strip(),
                origin=(request.POST.get("origin") or "").strip(),
                destination=(request.POST.get("destination") or "").strip(),
                km=km,
                price=price,
                notes=(request.POST.get("notes") or "").strip(),
            )
            messages.success(request, "Presupuesto guardado. Copialo o mandalo por WhatsApp.")
            return back("cotizador")

        if action == "quote_delete":
            get_object_or_404(DibuQuote, pk=request.POST.get("quote_id")).delete()
            return back("cotizador")

    # ------------------------------------------------------------ datos
    today = timezone.localdate()
    vehicles = list(DibuVehicle.objects.filter(active=True))
    services = list(DibuServiceType.objects.filter(active=True))
    clients = list(DibuClient.objects.filter(active=True))
    helpers = list(DibuHelper.objects.filter(active=True))

    trips_qs = DibuTrip.objects.filter(date__range=(period_start, period_end)).select_related("vehicle")
    costs_qs = DibuCost.objects.filter(date__range=(period_start, period_end)).select_related("vehicle")
    fuel_qs = DibuFuelLoad.objects.filter(date__range=(period_start, period_end)).select_related("vehicle")

    period_income = trips_qs.aggregate(total=Sum("price"))["total"] or ZERO
    period_helpers = trips_qs.aggregate(total=Sum("helpers_cost"))["total"] or ZERO
    period_fuel = fuel_qs.aggregate(total=Sum("amount"))["total"] or ZERO
    period_other_costs = costs_qs.aggregate(total=Sum("amount"))["total"] or ZERO
    period_costs = period_helpers + period_fuel + period_other_costs
    period_profit = period_income - period_costs
    period_margin = (period_profit / period_income * Decimal("100")) if period_income else ZERO
    trips_count = trips_qs.count()
    period_km = trips_qs.aggregate(total=Sum("km"))["total"] or ZERO
    average_ticket = (period_income / trips_count) if trips_count else ZERO

    unpaid_qs = DibuTrip.objects.filter(paid=False).select_related("vehicle")
    unpaid_total = unpaid_qs.aggregate(total=Sum("price"))["total"] or ZERO

    # comparacion contra el periodo anterior de igual duracion
    span = (period_end - period_start).days + 1
    prev_end = period_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=span - 1)
    prev_trips = DibuTrip.objects.filter(date__range=(prev_start, prev_end))
    prev_income = prev_trips.aggregate(total=Sum("price"))["total"] or ZERO
    prev_costs = (
        (prev_trips.aggregate(total=Sum("helpers_cost"))["total"] or ZERO)
        + (DibuFuelLoad.objects.filter(date__range=(prev_start, prev_end)).aggregate(total=Sum("amount"))["total"] or ZERO)
        + (DibuCost.objects.filter(date__range=(prev_start, prev_end)).aggregate(total=Sum("amount"))["total"] or ZERO)
    )
    prev_profit = prev_income - prev_costs

    def delta_percent(current, previous):
        if not previous:
            return None
        return int(((Decimal(str(current)) - Decimal(str(previous))) / Decimal(str(previous))) * Decimal("100"))

    # ------------------------------------------------------------ por vehiculo
    all_fuel_loads = list(DibuFuelLoad.objects.all().select_related("vehicle"))
    period_fuel_loads = list(fuel_qs)
    vehicle_rows = []
    for vehicle in vehicles:
        v_trips = [trip for trip in trips_qs if trip.vehicle_id == vehicle.id]
        v_income = sum((Decimal(str(trip.price or 0)) for trip in v_trips), ZERO)
        v_helpers = sum((Decimal(str(trip.helpers_cost or 0)) for trip in v_trips), ZERO)
        v_km = sum((Decimal(str(trip.km or 0)) for trip in v_trips), ZERO)
        v_fuel = sum(
            (Decimal(str(load.amount or 0)) for load in period_fuel_loads if load.vehicle_id == vehicle.id), ZERO
        )
        v_other = sum(
            (Decimal(str(cost.amount or 0)) for cost in costs_qs if cost.vehicle_id == vehicle.id), ZERO
        )
        v_costs = v_helpers + v_fuel + v_other
        v_profit = v_income - v_costs
        stats = _fuel_stats(vehicle, all_fuel_loads)
        period_stats = _fuel_stats(vehicle, period_fuel_loads)
        vehicle_rows.append({
            "vehicle": vehicle,
            "trips": len(v_trips),
            "income": v_income,
            "costs": v_costs,
            "fuel": v_fuel,
            "helpers": v_helpers,
            "other": v_other,
            "profit": v_profit,
            "km": v_km,
            "cost_per_km": (v_costs / v_km) if v_km else ZERO,
            "income_per_km": (v_income / v_km) if v_km else ZERO,
            "km_per_liter": stats["km_per_liter"],
            "price_per_liter": period_stats["price_per_liter"] or stats["price_per_liter"],
            "liters": period_stats["liters"],
            "margin": (v_profit / v_income * Decimal("100")) if v_income else ZERO,
            "tires": vehicle.tires_alert,
            "belt": vehicle.belt_alert,
        })
    max_vehicle_profit = max([abs(row["profit"]) for row in vehicle_rows] + [Decimal("1")])
    max_vehicle_income = max([row["income"] for row in vehicle_rows] + [Decimal("1")])
    for row in vehicle_rows:
        row["profit_percent"] = _percent_of(abs(row["profit"]), max_vehicle_profit)
        row["income_percent"] = _percent_of(row["income"], max_vehicle_income)

    maintenance_alerts = [
        {"vehicle": row["vehicle"], "kind": "Cubiertas", "info": row["tires"]}
        for row in vehicle_rows
        if row["tires"]["state"] in {"due", "soon"}
    ] + [
        {"vehicle": row["vehicle"], "kind": "Correa", "info": row["belt"]}
        for row in vehicle_rows
        if row["belt"]["state"] in {"due", "soon"}
    ]

    # ------------------------------------------------------------ series diarias
    income_by_day, costs_by_day, trips_by_day = {}, {}, {}
    for trip in trips_qs:
        income_by_day[trip.date] = income_by_day.get(trip.date, ZERO) + Decimal(str(trip.price or 0))
        costs_by_day[trip.date] = costs_by_day.get(trip.date, ZERO) + Decimal(str(trip.helpers_cost or 0))
        trips_by_day[trip.date] = trips_by_day.get(trip.date, 0) + 1
    for cost in costs_qs:
        costs_by_day[cost.date] = costs_by_day.get(cost.date, ZERO) + Decimal(str(cost.amount or 0))
    for load in period_fuel_loads:
        costs_by_day[load.date] = costs_by_day.get(load.date, ZERO) + Decimal(str(load.amount or 0))

    daily_rows = []
    for day in sorted(set(income_by_day) | set(costs_by_day)):
        day_income = income_by_day.get(day, ZERO)
        day_costs = costs_by_day.get(day, ZERO)
        daily_rows.append({
            "label": day.strftime("%d/%m"),
            "income": day_income,
            "costs": day_costs,
            "profit": day_income - day_costs,
            "trips": trips_by_day.get(day, 0),
        })
    daily_rows = daily_rows[-18:]
    max_daily = max([row["income"] for row in daily_rows] + [Decimal("1")])
    for row in daily_rows:
        row["income_percent"] = _percent_of(row["income"], max_daily)
        row["costs_percent"] = _percent_of(row["costs"], max_daily)

    # ------------------------------------------------------------ rankings
    hidden_categories = set(
        DibuCostCategory.objects.filter(show_in_metrics=False).values_list("name", flat=True)
    )
    cost_bars = list(
        costs_qs.exclude(category="")
        .exclude(category__in=hidden_categories)
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    if period_fuel and "Combustible" not in hidden_categories:
        cost_bars.append({"category": "Combustible", "total": period_fuel})
    if period_helpers and "Ayudantes" not in hidden_categories:
        cost_bars.append({"category": "Ayudantes", "total": period_helpers})
    cost_bars.sort(key=lambda row: row["total"], reverse=True)
    max_cost_bar = max([row["total"] for row in cost_bars] + [Decimal("1")])
    for row in cost_bars:
        row["percent"] = _percent_of(row["total"], max_cost_bar)

    top_clients = list(
        trips_qs.values("client").annotate(total=Sum("price"), count=Count("id")).order_by("-total")[:8]
    )
    max_client = max([row["total"] for row in top_clients] + [Decimal("1")])
    for row in top_clients:
        row["percent"] = _percent_of(row["total"], max_client)

    top_services = list(
        trips_qs.exclude(service_name="")
        .values("service_name")
        .annotate(total=Sum("price"), count=Count("id"))
        .order_by("-total")[:8]
    )
    max_service = max([row["total"] for row in top_services] + [Decimal("1")])
    for row in top_services:
        row["percent"] = _percent_of(row["total"], max_service)

    # ------------------------------------------------------------ agenda
    try:
        cal_year = int(request.GET.get("anio") or today.year)
        cal_month = int(request.GET.get("mes") or today.month)
    except (TypeError, ValueError):
        cal_year, cal_month = today.year, today.month
    cal_month = min(max(cal_month, 1), 12)
    first_weekday, days_in_month = monthrange(cal_year, cal_month)
    month_start = date(cal_year, cal_month, 1)
    month_end = date(cal_year, cal_month, days_in_month)
    month_trips = list(
        DibuTrip.objects.filter(date__range=(month_start, month_end)).select_related("vehicle").order_by("date")
    )
    trips_by_date = {}
    for trip in month_trips:
        trips_by_date.setdefault(trip.date, []).append(trip)

    calendar_cells = [{"blank": True} for _ in range(first_weekday)]
    for day_number in range(1, days_in_month + 1):
        day = date(cal_year, cal_month, day_number)
        day_trips = trips_by_date.get(day, [])
        calendar_cells.append({
            "blank": False,
            "day": day_number,
            "date": day,
            "is_today": day == today,
            "trips": day_trips,
            "total": sum((Decimal(str(trip.price or 0)) for trip in day_trips), ZERO),
        })
    while len(calendar_cells) % 7:
        calendar_cells.append({"blank": True})
    calendar_weeks = [calendar_cells[index:index + 7] for index in range(0, len(calendar_cells), 7)]
    prev_month = _add_months(month_start, -1)
    next_month = _add_months(month_start, 1)

    # ------------------------------------------------------------ listados
    trips_page = Paginator(
        DibuTrip.objects.select_related("vehicle").prefetch_related("helper_rows"), 25
    ).get_page(request.GET.get("pv"))
    costs_page = Paginator(DibuCost.objects.select_related("vehicle"), 25).get_page(request.GET.get("pc"))
    fuel_page = Paginator(DibuFuelLoad.objects.select_related("vehicle"), 20).get_page(request.GET.get("pf"))

    quotes = list(DibuQuote.objects.all()[:30])
    quote_rows = []
    for quote_obj in quotes:
        text = _quote_message(quote_obj)
        phone_digits = "".join(char for char in quote_obj.phone if char.isdigit())
        quote_rows.append({
            "quote": quote_obj,
            "text": text,
            "wa_url": (
                f"https://wa.me/{phone_digits}?text={quote(text)}"
                if phone_digits
                else f"https://wa.me/?text={quote(text)}"
            ),
        })

    client_rows = []
    for client in clients:
        client_trips = DibuTrip.objects.filter(client=client.name)
        client_rows.append({
            "client": client,
            "trips": client_trips.count(),
            "total": client_trips.aggregate(total=Sum("price"))["total"] or ZERO,
            "unpaid": client_trips.filter(paid=False).aggregate(total=Sum("price"))["total"] or ZERO,
            "last": client_trips.order_by("-date").values_list("date", flat=True).first(),
        })
    client_rows.sort(key=lambda row: row["total"], reverse=True)

    cost_categories = list(DibuCostCategory.objects.prefetch_related("items"))
    cost_items_map = {
        category.name: [item.name for item in category.items.all() if item.active]
        for category in cost_categories
    }
    service_map = {
        service.code: {"base": str(service.base_price), "per_km": str(service.price_per_km), "name": service.name}
        for service in services
    }
    helper_fees = {helper.name: str(helper.default_fee) for helper in helpers}

    context = {
        "is_dibu_auth": True,
        "today": today,
        "period_range": period_range,
        "period_start": period_start,
        "period_end": period_end,
        "section": request.GET.get("seccion") or "viajes",

        "vehicles": vehicles,
        "services": services,
        "clients": clients,
        "helpers": helpers,
        "client_rows": client_rows,
        "cost_categories": cost_categories,
        "cost_items_map": cost_items_map,
        "service_map": service_map,
        "helper_fees": helper_fees,

        "period_income": period_income,
        "period_costs": period_costs,
        "period_profit": period_profit,
        "period_margin": period_margin,
        "period_fuel": period_fuel,
        "period_helpers": period_helpers,
        "period_other_costs": period_other_costs,
        "period_km": period_km,
        "trips_count": trips_count,
        "average_ticket": average_ticket,
        "unpaid_total": unpaid_total,
        "unpaid_trips": list(unpaid_qs[:12]),
        "income_delta": delta_percent(period_income, prev_income),
        "costs_delta": delta_percent(period_costs, prev_costs),
        "profit_delta": delta_percent(period_profit, prev_profit),

        "vehicle_rows": vehicle_rows,
        "maintenance_alerts": maintenance_alerts,
        "daily_rows": daily_rows,
        "cost_bars": cost_bars,
        "hidden_categories": sorted(hidden_categories),
        "top_clients": top_clients,
        "top_services": top_services,

        "calendar_weeks": calendar_weeks,
        "weekday_labels": WEEKDAY_LABELS,
        "cal_year": cal_year,
        "cal_month": cal_month,
        "cal_month_name": dict(MONTH_NAMES)[cal_month],
        "prev_month": prev_month,
        "next_month": next_month,
        "month_total": sum((Decimal(str(trip.price or 0)) for trip in month_trips), ZERO),
        "month_trips_count": len(month_trips),

        "trips_page": trips_page,
        "costs_page": costs_page,
        "fuel_page": fuel_page,
        "quote_rows": quote_rows,
    }
    return render(request, "calculadora/flete_dibu.html", context)


# ---------------------------------------------------------------- billetera


def _ensure_dibu_wallet_defaults():
    settings_obj, _created = DibuWalletSettings.objects.get_or_create(pk=1)
    for name, color in DIBU_WALLET_DEFAULT_CATEGORIES:
        DibuExpenseCategory.objects.get_or_create(name=name, defaults={"color": color, "active": True})
    return settings_obj


def _wallet_bounds(request):
    today = timezone.localdate()
    try:
        year = int(request.GET.get("anio") or today.year)
    except (TypeError, ValueError):
        year = today.year
    try:
        month = int(request.GET.get("mes") or today.month)
    except (TypeError, ValueError):
        month = today.month
    month = min(max(month, 1), 12)
    period_range = request.GET.get("rango") or "month"
    if period_range == "7d":
        start, end = today - timedelta(days=6), today
    elif period_range == "30d":
        start, end = today - timedelta(days=29), today
    elif period_range == "ytd":
        start, end, year = date(today.year, 1, 1), today, today.year
    else:
        period_range = "month"
        start = date(year, month, 1)
        end = _add_months(start, 1) - timedelta(days=1)
    return year, month, period_range, start, end


def dibu_wallet(request):
    _ensure_dibu_user()
    if not _dibu_required(request):
        return redirect("flete_dibu")

    wallet_settings = _ensure_dibu_wallet_defaults()
    year, month, period_range, start, end = _wallet_bounds(request)

    def back(tab="panel"):
        return redirect(f"{request.path}?tab={tab}&anio={year}&mes={month}&rango={period_range}")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "currency":
            currency = request.POST.get("display_currency")
            if currency in {"ARS", "USD"}:
                wallet_settings.display_currency = currency
                wallet_settings.save(update_fields=["display_currency", "updated_at"])
            return back(request.POST.get("return_tab") or "panel")

        if action == "movement":
            DibuWalletMovement.objects.create(
                created_by=request.user,
                date=_dibu_date(request.POST.get("date")),
                kind=request.POST.get("kind") or DibuWalletMovement.EXPENSE,
                category=DibuExpenseCategory.objects.filter(pk=request.POST.get("category") or 0).first(),
                description=(request.POST.get("description") or "").strip(),
                amount=_decimal_from_post(request.POST.get("amount")),
                payment_method=(request.POST.get("payment_method") or "").strip(),
                notes=(request.POST.get("notes") or "").strip(),
            )
            messages.success(request, "Movimiento guardado.")
            return back("panel")

        if action == "movement_delete":
            get_object_or_404(DibuWalletMovement, pk=request.POST.get("movement_id")).delete()
            messages.success(request, "Movimiento eliminado.")
            return back("movimientos")

        if action == "import_profit":
            profit_start = parse_date(request.POST.get("from") or "") or start
            profit_end = parse_date(request.POST.get("to") or "") or end
            trips = DibuTrip.objects.filter(date__range=(profit_start, profit_end), paid=True)
            income = trips.aggregate(total=Sum("price"))["total"] or ZERO
            costs = (
                (trips.aggregate(total=Sum("helpers_cost"))["total"] or ZERO)
                + (DibuFuelLoad.objects.filter(date__range=(profit_start, profit_end)).aggregate(total=Sum("amount"))["total"] or ZERO)
                + (DibuCost.objects.filter(date__range=(profit_start, profit_end)).aggregate(total=Sum("amount"))["total"] or ZERO)
            )
            profit = income - costs
            if profit > 0:
                DibuWalletMovement.objects.create(
                    created_by=request.user,
                    date=profit_end,
                    kind=DibuWalletMovement.INCOME,
                    description=f"Ganancia fletes {profit_start.strftime('%d/%m')} a {profit_end.strftime('%d/%m')}",
                    amount=profit,
                    source="dibu_profit",
                )
                messages.success(request, "Ganancia del negocio pasada a la billetera.")
            else:
                messages.success(request, "En ese periodo no hubo ganancia positiva para pasar.")
            return back("panel")

        if action == "category":
            name = (request.POST.get("category_name") or "").strip()
            if name:
                DibuExpenseCategory.objects.get_or_create(
                    name=name,
                    defaults={"active": True, "color": (request.POST.get("color") or "").strip() or "#776b5e"},
                )
                messages.success(request, "Categoria agregada.")
            return back("config")

        if action == "category_toggle":
            category = get_object_or_404(DibuExpenseCategory, pk=request.POST.get("category_id"))
            category.active = not category.active
            category.save(update_fields=["active"])
            return back("config")

        if action == "budget":
            category = get_object_or_404(DibuExpenseCategory, pk=request.POST.get("category_id"))
            DibuBudget.objects.update_or_create(
                category=category,
                year=year,
                month=month,
                defaults={"amount": _decimal_from_post(request.POST.get("amount"))},
            )
            messages.success(request, "Presupuesto actualizado.")
            return back("presupuesto")

    currency = wallet_settings.display_currency
    rate_cache = {row.date: row.sell for row in BlueDollarRate.objects.all()}
    symbol = "US$" if currency == "USD" else "$"

    movements = list(
        DibuWalletMovement.objects.filter(date__range=(start, end)).select_related("category")
    )
    income = sum(
        (_display_money(row.amount, row.date, currency, rate_cache)
         for row in movements if row.kind == DibuWalletMovement.INCOME),
        ZERO,
    )
    expense = sum(
        (_display_money(row.amount, row.date, currency, rate_cache)
         for row in movements if row.kind == DibuWalletMovement.EXPENSE),
        ZERO,
    )
    balance = income - expense

    all_movements = DibuWalletMovement.objects.all()
    total_income = all_movements.filter(kind=DibuWalletMovement.INCOME).aggregate(total=Sum("amount"))["total"] or ZERO
    total_expense = all_movements.filter(kind=DibuWalletMovement.EXPENSE).aggregate(total=Sum("amount"))["total"] or ZERO

    categories = list(DibuExpenseCategory.objects.all())
    budgets = {
        row.category_id: row.amount
        for row in DibuBudget.objects.filter(year=year, month=month).select_related("category")
    }
    spent_by_category = {}
    for row in movements:
        if row.kind != DibuWalletMovement.EXPENSE or not row.category_id:
            continue
        spent_by_category[row.category_id] = spent_by_category.get(row.category_id, ZERO) + Decimal(str(row.amount or 0))

    category_rows = []
    for category in categories:
        spent = spent_by_category.get(category.id, ZERO)
        budget = budgets.get(category.id, ZERO)
        category_rows.append({
            "category": category,
            "spent": spent,
            "budget": budget,
            "left": budget - spent,
            "percent": _percent_of(spent, budget) if budget else 0,
            "share": _percent_of(spent, expense) if expense else 0,
            "over": bool(budget) and spent > budget,
        })
    category_rows.sort(key=lambda row: row["spent"], reverse=True)

    latest_rate = BlueDollarRate.objects.order_by("-date").first()
    suggestion = balance * (wallet_settings.investment_suggestion_percent / Decimal("100")) if balance > 0 else ZERO

    movements_page = Paginator(
        DibuWalletMovement.objects.select_related("category"), 25
    ).get_page(request.GET.get("p"))

    context = {
        "wallet_settings": wallet_settings,
        "currency": currency,
        "symbol": symbol,
        "today": timezone.localdate(),
        "tab": request.GET.get("tab") or "panel",
        "year": year,
        "month": month,
        "month_name": dict(MONTH_NAMES)[month],
        "months": MONTH_NAMES,
        "years": list(range(timezone.localdate().year - 3, timezone.localdate().year + 2)),
        "period_range": period_range,
        "start": start,
        "end": end,
        "income": income,
        "expense": expense,
        "balance": balance,
        "total_balance": total_income - total_expense,
        "categories": categories,
        "category_rows": category_rows,
        "movements_page": movements_page,
        "latest_rate": latest_rate,
        "suggestion": suggestion,
        "movements_count": len(movements),
    }
    return render(request, "calculadora/dibu_wallet.html", context)
