from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from calculadora.models import ClientePerfil

from .infografias import infografia_para_numero
from .models import (
    Curso,
    IntentoQuiz,
    Modulo,
    OpcionRespuesta,
    ProgresoCurso,
    ProgresoModulo,
    Quiz,
    RespuestaAlumno,
)


CURSO_SLUG = "finanzas-tecnologia-emprendimiento-30-dias"
PLAN_PREMIUM = 3


def _curso():
    return get_object_or_404(Curso, slug=CURSO_SLUG, activo=True)


def _perfil(request):
    if not request.user.is_authenticated:
        return None
    return ClientePerfil.objects.filter(user=request.user).first()


def _es_premium(request):
    perfil = _perfil(request)
    return bool(perfil and perfil.plan_activo == PLAN_PREMIUM)


def _ensure_progress(user, curso):
    progreso_curso, _ = ProgresoCurso.objects.get_or_create(usuario=user, curso=curso)
    modulos = list(curso.modulos.filter(activo=True).order_by("numero"))
    previous_completed = True

    for modulo in modulos:
        progreso, created = ProgresoModulo.objects.get_or_create(
            usuario=user,
            modulo=modulo,
            defaults={
                "estado": Modulo.ESTADO_DISPONIBLE if previous_completed else Modulo.ESTADO_BLOQUEADO,
            },
        )
        if progreso.estado != Modulo.ESTADO_COMPLETADO:
            expected = Modulo.ESTADO_DISPONIBLE if previous_completed else Modulo.ESTADO_BLOQUEADO
            if progreso.estado != expected:
                progreso.estado = expected
                progreso.save(update_fields=["estado", "actualizado_en"])
        previous_completed = progreso.estado == Modulo.ESTADO_COMPLETADO

    progreso_curso.recalcular()
    return progreso_curso


def _module_items(user, curso):
    _ensure_progress(user, curso)
    items = []
    for modulo in curso.modulos.filter(activo=True).order_by("numero"):
        progreso = ProgresoModulo.objects.get(usuario=user, modulo=modulo)
        items.append({
            "modulo": modulo,
            "progreso": progreso,
            "estado": progreso.estado,
        })
    return items


def _get_available_progress(user, modulo):
    _ensure_progress(user, modulo.curso)
    progreso = get_object_or_404(ProgresoModulo, usuario=user, modulo=modulo)
    return progreso


def curso_landing(request):
    curso = _curso()
    if request.user.is_authenticated and _es_premium(request):
        return redirect("curso_acelerado:panel")
    return render(request, "curso_acelerado/curso_landing.html", {"curso": curso})


def curso_bloqueado(request):
    curso = _curso()
    return render(request, "curso_acelerado/curso_bloqueado.html", {"curso": curso})


@login_required(login_url="/accounts/google/login/")
def curso_panel(request):
    if not _es_premium(request):
        return redirect("curso_acelerado:bloqueado")
    curso = _curso()
    progreso_curso = _ensure_progress(request.user, curso)
    return render(request, "curso_acelerado/curso_panel.html", {
        "curso": curso,
        "progreso_curso": progreso_curso,
        "items": _module_items(request.user, curso),
    })


@login_required(login_url="/accounts/google/login/")
def modulo_detalle(request, modulo_id):
    if not _es_premium(request):
        return redirect("curso_acelerado:bloqueado")
    modulo = get_object_or_404(Modulo, id=modulo_id, activo=True, curso__slug=CURSO_SLUG)
    progreso = _get_available_progress(request.user, modulo)
    if progreso.estado == Modulo.ESTADO_BLOQUEADO:
        return redirect("curso_acelerado:panel")
    quiz = getattr(modulo, "quiz", None)
    return render(request, "curso_acelerado/modulo_detalle.html", {
        "modulo": modulo,
        "progreso": progreso,
        "quiz": quiz,
        "preguntas": quiz.preguntas.prefetch_related("opciones") if quiz else [],
        "diagnostico": modulo.preguntas_diagnostico.prefetch_related("opciones"),
        "infografia": infografia_para_numero(modulo.numero),
    })


@login_required(login_url="/accounts/google/login/")
@require_POST
def quiz_submit(request, modulo_id):
    if not _es_premium(request):
        return redirect("curso_acelerado:bloqueado")
    modulo = get_object_or_404(Modulo, id=modulo_id, activo=True, curso__slug=CURSO_SLUG)
    progreso = _get_available_progress(request.user, modulo)
    if progreso.estado == Modulo.ESTADO_BLOQUEADO:
        return redirect("curso_acelerado:panel")

    quiz = get_object_or_404(Quiz, modulo=modulo, activo=True)
    preguntas = list(quiz.preguntas.prefetch_related("opciones"))
    total = len(preguntas)
    correctas = 0

    intento = IntentoQuiz.objects.create(
        usuario=request.user,
        quiz=quiz,
        total_preguntas=total,
    )

    for pregunta in preguntas:
        opcion_id = request.POST.get(f"pregunta_{pregunta.id}")
        if not opcion_id:
            continue
        opcion = OpcionRespuesta.objects.filter(id=opcion_id, pregunta=pregunta).first()
        if not opcion:
            continue
        es_correcta = opcion.es_correcta
        if es_correcta:
            correctas += 1
        RespuestaAlumno.objects.create(
            intento=intento,
            pregunta=pregunta,
            opcion=opcion,
            es_correcta=es_correcta,
        )

    puntaje = Decimal("0")
    if total:
        puntaje = Decimal(correctas * 100) / Decimal(total)
    aprobado = puntaje >= Decimal(quiz.porcentaje_aprobacion)

    intento.correctas = correctas
    intento.puntaje = puntaje
    intento.aprobado = aprobado
    intento.save(update_fields=["correctas", "puntaje", "aprobado"])

    progreso.intentos += 1
    progreso.mejor_puntaje = max(progreso.mejor_puntaje, puntaje)
    progreso.save(update_fields=["intentos", "mejor_puntaje", "actualizado_en"])

    if aprobado:
        progreso.marcar_completado(puntaje)
        siguiente = Modulo.objects.filter(curso=modulo.curso, activo=True, numero=modulo.numero + 1).first()
        if siguiente:
            progreso_siguiente, _ = ProgresoModulo.objects.get_or_create(
                usuario=request.user,
                modulo=siguiente,
                defaults={"estado": Modulo.ESTADO_DISPONIBLE},
            )
            if progreso_siguiente.estado == Modulo.ESTADO_BLOQUEADO:
                progreso_siguiente.estado = Modulo.ESTADO_DISPONIBLE
                progreso_siguiente.save(update_fields=["estado", "actualizado_en"])
    ProgresoCurso.objects.get(usuario=request.user, curso=modulo.curso).recalcular()

    return redirect(reverse("curso_acelerado:resultado_quiz", args=[intento.id]))


@login_required(login_url="/accounts/google/login/")
def resultado_quiz(request, intento_id):
    if not _es_premium(request):
        return redirect("curso_acelerado:bloqueado")
    intento = get_object_or_404(IntentoQuiz, id=intento_id, usuario=request.user)
    return render(request, "curso_acelerado/resultado_quiz.html", {"intento": intento})


@login_required(login_url="/accounts/google/login/")
def progreso_general(request):
    if not _es_premium(request):
        return redirect("curso_acelerado:bloqueado")
    curso = _curso()
    progreso_curso = _ensure_progress(request.user, curso)
    return render(request, "curso_acelerado/curso_panel.html", {
        "curso": curso,
        "progreso_curso": progreso_curso,
        "items": _module_items(request.user, curso),
        "vista_progreso": True,
    })

# Create your views here.
