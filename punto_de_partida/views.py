import random
import uuid
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from . import constants as c
from . import logic
from .models import HistorialCapital, Miembro, Participante, Partida, Voto


def json_no_store(data, status=200):
    response = JsonResponse(data, status=status)
    response["Cache-Control"] = "no-store"
    return response


def _token_session_key(partida_id):
    return f"pdp_token_{partida_id}"


def _opcion_conservadora(ronda):
    return {1: "ahorros", 2: "banco", 3: "mirar", 5: "normal"}.get(ronda, "")


def _leaderboard(participantes):
    ordenado = sorted(participantes, key=lambda p: p.capital_actual, reverse=True)
    return [
        {"nombre": p.nombre, "tipo": p.tipo, "capital_actual": str(p.capital_actual)}
        for p in ordenado
    ]


def _get_partida_de_host(request, codigo):
    return get_object_or_404(Partida, codigo=codigo, host_user=request.user)


def _get_miembro_de_sesion(request, partida):
    token = request.session.get(_token_session_key(partida.id))
    if not token:
        return None
    return (
        Miembro.objects.filter(token=token, participante__partida_id=partida.id)
        .select_related("participante")
        .first()
    )


# --- Vistas del host ---

@staff_member_required
def host_crear_partida(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()[:120]
        codigo = logic.generar_codigo()
        intentos = 0
        while Partida.objects.filter(codigo=codigo).exists() and intentos < 10:
            codigo = logic.generar_codigo()
            intentos += 1
        partida = Partida.objects.create(codigo=codigo, nombre=nombre, host_user=request.user)
        return redirect("punto_de_partida:host_lobby", codigo=partida.codigo)
    return render(request, "punto_de_partida/host_crear.html")


@staff_member_required
def host_lobby(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    return render(request, "punto_de_partida/host_lobby.html", {"partida": partida})


@staff_member_required
def host_final(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    return render(request, "punto_de_partida/host_final.html", {"partida": partida})


@staff_member_required
@require_GET
def host_estado(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    participantes = list(partida.participantes.prefetch_related("miembros").all())

    data = {
        "success": True,
        "codigo": partida.codigo,
        "estado_partida": partida.estado,
        "ronda_actual": partida.ronda_actual,
        "ronda_estado": partida.ronda_estado,
        "total_participantes": len(participantes),
    }

    if partida.estado == Partida.LOBBY:
        data["lobby_participantes"] = [
            {"nombre": p.nombre, "tipo": p.tipo, "miembros": p.miembros.count()}
            for p in participantes
        ]
    else:
        data["leaderboard"] = _leaderboard(participantes)

    if partida.estado == Partida.EN_CURSO and partida.ronda_estado == Partida.RONDA_ACTIVA:
        detalle_votos = []
        votos_recibidos = 0
        for p in participantes:
            total_miembros = p.miembros.count()
            miembros_votaron = Voto.objects.filter(participante=p, ronda=partida.ronda_actual).count()
            if miembros_votaron > 0:
                votos_recibidos += 1
            detalle_votos.append({
                "participante": p.nombre,
                "miembros_votaron": miembros_votaron,
                "miembros_total": total_miembros,
            })
        data["votos_recibidos"] = votos_recibidos
        data["votos_totales_esperados"] = len(participantes)
        data["detalle_votos"] = detalle_votos

    if partida.estado == Partida.FINALIZADA:
        data["podio"] = _leaderboard(participantes)

    return json_no_store(data)


@staff_member_required
@require_POST
def host_iniciar_partida(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    updated = Partida.objects.filter(id=partida.id, estado=Partida.LOBBY).update(
        estado=Partida.EN_CURSO, ronda_actual=1
    )
    if not updated:
        return json_no_store({"success": False, "error": "ya_iniciada"}, status=409)

    with transaction.atomic():
        miembros = list(
            Miembro.objects.filter(participante__partida_id=partida.id).select_related("participante")
        )
        if not miembros:
            Partida.objects.filter(id=partida.id).update(estado=Partida.LOBBY, ronda_actual=0)
            return json_no_store({"success": False, "error": "sin_participantes"}, status=400)

        rng = random.Random()
        pesos = []
        for m in miembros:
            tier, peso = logic.elegir_tier_peso(rng)
            m.peso_tier = tier
            m.peso_valor = peso
            m.habilidad = logic.elegir_habilidad(rng)
            pesos.append((m.id, peso))
        montos = logic.asignar_capital_inicial(pesos)
        for m in miembros:
            m.monto_asignado = montos[m.id]
        Miembro.objects.bulk_update(miembros, ["peso_tier", "peso_valor", "habilidad", "monto_asignado"])

        participantes = list(Participante.objects.filter(partida_id=partida.id).prefetch_related("miembros"))
        historial_bulk = []
        for p in participantes:
            miembros_p = list(p.miembros.all())
            capital_inicial = sum((m.monto_asignado for m in miembros_p), Decimal("0"))
            deuda_inicial = sum(
                (c.DEUDA_INICIAL_MONTO for m in miembros_p if m.peso_tier == "deuda_inicial"), Decimal("0")
            )
            p.capital_inicial = capital_inicial
            p.capital_actual = capital_inicial
            p.deuda = deuda_inicial
            p.colchon_disponible = any(m.habilidad == "colchon_familiar" for m in miembros_p)
            historial_bulk.append(
                HistorialCapital(participante=p, ronda=0, capital=capital_inicial, deuda=deuda_inicial)
            )
        Participante.objects.bulk_update(
            participantes, ["capital_inicial", "capital_actual", "deuda", "colchon_disponible"]
        )
        HistorialCapital.objects.bulk_create(historial_bulk)

    return json_no_store({"success": True})


@staff_member_required
@require_POST
def host_iniciar_ronda(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    updated = Partida.objects.filter(
        id=partida.id, estado=Partida.EN_CURSO, ronda_estado=Partida.RONDA_INACTIVA
    ).update(ronda_estado=Partida.RONDA_ACTIVA)
    if not updated:
        return json_no_store({"success": False, "error": "no_se_pudo_iniciar"}, status=409)
    return json_no_store({"success": True})


@staff_member_required
@require_POST
def host_revelar_ronda(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    updated = Partida.objects.filter(id=partida.id, ronda_estado=Partida.RONDA_ACTIVA).update(
        ronda_estado=Partida.RONDA_REVELADA
    )
    if not updated:
        return json_no_store({"success": False, "error": "ronda_no_activa"}, status=409)

    ronda = partida.ronda_actual
    rng = random.Random()

    with transaction.atomic():
        participantes = list(
            Participante.objects.filter(partida_id=partida.id).prefetch_related("miembros", "votos")
        )
        historial_bulk = []
        for p in participantes:
            miembros_p = list(p.miembros.all())
            habilidades = [m.habilidad for m in miembros_p if m.habilidad]

            if ronda in (1, 2, 3, 5):
                votos_ronda = [v.opcion for v in p.votos.all() if v.ronda == ronda]
                if p.tipo == Participante.EQUIPO:
                    opcion = logic.tally_voto_equipo(votos_ronda, len(miembros_p), _opcion_conservadora(ronda))
                else:
                    opcion = votos_ronda[0] if votos_ronda else _opcion_conservadora(ronda)
            else:
                opcion = None  # rondas 4 y 6 son automáticas

            resultado = logic.resolver_ronda_participante(
                ronda, opcion, p.capital_actual, p.deuda, habilidades,
                p.colchon_disponible, p.colchon_usado, p.penalizacion_ronda2, rng,
            )
            p.capital_actual = resultado["capital_nuevo"]
            p.deuda = p.deuda + resultado.get("deuda_delta", Decimal("0"))
            if "penalizacion_ronda2" in resultado:
                p.penalizacion_ronda2 = resultado["penalizacion_ronda2"]
            if resultado.get("colchon_usado"):
                p.colchon_usado = True

            detalle = dict(resultado["detalle"])
            detalle["opcion_elegida"] = opcion
            historial_bulk.append(
                HistorialCapital(participante=p, ronda=ronda, capital=p.capital_actual, deuda=p.deuda, detalle=detalle)
            )

        Participante.objects.bulk_update(
            participantes, ["capital_actual", "deuda", "penalizacion_ronda2", "colchon_usado"]
        )
        HistorialCapital.objects.bulk_create(historial_bulk)

    return json_no_store({"success": True})


@staff_member_required
@require_POST
def host_siguiente_ronda(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    if partida.estado != Partida.EN_CURSO or partida.ronda_estado != Partida.RONDA_REVELADA:
        return json_no_store({"success": False, "error": "ronda_no_revelada"}, status=409)

    if partida.ronda_actual >= c.TOTAL_RONDAS:
        updated = Partida.objects.filter(
            id=partida.id, estado=Partida.EN_CURSO, ronda_estado=Partida.RONDA_REVELADA
        ).update(estado=Partida.FINALIZADA)
    else:
        updated = Partida.objects.filter(
            id=partida.id, estado=Partida.EN_CURSO, ronda_estado=Partida.RONDA_REVELADA
        ).update(ronda_actual=partida.ronda_actual + 1, ronda_estado=Partida.RONDA_INACTIVA)
    if not updated:
        return json_no_store({"success": False, "error": "no_se_pudo_avanzar"}, status=409)
    return json_no_store({"success": True})


# --- Vistas del jugador (sin login, identidad por sesión) ---

def jugador_unirse(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)

    if partida.estado == Partida.FINALIZADA:
        return render(request, "punto_de_partida/jugador_unirse.html", {
            "partida": partida, "error": "La partida ya terminó."
        })

    miembro = _get_miembro_de_sesion(request, partida)
    if miembro:
        return redirect("punto_de_partida:jugador_jugar", codigo=codigo)

    if partida.estado != Partida.LOBBY:
        return render(request, "punto_de_partida/jugador_unirse.html", {
            "partida": partida, "error": "La partida ya arrancó, no te podés unir ahora."
        })

    if request.method == "POST":
        modo = request.POST.get("modo", "")
        nombre = request.POST.get("nombre", "").strip()[:60]
        codigo_equipo_ingresado = request.POST.get("codigo_equipo", "").strip().upper()
        error = None
        participante = None

        if not nombre:
            error = "Ingresá tu nombre."
        elif modo not in ("individual", "crear_equipo", "unirse_equipo"):
            error = "Elegí una opción válida."

        if not error:
            try:
                with transaction.atomic():
                    if modo == "individual":
                        participante = Participante.objects.create(
                            partida=partida, tipo=Participante.INDIVIDUAL, nombre=nombre
                        )
                    elif modo == "crear_equipo":
                        codigo_equipo = logic.generar_codigo(4)
                        intentos = 0
                        while (
                            Participante.objects.filter(partida=partida, codigo_equipo=codigo_equipo).exists()
                            and intentos < 10
                        ):
                            codigo_equipo = logic.generar_codigo(4)
                            intentos += 1
                        participante = Participante.objects.create(
                            partida=partida, tipo=Participante.EQUIPO, nombre=nombre, codigo_equipo=codigo_equipo
                        )
                    else:  # unirse_equipo
                        participante = Participante.objects.select_for_update().get(
                            partida=partida, tipo=Participante.EQUIPO, codigo_equipo=codigo_equipo_ingresado
                        )
                        if participante.miembros.count() >= 4:
                            error = "Ese equipo ya está completo (máximo 4 integrantes)."
                            participante = None

                    if participante is not None:
                        token = uuid.uuid4().hex
                        Miembro.objects.create(participante=participante, token=token, nombre=nombre)
                        request.session[_token_session_key(partida.id)] = token
            except Participante.DoesNotExist:
                error = "No encontramos ese código de equipo."
            except IntegrityError:
                error = "Ese nombre ya está en uso en esta partida, probá con otro."

        if error:
            return render(request, "punto_de_partida/jugador_unirse.html", {"partida": partida, "error": error})
        return redirect("punto_de_partida:jugador_jugar", codigo=codigo)

    return render(request, "punto_de_partida/jugador_unirse.html", {"partida": partida})


def jugador_jugar(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    miembro = _get_miembro_de_sesion(request, partida)
    if not miembro:
        return redirect("punto_de_partida:jugador_unirse", codigo=codigo)
    return render(request, "punto_de_partida/jugador_jugar.html", {"partida": partida, "miembro": miembro})


@require_GET
def jugador_estado(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    miembro = _get_miembro_de_sesion(request, partida)
    if not miembro:
        return json_no_store({"success": False, "error": "no_unido"}, status=401)
    participante = miembro.participante

    data = {
        "success": True,
        "estado_partida": partida.estado,
        "ronda_actual": partida.ronda_actual,
        "ronda_estado": partida.ronda_estado,
        "mi_nombre": miembro.nombre,
        "mi_habilidad": c.HABILIDADES.get(miembro.habilidad, {}).get("nombre", "") if miembro.habilidad else "",
    }

    if partida.estado == Partida.LOBBY:
        data["participante"] = {
            "nombre": participante.nombre,
            "tipo": participante.tipo,
            "codigo_equipo": participante.codigo_equipo,
            "miembros": participante.miembros.count(),
        }
        return json_no_store(data)

    data["mi_participante"] = {
        "tipo": participante.tipo,
        "nombre": participante.nombre,
        "capital_actual": str(participante.capital_actual),
        "deuda": str(participante.deuda),
    }

    if partida.estado == Partida.EN_CURSO and partida.ronda_estado == Partida.RONDA_ACTIVA:
        ronda_cfg = next((r for r in c.RONDAS if r["numero"] == partida.ronda_actual), None)
        habilidades = (
            participante.habilidades()
            if participante.tipo == Participante.EQUIPO
            else ([miembro.habilidad] if miembro.habilidad else [])
        )
        opciones = [
            {
                "id": op["id"],
                "label": op["label"],
                "disponible": logic.opcion_disponible(
                    partida.ronda_actual, op["id"], participante.capital_actual, habilidades
                ),
            }
            for op in (ronda_cfg["opciones"] if ronda_cfg else [])
        ]
        data["opciones"] = opciones
        data["titulo_ronda"] = ronda_cfg["titulo"] if ronda_cfg else ""
        data["descripcion_ronda"] = ronda_cfg["descripcion"] if ronda_cfg else ""
        voto = Voto.objects.filter(miembro=miembro, ronda=partida.ronda_actual).first()
        data["ya_vote"] = voto is not None
        data["mi_voto"] = voto.opcion if voto else None

    if partida.ronda_estado == Partida.RONDA_REVELADA and partida.ronda_actual >= 1:
        historial = HistorialCapital.objects.filter(participante=participante, ronda=partida.ronda_actual).first()
        if historial:
            data["resultado_ultima_ronda"] = {"capital": str(historial.capital), "detalle": historial.detalle}

    if partida.estado == Partida.FINALIZADA:
        todos = Participante.objects.filter(partida=partida).order_by("-capital_actual")
        data["podio"] = [{"nombre": p.nombre, "capital_actual": str(p.capital_actual)} for p in todos]
        data["historial_propio"] = [
            {"ronda": h.ronda, "capital": str(h.capital)}
            for h in HistorialCapital.objects.filter(participante=participante).order_by("ronda")
        ]

    return json_no_store(data)


@require_POST
def jugador_votar(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    miembro = _get_miembro_de_sesion(request, partida)
    if not miembro:
        return json_no_store({"success": False, "error": "no_unido"}, status=401)
    if partida.estado != Partida.EN_CURSO or partida.ronda_estado != Partida.RONDA_ACTIVA:
        return json_no_store({"success": False, "error": "ronda_no_activa"}, status=409)

    opcion = request.POST.get("opcion", "")
    ronda_cfg = next((r for r in c.RONDAS if r["numero"] == partida.ronda_actual), None)
    ids_validos = {op["id"] for op in (ronda_cfg["opciones"] if ronda_cfg else [])}
    if opcion not in ids_validos:
        return json_no_store({"success": False, "error": "opcion_invalida"}, status=400)

    participante = miembro.participante
    habilidades = (
        participante.habilidades()
        if participante.tipo == Participante.EQUIPO
        else ([miembro.habilidad] if miembro.habilidad else [])
    )
    if not logic.opcion_disponible(partida.ronda_actual, opcion, participante.capital_actual, habilidades):
        return json_no_store({"success": False, "error": "opcion_no_disponible"}, status=400)

    Voto.objects.update_or_create(
        miembro=miembro, ronda=partida.ronda_actual, defaults={"participante": participante, "opcion": opcion}
    )
    return json_no_store({"success": True})
