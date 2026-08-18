from django.db import migrations, models
import django.db.models.deletion


DIAGNOSTICO = {
    1: [
        (
            "Que es el ahorro?",
            [
                ("Guardar parte del dinero que no gastas.", True),
                ("Gastar todo lo que ganas.", False),
                ("Pedir dinero prestado.", False),
                ("Invertir sin ningun plan.", False),
            ],
        ),
        (
            "Si gastas mas de lo que ganas, que pasa con tus finanzas?",
            [
                ("Se ordenan solas.", False),
                ("Entras en deuda o te quedas sin ahorro.", True),
                ("Mejoran automaticamente.", False),
                ("No pasa nada.", False),
            ],
        ),
        (
            "Que es mas facil de controlar: lo que ganas o lo que gastas?",
            [
                ("Lo que gastas, porque depende de tus decisiones.", True),
                ("Lo que ganas siempre.", False),
                ("Ninguno de los dos se puede controlar.", False),
                ("Los bancos deciden por vos.", False),
            ],
        ),
    ],
    2: [
        (
            "Que es un presupuesto?",
            [
                ("Un plan para saber en que vas a gastar tu dinero.", True),
                ("Un tipo de impuesto.", False),
                ("Un prestamo bancario.", False),
                ("Una tarjeta de credito.", False),
            ],
        ),
        (
            "Para que sirve un fondo de emergencia?",
            [
                ("Para cubrir gastos imprevistos.", True),
                ("Para gastar en vacaciones.", False),
                ("Para pagar impuestos.", False),
                ("No sirve para nada en particular.", False),
            ],
        ),
        (
            "Que tipo de deuda conviene evitar?",
            [
                ("La que financia lujos que pierden valor.", True),
                ("La que se usa para estudiar.", False),
                ("La que se usa para invertir en un negocio.", False),
                ("Ninguna deuda es mala.", False),
            ],
        ),
    ],
    3: [
        (
            "Que es invertir?",
            [
                ("Poner tu dinero a trabajar para generar mas dinero.", True),
                ("Gastar todo tu sueldo.", False),
                ("Guardar dinero debajo del colchon.", False),
                ("Pedir un prestamo.", False),
            ],
        ),
        (
            "Que instrumento representa ser dueno de una parte de una empresa?",
            [
                ("Una accion.", True),
                ("Un bono.", False),
                ("Un plazo fijo.", False),
                ("Una factura.", False),
            ],
        ),
        (
            "Si una inversion promete ganancias muy altas sin riesgo, que deberias pensar?",
            [
                ("Que puede ser sospechoso o una estafa.", True),
                ("Que es cien por ciento segura.", False),
                ("Que hay que invertir todo de inmediato.", False),
                ("Que no hace falta informarse.", False),
            ],
        ),
    ],
    4: [
        (
            "Para que sirve una planilla de calculo como Google Sheets?",
            [
                ("Para organizar y calcular datos facilmente.", True),
                ("Solo para escuchar musica.", False),
                ("Para editar videos.", False),
                ("Para enviar mensajes de texto.", False),
            ],
        ),
        (
            "Que es automatizar una tarea?",
            [
                ("Hacer que se ejecute sola, sin repetirla manualmente.", True),
                ("Hacerla mas lenta.", False),
                ("Eliminarla por completo.", False),
                ("Hacerla solo los fines de semana.", False),
            ],
        ),
        (
            "Que tipo de herramienta es una IA generativa?",
            [
                ("Una que puede crear texto, imagenes o codigo.", True),
                ("Un antivirus.", False),
                ("Un tipo de impresora.", False),
                ("Una red social.", False),
            ],
        ),
    ],
    5: [
        (
            "Que es programar, en palabras simples?",
            [
                ("Dar instrucciones a una computadora para que haga algo.", True),
                ("Reparar una computadora.", False),
                ("Disenar un logo.", False),
                ("Enviar correos.", False),
            ],
        ),
        (
            "Cual de estos es un lenguaje de programacion?",
            [
                ("Python", True),
                ("Word", False),
                ("PDF", False),
                ("Excel", False),
            ],
        ),
        (
            "Que necesita una pagina web para verse y funcionar bien?",
            [
                ("Estructura, diseno y comportamiento.", True),
                ("Solo texto sin formato.", False),
                ("Unicamente imagenes.", False),
                ("Nada, se genera sola.", False),
            ],
        ),
    ],
    6: [
        (
            "Que es un prompt?",
            [
                ("La instruccion que le das a una inteligencia artificial.", True),
                ("Un tipo de virus informatico.", False),
                ("Un dispositivo fisico.", False),
                ("Un idioma de programacion.", False),
            ],
        ),
        (
            "La inteligencia artificial puede ayudar a...?",
            [
                ("Analizar datos y generar contenido.", True),
                ("Reemplazar por completo el pensamiento critico.", False),
                ("Funcionar sin ningun dato.", False),
                ("Adivinar el futuro con certeza.", False),
            ],
        ),
        (
            "Que hace mas efectiva a una instruccion para una IA?",
            [
                ("Ser clara y especifica.", True),
                ("Ser lo mas ambigua posible.", False),
                ("No dar ningun detalle.", False),
                ("Repetir la misma palabra muchas veces.", False),
            ],
        ),
    ],
    7: [
        (
            "Que necesita todo negocio para existir?",
            [
                ("Un problema real y un cliente dispuesto a pagar por resolverlo.", True),
                ("Una oficina grande.", False),
                ("Muchos empleados desde el inicio.", False),
                ("Un prestamo bancario.", False),
            ],
        ),
        (
            "Que es un MVP?",
            [
                ("La version minima de un producto para probarlo.", True),
                ("Un premio a la mejor empresa.", False),
                ("Un tipo de sociedad legal.", False),
                ("Un plan de marketing.", False),
            ],
        ),
        (
            "Antes de invertir mucho dinero en una idea, que conviene hacer?",
            [
                ("Validarla con clientes reales.", True),
                ("Gastar todo el presupuesto de una vez.", False),
                ("Copiar exactamente a la competencia.", False),
                ("Esperar a tener certeza absoluta.", False),
            ],
        ),
    ],
    8: [
        (
            "Que es una marca personal?",
            [
                ("Como te perciben los demas por lo que comunicas.", True),
                ("Un logo comprado.", False),
                ("Una cuenta bancaria.", False),
                ("Un tipo de producto.", False),
            ],
        ),
        (
            "Que es un embudo de ventas?",
            [
                ("El camino que recorre un cliente hasta comprar.", True),
                ("Un tipo de descuento.", False),
                ("Un impuesto sobre las ventas.", False),
                ("Una red social.", False),
            ],
        ),
        (
            "Que ayuda mas a vender en el largo plazo?",
            [
                ("Generar confianza con contenido de valor.", True),
                ("Prometer cosas que no se pueden cumplir.", False),
                ("Spamear a los clientes.", False),
                ("Subir el precio sin ninguna justificacion.", False),
            ],
        ),
    ],
    9: [
        (
            "Que es un CRM?",
            [
                ("Un sistema para gestionar la relacion con los clientes.", True),
                ("Un tipo de moneda.", False),
                ("Una red social.", False),
                ("Un metodo de pago.", False),
            ],
        ),
        (
            "Que muestra un dashboard?",
            [
                ("Indicadores clave del negocio de un vistazo.", True),
                ("Solo fotos de productos.", False),
                ("Los correos personales del dueno.", False),
                ("Un catalogo de precios.", False),
            ],
        ),
        (
            "Que tipo de tareas conviene automatizar primero?",
            [
                ("Las repetitivas que se hacen siempre igual.", True),
                ("Las que se hacen una sola vez en la vida.", False),
                ("Ninguna tarea deberia automatizarse.", False),
                ("Las decisiones mas importantes de la empresa.", False),
            ],
        ),
    ],
    10: [
        (
            "Que combina un buen negocio digital?",
            [
                ("Un problema real, tecnologia y buenas decisiones financieras.", True),
                ("Solo una buena idea sin validar.", False),
                ("Unicamente publicidad.", False),
                ("Un local fisico grande.", False),
            ],
        ),
        (
            "Antes de invertir en un proyecto propio, que conviene tener ordenado?",
            [
                ("Tus finanzas personales.", True),
                ("Nada, se puede improvisar todo.", False),
                ("Solo el nombre de la empresa.", False),
                ("El logo y los colores.", False),
            ],
        ),
        (
            "Que representa el rango Legendario en este curso?",
            [
                ("El nivel final, donde se integra todo lo aprendido.", True),
                ("El primer nivel del curso.", False),
                ("Un modulo opcional sin contenido.", False),
                ("Un examen de ingreso.", False),
            ],
        ),
    ],
}


