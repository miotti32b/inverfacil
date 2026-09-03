import json

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .contenido import crear_sesion
from .models import Etapa, Opcion, Sesion, Voto


def unirse(request):
    error = None
    if request.method == "POST":
        codigo = request.POST.get("codigo", "").strip().upper()
        sesion = Sesion.objects.filter(codigo=codigo, activa=True).first()
        if sesion:
            return redirect("charla_votacion:sesion", codigo=sesion.codigo)
        error = "No encontramos esa sesión. Revisá el código con el profe."
    return render(request, "charla_votacion/unirse.html", {"error": error})


def sesion_alumno(request, codigo):
    sesion = get_object_or_404(Sesion, codigo=codigo, activa=True)
    return render(request, "charla_votacion/alumno.html", {"sesion": sesion})


def _estado_json(sesion):
    etapa = sesion.etapa_actual
    data = {
        "terminada": sesion.terminada,
        "prompt_final": sesion.prompt_final if sesion.terminada else "",
    }
    if etapa:
        data["etapa"] = {
            "id": etapa.id,
            "titulo": etapa.titulo,
            "descripcion": etapa.descripcion,
            "cerrada": etapa.cerrada,
            "ganadora_id": etapa.ganadora_id,
            "opciones": [
                {"id": o.id, "texto": o.texto, "descripcion": o.descripcion}
                for o in etapa.opciones.all()
            ],
            "resultados": etapa.resultados(),
        }
    else:
        data["etapa"] = None
    return data


def api_estado(request, codigo):
    sesion = get_object_or_404(Sesion, codigo=codigo)
    return JsonResponse(_estado_json(sesion))


@require_POST
def api_votar(request, codigo):
    sesion = get_object_or_404(Sesion, codigo=codigo, activa=True)
    etapa = sesion.etapa_actual
    if not etapa or etapa.cerrada:
        return JsonResponse({"ok": False, "error": "Esta etapa ya cerró."}, status=400)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = request.POST

    opcion_id = payload.get("opcion_id")
    dispositivo_id = (payload.get("dispositivo_id") or "").strip()
    if not opcion_id or not dispositivo_id:
        return JsonResponse({"ok": False, "error": "Faltan datos del voto."}, status=400)

    opcion = get_object_or_404(Opcion, id=opcion_id, etapa=etapa)

    _, creado = Voto.objects.get_or_create(
        etapa=etapa, dispositivo_id=dispositivo_id, defaults={"opcion": opcion}
    )
    if not creado:
        return JsonResponse({"ok": False, "error": "Ya votaste en esta etapa."}, status=400)

    return JsonResponse({"ok": True})


@staff_member_required
def presentador(request, codigo):
    sesion = get_object_or_404(Sesion, codigo=codigo)
    return render(request, "charla_votacion/presentador.html", {"sesion": sesion})


@staff_member_required
@require_POST
def presentador_cerrar_etapa(request, codigo):
    sesion = get_object_or_404(Sesion, codigo=codigo)
    etapa = sesion.etapa_actual
    if etapa and not etapa.cerrada:
        etapa.cerrar_y_elegir_ganadora()
    return JsonResponse(_estado_json(sesion))


@staff_member_required
@require_POST
def presentador_siguiente_etapa(request, codigo):
    sesion = get_object_or_404(Sesion, codigo=codigo)
    etapa = sesion.etapa_actual
    if etapa and not etapa.cerrada:
        etapa.cerrar_y_elegir_ganadora()
    sesion.avanzar()
    return JsonResponse(_estado_json(sesion))


@staff_member_required
def panel(request):
    sesiones = Sesion.objects.order_by("-creada")
    return render(request, "charla_votacion/panel.html", {"sesiones": sesiones})


@staff_member_required
@require_POST
def panel_crear_sesion(request):
    nombre = request.POST.get("nombre", "").strip() or "Charla en vivo"
    sesion = crear_sesion(nombre=nombre)
    return redirect("charla_votacion:panel_resultados", codigo=sesion.codigo)


@staff_member_required
def panel_resultados(request, codigo):
    sesion = get_object_or_404(Sesion, codigo=codigo)
    etapas = []
    for etapa in sesion.etapas.order_by("orden"):
        resultados = etapa.resultados()
        total = sum(r["votos"] for r in resultados) or 1
        etapas.append({"etapa": etapa, "resultados": resultados, "total": total})
    return render(
        request,
        "charla_votacion/resultados.html",
        {"sesion": sesion, "etapas": etapas},
    )
