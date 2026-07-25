from django.db import migrations, models


PUNTOS_CLAVE = {
    1: [
        "Ingreso, gasto, ahorro, deuda e inversion son los 5 movimientos basicos del dinero.",
        "Libertad financiera = tus ingresos pasivos cubren tus gastos.",
        "La carrera de la rata es gastar mas a medida que ganas mas, sin avanzar.",
        "Registrar tus movimientos es el primer habito de una mente financiera ordenada.",
    ],
    2: [
        "Regla 50/30/20: necesidades, gustos, y ahorro mas pago de deudas.",
        "Fondo de emergencia: entre 3 y 6 meses de gastos guardados aparte.",
        "Controlar gastos empieza por registrarlos todos, sin excepcion.",
        "Deuda buena genera valor futuro; deuda mala financia consumo que pierde valor.",
    ],
    3: [
        "Accion = parte de una empresa. Bono = prestamo a un emisor. FCI = fondo gestionado por profesionales.",
        "Riesgo, liquidez y rentabilidad son las tres variables clave de toda inversion.",
        "El interes compuesto hace que el interes generado tambien genere interes.",
        "Tu perfil de inversor define cuanto riesgo podes asumir y en que plazo.",
    ],
    4: [
        "Google Sheets ordena finanzas y datos sin necesidad de programar.",
        "Automatizar tareas repetitivas libera tiempo para lo importante.",
        "La IA generativa crea texto, imagenes o codigo a partir de instrucciones simples.",
        "Organizar tu informacion digital ahorra horas de busqueda cada semana.",
    ],
    5: [
        "Variable, condicional, funcion y dato son los ladrillos basicos de programar.",
        "HTML define estructura, CSS define diseno, JavaScript define interactividad.",
        "Python se usa mucho para logica de backend, datos y automatizacion.",
        "Una app web combina frontend (interfaz) y backend (logica que procesa datos).",
    ],
    6: [
        "Un prompt efectivo es claro, especifico y da contexto y ejemplo.",
        "La IA procesa datos y genera respuestas simulando razonamiento humano.",
        "Se usa en negocios, finanzas y marketing para ahorrar tiempo y mejorar decisiones.",
        "Automatizar con IA reduce tareas repetitivas sin intervencion constante.",
    ],
    7: [
        "Todo negocio parte de un problema real, una solucion y un cliente que paga.",
        "La propuesta de valor explica por que un cliente te elige a vos y no a otro.",
        "El MVP prueba la idea con clientes reales antes de invertir en grande.",
        "Validar rapido evita perder tiempo y plata en algo que nadie quiere comprar.",
    ],
    8: [
        "Tu marca personal es lo que comunicas de forma consistente en el tiempo.",
        "El contenido educativo construye audiencia y confianza antes de vender.",
        "El embudo de ventas va de atraccion a interes, decision y accion.",
        "Una oferta irresistible combina beneficio claro, garantia y urgencia real.",
    ],
    9: [
        "Los procesos repetitivos son los primeros candidatos a automatizar.",
        "El CRM ordena la relacion con clientes; el ERP integra toda la empresa.",
        "Los dashboards muestran el estado del negocio de un vistazo, con datos reales.",
        "Automatizar WhatsApp y email ahorra tiempo operativo todos los dias.",
    ],
    10: [
        "Detectar oportunidades es cruzar finanzas, tecnologia y emprendimiento.",
        "Todo negocio digital nace de un problema real validado con un MVP.",
        "Antes de invertir, aplica presupuesto, fondo de emergencia e interes compuesto.",
        "Este es tu ultimo nivel: alcanzaste el rango Legendario del curso.",
    ],
}


def seed_puntos_clave(apps, schema_editor):
    Modulo = apps.get_model("curso_acelerado", "Modulo")
    for modulo in Modulo.objects.filter(curso__slug="finanzas-tecnologia-emprendimiento-30-dias"):
        puntos = PUNTOS_CLAVE.get(modulo.numero)
        if puntos:
            modulo.puntos_clave = "\n".join(puntos)
            modulo.save(update_fields=["puntos_clave"])


class Migration(migrations.Migration):
    dependencies = [
        ("curso_acelerado", "0003_contenido_didactico"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="modulo",
            name="youtube_url",
        ),
        migrations.AddField(
            model_name="modulo",
            name="puntos_clave",
            field=models.TextField(
                blank=True,
                help_text="Un punto clave por linea. Se muestra como lista de repaso rapido.",
            ),
        ),
        migrations.RunPython(seed_puntos_clave, migrations.RunPython.noop),
    ]
