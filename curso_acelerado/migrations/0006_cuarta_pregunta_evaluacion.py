from django.db import migrations


CUARTA_PREGUNTA = {
    1: (
        "Segun el modulo, que caracteriza a una persona financieramente ordenada?",
        [
            ("Registra sus movimientos, prioriza el ahorro y evita la deuda mala.", True),
            ("Gasta primero y ahorra solo si le sobra algo.", False),
            ("Nunca registra en que se le va el dinero.", False),
            ("Evita cualquier tipo de ahorro.", False),
        ],
    ),
    2: (
        "Segun el modulo, como conviene clasificar los objetivos financieros personales?",
        [
            ("En corto, mediano y largo plazo.", True),
            ("Solo en objetivos de corto plazo.", False),
            ("No hace falta clasificarlos.", False),
            ("Unicamente en objetivos imposibles de lograr.", False),
        ],
    ),
    3: (
        "Segun el modulo, de que depende el perfil de inversor de una persona?",
        [
            ("De cuanto riesgo esta dispuesta a asumir y en cuanto tiempo planea usar el dinero.", True),
            ("Unicamente de cuanto dinero tiene ahorrado.", False),
            ("De la edad exacta que tiene la persona.", False),
            ("No depende de ningun factor en particular.", False),
        ],
    ),
    4: (
        "Segun el modulo, que beneficio trae la organizacion digital?",
        [
            ("Reduce el tiempo que se pierde buscando informacion.", True),
            ("Aumenta el desorden de archivos y notas.", False),
            ("No tiene ningun beneficio real.", False),
            ("Solo sirve para guardar fotos.", False),
        ],
    ),
    5: (
        "Segun el modulo, que es una funcion en programacion?",
        [
            ("Un bloque de instrucciones que se puede reutilizar.", True),
            ("Un tipo de error del programa.", False),
            ("Un dato que nunca cambia.", False),
            ("El nombre de una pagina web.", False),
        ],
    ),
    6: (
        "Segun el modulo, para que se usa la inteligencia artificial en marketing?",
        [
            ("Para generar ideas de contenido, textos publicitarios y campanas.", True),
            ("Unicamente para imprimir folletos.", False),
            ("Para reemplazar por completo a los clientes.", False),
            ("No tiene ningun uso en marketing.", False),
        ],
    ),
    7: (
        "Segun el modulo, que explica el modelo de negocio?",
        [
            ("De que forma concreta la empresa va a generar ingresos.", True),
            ("El logo de la empresa.", False),
            ("La cantidad de horas trabajadas por semana.", False),
            ("El nombre del emprendedor.", False),
        ],
    ),
    8: (
        "Segun el modulo, como se construyen la confianza y la autoridad?",
        [
            ("Con consistencia y resultados reales a lo largo del tiempo.", True),
            ("Con publicidad agresiva unicamente.", False),
            ("De un dia para el otro sin ningun esfuerzo.", False),
            ("Subiendo los precios de forma constante.", False),
        ],
    ),
    9: (
        "Segun el modulo, que permite la automatizacion de WhatsApp y email?",
        [
            ("Enviar mensajes o respuestas automaticas segun las acciones del cliente.", True),
            ("Eliminar la necesidad de tener clientes.", False),
            ("Aumentar el precio de los productos.", False),
            ("Reemplazar el dashboard del negocio.", False),
        ],
    ),
    10: (
        "Segun el modulo, que va a integrar el juego final que se sumara en una etapa posterior?",
        [
            ("Finanzas, tecnologia, emprendimiento y toma de decisiones.", True),
            ("Unicamente contenido de marketing.", False),
            ("Solo ejercicios de programacion.", False),
            ("Nada relacionado con el curso.", False),
        ],
    ),
}


def agregar_cuarta_pregunta(apps, schema_editor):
    Modulo = apps.get_model("curso_acelerado", "Modulo")
    Quiz = apps.get_model("curso_acelerado", "Quiz")
    Pregunta = apps.get_model("curso_acelerado", "Pregunta")
    OpcionRespuesta = apps.get_model("curso_acelerado", "OpcionRespuesta")

    for modulo in Modulo.objects.filter(curso__slug="finanzas-tecnologia-emprendimiento-30-dias"):
        datos = CUARTA_PREGUNTA.get(modulo.numero)
        quiz = Quiz.objects.filter(modulo=modulo).first()
        if not datos or not quiz:
            continue
        if Pregunta.objects.filter(quiz=quiz, orden=4).exists():
            continue
        texto, opciones = datos
        pregunta = Pregunta.objects.create(
            quiz=quiz,
            texto=texto,
            explicacion="Respuesta basada en el contenido teorico del modulo.",
            orden=4,
        )
        for op_orden, (texto_opcion, es_correcta) in enumerate(opciones, start=1):
            OpcionRespuesta.objects.create(
                pregunta=pregunta,
                texto=texto_opcion,
                es_correcta=es_correcta,
                orden=op_orden,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("curso_acelerado", "0005_diagnostico_previo"),
    ]

    operations = [
        migrations.RunPython(agregar_cuarta_pregunta, migrations.RunPython.noop),
    ]
