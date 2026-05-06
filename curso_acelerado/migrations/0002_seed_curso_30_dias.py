from django.db import migrations


CURSO = {
    "titulo": "Finanzas, Tecnologia y Emprendimiento en 30 dias",
    "slug": "finanzas-tecnologia-emprendimiento-30-dias",
    "descripcion": (
        "Curso acelerado para ordenar finanzas, entender tecnologia aplicada y "
        "pensar emprendimientos modernos con criterio."
    ),
}


MODULOS = [
    (
        1,
        "Mentalidad financiera y mapa del dinero",
        "Que el alumno entienda como funciona el dinero en la vida real.",
        [
            "Ingresos, gastos, ahorro, deuda e inversion.",
            "Libertad financiera.",
            "Carrera de la rata.",
            "Errores financieros comunes.",
            "Como piensa una persona financieramente ordenada.",
        ],
    ),
    (
        2,
        "Finanzas personales aplicadas",
        "Que el alumno aprenda a ordenar su economia.",
        [
            "Presupuesto mensual.",
            "Fondo de emergencia.",
            "Control de gastos.",
            "Deuda buena y deuda mala.",
            "Objetivos financieros personales.",
        ],
    ),
    (
        3,
        "Inversiones desde cero",
        "Introducir al alumno en el mundo de las inversiones.",
        [
            "Acciones, bonos y fondos comunes de inversion.",
            "Cauciones, dolar y criptoactivos.",
            "Riesgo, liquidez y rentabilidad.",
            "Interes compuesto.",
            "Perfil de inversor.",
        ],
    ),
    (
        4,
        "Tecnologia para la vida y el trabajo",
        "Mostrar como usar herramientas digitales para mejorar la productividad.",
        [
            "Google Sheets.",
            "Organizacion digital.",
            "Automatizaciones simples.",
            "IA generativa.",
            "Herramientas para estudiar, trabajar y emprender.",
        ],
    ),
    (
        5,
        "Programacion para no programadores",
        "Explicar la logica de la programacion de forma simple.",
        [
            "Que es programar.",
            "Variables, condicionales, funciones y datos.",
            "HTML, CSS, JavaScript y Python.",
            "Que es una app web.",
        ],
    ),
    (
        6,
        "Inteligencia Artificial aplicada",
        "Ensenar a usar IA para estudiar, trabajar, vender y crear.",
        [
            "Que es la inteligencia artificial.",
            "Prompts efectivos.",
            "Casos de uso en negocios, finanzas y marketing.",
            "Automatizacion con IA.",
        ],
    ),
    (
        7,
        "Emprendimiento moderno",
        "Ensenar como pensar y validar una idea de negocio.",
        [
            "Problema, solucion y cliente.",
            "Propuesta de valor.",
            "MVP y modelo de negocio.",
            "Validacion rapida.",
            "Errores comunes al emprender.",
        ],
    ),
    (
        8,
        "Marketing digital y ventas",
        "Que el alumno aprenda a comunicar y vender mejor.",
        [
            "Marca personal.",
            "Redes sociales y contenido educativo.",
            "Embudo de ventas.",
            "Oferta irresistible.",
            "Confianza, autoridad y conversion.",
        ],
    ),
    (
        9,
        "Automatizacion y sistemas para negocios",
        "Mostrar como la tecnologia permite escalar negocios.",
        [
            "Procesos repetitivos.",
            "CRM y ERP.",
            "Formularios y bases de datos.",
            "WhatsApp automation y email automation.",
            "Dashboards e indicadores.",
        ],
    ),
    (
        10,
        "Integracion final: finanzas, tecnologia y emprendimiento",
        "Unir todo lo aprendido.",
        [
            "Como detectar oportunidades.",
            "Como pensar un negocio digital.",
            "Como usar tecnologia para ganar eficiencia.",
            "Como tomar decisiones financieras.",
            "Introduccion al juego final, reservado para una etapa posterior.",
        ],
    ),
]


def forwards(apps, schema_editor):
    Curso = apps.get_model("curso_acelerado", "Curso")
    Modulo = apps.get_model("curso_acelerado", "Modulo")
    Quiz = apps.get_model("curso_acelerado", "Quiz")
    Pregunta = apps.get_model("curso_acelerado", "Pregunta")
    OpcionRespuesta = apps.get_model("curso_acelerado", "OpcionRespuesta")

    curso, _ = Curso.objects.get_or_create(
        slug=CURSO["slug"],
        defaults={
            "titulo": CURSO["titulo"],
            "descripcion": CURSO["descripcion"],
            "activo": True,
        },
    )

    for numero, titulo, objetivo, contenidos in MODULOS:
        contenido_teorico = (
            f"Objetivo del modulo: {objetivo}\n\n"
            "Contenidos principales:\n"
            + "\n".join(f"- {item}" for item in contenidos)
            + "\n\nEste contenido es una base editable desde Django Admin. "
            "Podes expandirlo con ejemplos, casos reales, infografias y material propio."
        )
        modulo, _ = Modulo.objects.get_or_create(
            curso=curso,
            numero=numero,
            defaults={
                "titulo": titulo,
                "objetivo": objetivo,
                "descripcion": " ".join(contenidos),
                "contenido_teorico": contenido_teorico,
                "youtube_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "imagen_url": "",
                "activo": True,
            },
        )
        quiz, _ = Quiz.objects.get_or_create(
            modulo=modulo,
            defaults={
                "titulo": f"Quiz modulo {numero}",
                "porcentaje_aprobacion": 70,
                "activo": True,
            },
        )
        pregunta, created = Pregunta.objects.get_or_create(
            quiz=quiz,
            orden=1,
            defaults={
                "texto": f"Para aprobar este modulo, cual es la idea central de '{titulo}'?",
                "explicacion": "Pregunta base editable desde el admin.",
            },
        )
        if created:
            OpcionRespuesta.objects.create(
                pregunta=pregunta,
                texto=objetivo,
                es_correcta=True,
                orden=1,
            )
            OpcionRespuesta.objects.create(
                pregunta=pregunta,
                texto="Memorizar conceptos sin aplicarlos.",
                es_correcta=False,
                orden=2,
            )
            OpcionRespuesta.objects.create(
                pregunta=pregunta,
                texto="Evitar tomar decisiones hasta tener certeza absoluta.",
                es_correcta=False,
                orden=3,
            )


def backwards(apps, schema_editor):
    Curso = apps.get_model("curso_acelerado", "Curso")
    Curso.objects.filter(slug=CURSO["slug"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("curso_acelerado", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
