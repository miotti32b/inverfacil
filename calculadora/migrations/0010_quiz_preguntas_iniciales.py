from django.db import migrations


PREGUNTAS = [
    {
        "text": "¿Qué es un CEDEAR?",
        "options": [
            ("Certificado de Depósito Argentino que representa acciones extranjeras", True),
            ("Un bono del gobierno nacional en pesos", False),
            ("Un fondo de inversión en dólares del BCRA", False),
            ("Una letra del Tesoro a corto plazo", False),
        ],
    },
    {
        "text": "¿Qué estrategia de inversión consiste en comprar el mismo activo en cuotas periódicas sin importar el precio?",
        "options": [
            ("Dollar Cost Averaging (DCA)", True),
            ("Buy the Dip", False),
            ("Swing Trading", False),
            ("Stop Loss dinámico", False),
        ],
    },
    {
        "text": "¿Qué mide el ratio Precio/Ganancias (P/E) de una acción?",
        "options": [
            ("Cuánto paga el mercado por cada peso de ganancia de la empresa", True),
            ("El porcentaje de dividendos que reparte la empresa", False),
            ("La relación entre deuda y patrimonio neto", False),
            ("El precio de la acción comparado con su valor en libros", False),
        ],
    },
    
    {
        "text": "¿Qué es un ETF (Exchange Traded Fund)?",
        "options": [
            ("Un fondo que cotiza en bolsa y replica un índice o canasta de activos", True),
            ("Un contrato de futuros sobre divisas", False),
            ("Un bono corporativo de tasa variable", False),
            ("Un depósito bancario con tasa garantizada", False),
        ],
    },
    {
        "text": "En finanzas personales, ¿qué representa el 'fondo de emergencia'?",
        "options": [
            ("Reserva líquida equivalente a 3-6 meses de gastos esenciales", True),
            ("Dinero invertido en activos de alto riesgo para emergencias", False),
            ("El límite máximo de una tarjeta de crédito", False),
            ("El ahorro destinado a vacaciones anuales", False),
        ],
    },
    {
        "text": "¿Qué es el 'interés compuesto'?",
        "options": [
            ("Interés que se calcula sobre el capital inicial más los intereses acumulados", True),
            ("Una tasa de interés fija pactada al inicio del contrato", False),
            ("El interés que cobra el banco por un préstamo hipotecario", False),
            ("La diferencia entre la tasa activa y pasiva de un banco", False),
        ],
    },
    {
        "text": "¿Qué indica una inflación alta y sostenida sobre el poder del dinero en efectivo?",
        "options": [
            ("Lo erosiona: el mismo dinero compra menos bienes con el tiempo", True),
            ("Lo fortalece porque sube la tasa de interés nominal", False),
            ("No tiene efecto si el dinero está en una caja de ahorro", False),
            ("Lo protege porque el Estado garantiza el valor", False),
        ],
    },
    {
        "text": "¿Qué es la diversificación en una cartera de inversión?",
        "options": [
            ("Distribuir el capital en distintos activos para reducir el riesgo total", True),
            ("Concentrar toda la inversión en el activo con mayor rentabilidad histórica", False),
            ("Invertir solo en activos del mismo sector para maximizar ganancias", False),
            ("Cambiar de activos cada semana según las noticias del mercado", False),
        ],
    },
    {
        "text": "¿Qué son las Obligaciones Negociables (ONs) en Argentina?",
        "options": [
            ("Bonos corporativos emitidos por empresas privadas que cotizan en bolsa", True),
            ("Acciones preferidas de empresas del Estado", False),
            ("Letras del Banco Central en pesos ajustables", False),
            ("Contratos de futuros sobre commodities agrícolas", False),
        ],
    },
]


def agregar_preguntas(apps, schema_editor):
    QuizQuestion = apps.get_model('calculadora', 'QuizQuestion')
    QuizOption = apps.get_model('calculadora', 'QuizOption')

    for pregunta in PREGUNTAS:
        q = QuizQuestion.objects.create(text=pregunta["text"])
        for text, is_correct in pregunta["options"]:
            QuizOption.objects.create(question=q, text=text, is_correct=is_correct)


def eliminar_preguntas(apps, schema_editor):
    QuizQuestion = apps.get_model('calculadora', 'QuizQuestion')
    textos = [p["text"] for p in PREGUNTAS]
    QuizQuestion.objects.filter(text__in=textos).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('calculadora', '0009_solicitudasesoria'),
    ]

    operations = [
        migrations.RunPython(agregar_preguntas, eliminar_preguntas),
    ]
