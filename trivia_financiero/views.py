import random
import uuid

from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from . import constants as c
from . import logic
from .models import Jugador, Miembro, Partida, PartidaPregunta, Pregunta, Respuesta, VotoMiembro


def json_no_store(data, status=200):
    response = JsonResponse(data, status=status)
    response["Cache-Control"] = "no-store"
    return response


def _token_session_key(partida_id):
    return f"tf_token_{partida_id}"


def _get_partida_de_host(request, codigo):
    return get_object_or_404(Partida, codigo=codigo, host_user=request.user)


def _get_miembro_de_sesion(request, partida):
    token = request.session.get(_token_session_key(partida.id))
    if not token:
        return None
    return (
        Miembro.objects.filter(token=token, jugador__partida_id=partida.id)
        .select_related("jugador")
        .first()
    )


def _pregunta_actual(partida):
    return partida.preguntas.filter(orden=partida.pregunta_actual_index).select_related("pregunta").first()


def _leaderboard(jugadores):
    ordenado = sorted(jugadores, key=lambda j: j.puntaje_total, reverse=True)
    return [
        {"nombre": j.nombre, "tipo": j.tipo, "puntaje_total": j.puntaje_total}
        for j in ordenado
    ]


# --- Panel (estilo charla_votacion, tema claro) ---

@staff_member_required
def panel(request):
    partidas = Partida.objects.filter(host_user=request.user).order_by("-creado_en")
    return render(request, "trivia_financiero/panel.html", {"partidas": partidas})


@staff_member_required
@require_POST
def panel_crear(request):
    nombre = request.POST.get("nombre", "").strip()[:120] or "Charla en vivo"
    colegio = request.POST.get("colegio", "").strip()[:120]
    curso = request.POST.get("curso", "").strip()[:60]

    codigo = logic.generar_codigo()
    intentos = 0
    while Partida.objects.filter(codigo=codigo).exists() and intentos < 10:
        codigo = logic.generar_codigo()
        intentos += 1

    partida = Partida.objects.create(
        codigo=codigo, nombre=nombre, colegio=colegio, curso=curso, host_user=request.user
    )
    return redirect("trivia_financiero:host_lobby", codigo=partida.codigo)