def seed_diagnostico(apps, schema_editor):
    Modulo = apps.get_model("curso_acelerado", "Modulo")
    PreguntaDiagnostico = apps.get_model("curso_acelerado", "PreguntaDiagnostico")
    OpcionDiagnostico = apps.get_model("curso_acelerado", "OpcionDiagnostico")

    for modulo in Modulo.objects.filter(curso__slug="finanzas-tecnologia-emprendimiento-30-dias"):
        preguntas = DIAGNOSTICO.get(modulo.numero)
        if not preguntas:
            continue
        for orden, (texto, opciones) in enumerate(preguntas, start=1):
            pregunta = PreguntaDiagnostico.objects.create(
                modulo=modulo,
                texto=texto,
                orden=orden,
            )
            for op_orden, (texto_opcion, es_correcta) in enumerate(opciones, start=1):
                OpcionDiagnostico.objects.create(
                    pregunta=pregunta,
                    texto=texto_opcion,
                    es_correcta=es_correcta,
                    orden=op_orden,
                )


class Migration(migrations.Migration):
    dependencies = [
        ("curso_acelerado", "0004_gamificacion_niveles"),
    ]

    operations = [
        migrations.CreateModel(
            name="PreguntaDiagnostico",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("texto", models.TextField()),
                ("orden", models.PositiveSmallIntegerField(default=1)),
                (
                    "modulo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="preguntas_diagnostico",
                        to="curso_acelerado.modulo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Pregunta de diagnostico",
                "verbose_name_plural": "Preguntas de diagnostico",
                "ordering": ["orden", "id"],
            },
        ),
        migrations.CreateModel(
            name="OpcionDiagnostico",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("texto", models.CharField(max_length=255)),
                ("es_correcta", models.BooleanField(default=False)),
                ("orden", models.PositiveSmallIntegerField(default=1)),
                (
                    "pregunta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="opciones",
                        to="curso_acelerado.preguntadiagnostico",
                    ),
                ),
            ],
            options={
                "verbose_name": "Opcion de diagnostico",
                "verbose_name_plural": "Opciones de diagnostico",
                "ordering": ["orden", "id"],
            },
        ),
        migrations.RunPython(seed_diagnostico, migrations.RunPython.noop),
    ]