@staff_member_required
def panel_resultado(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    filas = []
    for pp in partida.preguntas.select_related("pregunta").order_by("orden"):
        respuestas = Respuesta.objects.filter(partida_pregunta=pp)
        total = respuestas.count()
        correctas = respuestas.filter(es_correcta=True).count()
        filas.append({
            "pregunta": pp.pregunta,
            "total": total,
            "correctas": correctas,
            "pct": round(100 * correctas / total) if total else None,
        })
    jugadores = list(partida.jugadores.all())
    return render(request, "trivia_financiero/panel_resultado.html", {
        "partida": partida, "filas": filas, "podio": _leaderboard(jugadores),
    })


@staff_member_required
def panel_estadisticas(request):
    colegio = request.GET.get("colegio", "").strip()
    curso = request.GET.get("curso", "").strip()

    partidas_qs = Partida.objects.filter(host_user=request.user)
    colegios = sorted(v for v in partidas_qs.values_list("colegio", flat=True).distinct() if v)
    cursos = sorted(v for v in partidas_qs.values_list("curso", flat=True).distinct() if v)

    qs = Respuesta.objects.filter(jugador__partida__host_user=request.user)
    if colegio:
        qs = qs.filter(jugador__partida__colegio=colegio)
    if curso:
        qs = qs.filter(jugador__partida__curso=curso)

    por_pregunta = (
        qs.values("partida_pregunta__pregunta__id", "partida_pregunta__pregunta__texto")
        .annotate(total=Count("id"), correctas=Count("id", filter=Q(es_correcta=True)))
        .order_by("correctas")
    )
    filas = [
        {
            "texto": row["partida_pregunta__pregunta__texto"],
            "total": row["total"],
            "correctas": row["correctas"],
            "pct": round(100 * row["correctas"] / row["total"]) if row["total"] else 0,
        }
        for row in por_pregunta
    ]

    partidas_filtradas = partidas_qs
    if colegio:
        partidas_filtradas = partidas_filtradas.filter(colegio=colegio)
    if curso:
        partidas_filtradas = partidas_filtradas.filter(curso=curso)

    return render(request, "trivia_financiero/panel_estadisticas.html", {
        "filas": filas,
        "colegios": colegios,
        "cursos": cursos,
        "colegio_actual": colegio,
        "curso_actual": curso,
        "total_partidas": partidas_filtradas.count(),
    })


# --- Vistas del host (control en vivo) ---

@staff_member_required
def host_lobby(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    return render(request, "trivia_financiero/host_lobby.html", {"partida": partida})


@staff_member_required
@require_GET
def host_estado(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    jugadores = list(partida.jugadores.prefetch_related("miembros").all())

    data = {
        "success": True,
        "codigo": partida.codigo,
        "estado_partida": partida.estado,
        "pregunta_actual_index": partida.pregunta_actual_index,
        "pregunta_estado": partida.pregunta_estado,
        "total_preguntas": c.TOTAL_PREGUNTAS,
        "total_jugadores": len(jugadores),
    }

    if partida.estado == Partida.LOBBY:
        data["lobby_jugadores"] = [
            {"nombre": j.nombre, "tipo": j.tipo, "miembros": j.miembros.count()}
            for j in jugadores
        ]
    else:
        data["leaderboard"] = _leaderboard(jugadores)

    pp = _pregunta_actual(partida)
    if pp:
        data["pregunta_texto"] = pp.pregunta.texto
        if partida.pregunta_estado == Partida.PREGUNTA_ACTIVA:
            data["pregunta_iniciada_en"] = (
                partida.pregunta_iniciada_en.isoformat() if partida.pregunta_iniciada_en else None
            )
            data["duracion_seg"] = c.DURACION_PREGUNTA_SEGUNDOS
            votos_recibidos = 0
            for j in jugadores:
                if VotoMiembro.objects.filter(miembro__jugador=j, partida_pregunta=pp).exists():
                    votos_recibidos += 1
            data["votos_recibidos"] = votos_recibidos
            data["votos_totales_esperados"] = len(jugadores)
        elif partida.pregunta_estado == Partida.PREGUNTA_REVELADA:
            data["explicacion"] = pp.pregunta.explicacion
            data["respuesta_correcta"] = pp.pregunta.respuesta_correcta
            data["opciones"] = pp.pregunta.opciones

    if partida.estado == Partida.FINALIZADA:
        data["podio"] = _leaderboard(jugadores)

    return json_no_store(data)


@staff_member_required
@require_POST
def host_iniciar_partida(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    updated = Partida.objects.filter(id=partida.id, estado=Partida.LOBBY).update(estado=Partida.EN_CURSO)
    if not updated:
        return json_no_store({"success": False, "error": "ya_iniciada"}, status=409)

    if not partida.jugadores.exists():
        Partida.objects.filter(id=partida.id).update(estado=Partida.LOBBY)
        return json_no_store({"success": False, "error": "sin_jugadores"}, status=400)

    rng = random.Random()
    preguntas = logic.seleccionar_preguntas(rng)
    PartidaPregunta.objects.bulk_create([
        PartidaPregunta(partida=partida, pregunta=pregunta, orden=i)
        for i, pregunta in enumerate(preguntas)
    ])
    return json_no_store({"success": True})


@staff_member_required
@require_POST
def host_iniciar_pregunta(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    updated = Partida.objects.filter(
        id=partida.id, estado=Partida.EN_CURSO, pregunta_estado=Partida.PREGUNTA_INACTIVA
    ).update(pregunta_estado=Partida.PREGUNTA_ACTIVA, pregunta_iniciada_en=timezone.now())
    if not updated:
        return json_no_store({"success": False, "error": "no_se_pudo_iniciar"}, status=409)
    return json_no_store({"success": True})


@staff_member_required
@require_POST
def host_revelar_pregunta(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    updated = Partida.objects.filter(id=partida.id, pregunta_estado=Partida.PREGUNTA_ACTIVA).update(
        pregunta_estado=Partida.PREGUNTA_REVELADA
    )
    if not updated:
        return json_no_store({"success": False, "error": "pregunta_no_activa"}, status=409)

    pp = _pregunta_actual(partida)
    if not pp:
        return json_no_store({"success": False, "error": "sin_pregunta_actual"}, status=409)

    with transaction.atomic():
        jugadores = list(Jugador.objects.filter(partida_id=partida.id).prefetch_related("miembros"))
        respuestas_bulk = []
        for j in jugadores:
            miembros = list(j.miembros.all())
            votos = list(VotoMiembro.objects.filter(miembro__in=miembros, partida_pregunta=pp))

            if j.tipo == Jugador.EQUIPO:
                opciones_votadas = [v.opcion_elegida for v in votos]
                opcion_elegida = logic.tally_voto_equipo(opciones_votadas, total_miembros=len(miembros))
                es_correcta = opcion_elegida == pp.pregunta.respuesta_correcta if opcion_elegida is not None else False
                puntos = logic.calcular_puntos_equipo(es_correcta)
                tiempo_ms = None
            else:
                voto = votos[0] if votos else None
                opcion_elegida = voto.opcion_elegida if voto else None
                tiempo_ms = voto.tiempo_ms if voto else None
                es_correcta = opcion_elegida == pp.pregunta.respuesta_correcta if opcion_elegida is not None else False
                puntos = logic.calcular_puntos_individual(es_correcta, tiempo_ms, c.DURACION_PREGUNTA_SEGUNDOS)

            j.puntaje_total += puntos
            respuestas_bulk.append(Respuesta(
                jugador=j, partida_pregunta=pp, opcion_elegida=opcion_elegida,
                es_correcta=es_correcta, puntos_obtenidos=puntos, tiempo_ms=tiempo_ms,
            ))

        Jugador.objects.bulk_update(jugadores, ["puntaje_total"])
        Respuesta.objects.bulk_create(respuestas_bulk)

    return json_no_store({"success": True})


@staff_member_required
@require_POST
def host_siguiente_pregunta(request, codigo):
    partida = _get_partida_de_host(request, codigo)
    if partida.estado != Partida.EN_CURSO or partida.pregunta_estado != Partida.PREGUNTA_REVELADA:
        return json_no_store({"success": False, "error": "pregunta_no_revelada"}, status=409)

    if partida.pregunta_actual_index + 1 >= c.TOTAL_PREGUNTAS:
        updated = Partida.objects.filter(
            id=partida.id, estado=Partida.EN_CURSO, pregunta_estado=Partida.PREGUNTA_REVELADA
        ).update(estado=Partida.FINALIZADA)
    else:
        updated = Partida.objects.filter(
            id=partida.id, estado=Partida.EN_CURSO, pregunta_estado=Partida.PREGUNTA_REVELADA
        ).update(
            pregunta_actual_index=partida.pregunta_actual_index + 1,
            pregunta_estado=Partida.PREGUNTA_INACTIVA,
            pregunta_iniciada_en=None,
        )
    if not updated:
        return json_no_store({"success": False, "error": "no_se_pudo_avanzar"}, status=409)
    return json_no_store({"success": True})


# --- Vistas del jugador (sin login, identidad por sesión) ---

def jugador_unirse(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)

    if partida.estado == Partida.FINALIZADA:
        return render(request, "trivia_financiero/jugador_unirse.html", {
            "partida": partida, "error": "La partida ya terminó."
        })

    miembro = _get_miembro_de_sesion(request, partida)
    if miembro:
        return redirect("trivia_financiero:jugador_jugar", codigo=codigo)

    if partida.estado != Partida.LOBBY:
        return render(request, "trivia_financiero/jugador_unirse.html", {
            "partida": partida, "error": "La partida ya arrancó, no te podés unir ahora."
        })

    if request.method == "POST":
        modo = request.POST.get("modo", "")
        nombre = request.POST.get("nombre", "").strip()[:60]
        codigo_equipo_ingresado = request.POST.get("codigo_equipo", "").strip().upper()
        error = None
        jugador = None

        if not nombre:
            error = "Ingresá tu nombre."
        elif modo not in ("individual", "crear_equipo", "unirse_equipo"):
            error = "Elegí una opción válida."

        if not error:
            try:
                with transaction.atomic():
                    if modo == "individual":
                        jugador = Jugador.objects.create(
                            partida=partida, tipo=Jugador.INDIVIDUAL, nombre=nombre
                        )
                    elif modo == "crear_equipo":
                        codigo_equipo = logic.generar_codigo(4)
                        intentos = 0
                        while (
                            Jugador.objects.filter(partida=partida, codigo_equipo=codigo_equipo).exists()
                            and intentos < 10
                        ):
                            codigo_equipo = logic.generar_codigo(4)
                            intentos += 1
                        jugador = Jugador.objects.create(
                            partida=partida, tipo=Jugador.EQUIPO, nombre=nombre, codigo_equipo=codigo_equipo
                        )
                    else:  # unirse_equipo
                        jugador = Jugador.objects.select_for_update().get(
                            partida=partida, tipo=Jugador.EQUIPO, codigo_equipo=codigo_equipo_ingresado
                        )
                        if jugador.miembros.count() >= c.MAX_INTEGRANTES_EQUIPO:
                            error = f"Ese equipo ya está completo (máximo {c.MAX_INTEGRANTES_EQUIPO})."
                            jugador = None

                    if jugador is not None:
                        token = uuid.uuid4().hex
                        Miembro.objects.create(jugador=jugador, token=token, nombre=nombre)
                        request.session[_token_session_key(partida.id)] = token
            except Jugador.DoesNotExist:
                error = "No encontramos ese código de equipo."
            except IntegrityError:
                error = "Ese nombre ya está en uso en esta partida, probá con otro."

        if error:
            return render(request, "trivia_financiero/jugador_unirse.html", {"partida": partida, "error": error})
        return redirect("trivia_financiero:jugador_jugar", codigo=codigo)

    return render(request, "trivia_financiero/jugador_unirse.html", {"partida": partida})


def jugador_jugar(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    miembro = _get_miembro_de_sesion(request, partida)
    if not miembro:
        return redirect("trivia_financiero:jugador_unirse", codigo=codigo)
    return render(request, "trivia_financiero/jugador_jugar.html", {"partida": partida, "miembro": miembro})


@require_GET
def jugador_estado(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    miembro = _get_miembro_de_sesion(request, partida)
    if not miembro:
        return json_no_store({"success": False, "error": "no_unido"}, status=401)
    jugador = miembro.jugador

    data = {
        "success": True,
        "estado_partida": partida.estado,
        "pregunta_actual_index": partida.pregunta_actual_index,
        "pregunta_estado": partida.pregunta_estado,
        "total_preguntas": c.TOTAL_PREGUNTAS,
        "duracion_seg": c.DURACION_PREGUNTA_SEGUNDOS,
        "mi_nombre": miembro.nombre,
    }

    if partida.estado == Partida.LOBBY:
        data["jugador"] = {
            "nombre": jugador.nombre, "tipo": jugador.tipo,
            "codigo_equipo": jugador.codigo_equipo, "miembros": jugador.miembros.count(),
        }
        return json_no_store(data)

    data["mi_puntaje"] = jugador.puntaje_total

    pp = _pregunta_actual(partida)
    if pp and partida.estado == Partida.EN_CURSO:
        if partida.pregunta_estado == Partida.PREGUNTA_ACTIVA:
            data["pregunta_texto"] = pp.pregunta.texto
            data["opciones"] = pp.pregunta.opciones
            data["pregunta_iniciada_en"] = partida.pregunta_iniciada_en.isoformat() if partida.pregunta_iniciada_en else None
            voto = VotoMiembro.objects.filter(miembro=miembro, partida_pregunta=pp).first()
            data["ya_vote"] = voto is not None
            data["mi_voto"] = voto.opcion_elegida if voto else None
        elif partida.pregunta_estado == Partida.PREGUNTA_REVELADA:
            data["pregunta_texto"] = pp.pregunta.texto
            data["opciones"] = pp.pregunta.opciones
            data["respuesta_correcta"] = pp.pregunta.respuesta_correcta
            data["explicacion"] = pp.pregunta.explicacion
            mi_respuesta = Respuesta.objects.filter(jugador=jugador, partida_pregunta=pp).first()
            if mi_respuesta:
                data["mi_resultado"] = {
                    "opcion_elegida": mi_respuesta.opcion_elegida,
                    "es_correcta": mi_respuesta.es_correcta,
                    "puntos_obtenidos": mi_respuesta.puntos_obtenidos,
                }

    if partida.estado == Partida.FINALIZADA:
        todos = Jugador.objects.filter(partida=partida).order_by("-puntaje_total")
        data["podio"] = [{"nombre": j.nombre, "puntaje_total": j.puntaje_total} for j in todos]

    return json_no_store(data)


@require_POST
def jugador_votar(request, codigo):
    partida = get_object_or_404(Partida, codigo=codigo)
    miembro = _get_miembro_de_sesion(request, partida)
    if not miembro:
        return json_no_store({"success": False, "error": "no_unido"}, status=401)
    if partida.estado != Partida.EN_CURSO or partida.pregunta_estado != Partida.PREGUNTA_ACTIVA:
        return json_no_store({"success": False, "error": "pregunta_no_activa"}, status=409)

    if logic.tiempo_agotado(partida.pregunta_iniciada_en, timezone.now(), c.DURACION_PREGUNTA_SEGUNDOS):
        return json_no_store({"success": False, "error": "tiempo_agotado"}, status=409)

    try:
        opcion_elegida = int(request.POST.get("opcion", ""))
    except (TypeError, ValueError):
        return json_no_store({"success": False, "error": "opcion_invalida"}, status=400)

    pp = _pregunta_actual(partida)
    if not pp or not (0 <= opcion_elegida < len(pp.pregunta.opciones)):
        return json_no_store({"success": False, "error": "opcion_invalida"}, status=400)

    tiempo_ms = max(0, int((timezone.now() - partida.pregunta_iniciada_en).total_seconds() * 1000))

    VotoMiembro.objects.update_or_create(
        miembro=miembro, partida_pregunta=pp,
        defaults={"opcion_elegida": opcion_elegida, "tiempo_ms": tiempo_ms},
    )
    return json_no_store({"success": True})
