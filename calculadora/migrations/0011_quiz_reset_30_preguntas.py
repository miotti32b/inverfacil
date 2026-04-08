from django.db import migrations

PREGUNTAS = [
    # 1 - Instrumentos argentinos
    {
        "text": "¿Qué es un CEDEAR?",
        "options": [
            ("Certificado de Depósito Argentino que representa acciones extranjeras", True),
            ("Un bono del gobierno nacional en pesos", False),
            ("Un fondo de inversión en dólares del BCRA", False),
            ("Una letra del Tesoro a corto plazo", False),
        ],
    },
    # 2 - Metodologías
    {
        "text": "¿Qué estrategia consiste en comprar el mismo activo en cuotas periódicas sin importar el precio?",
        "options": [
            ("Dollar Cost Averaging (DCA)", True),
            ("Buy the Dip", False),
            ("Swing Trading", False),
            ("Stop Loss dinámico", False),
        ],
    },
    # 3 - Análisis fundamental
    {
        "text": "¿Qué mide el ratio Precio/Ganancias (P/E) de una acción?",
        "options": [
            ("Cuánto paga el mercado por cada peso de ganancia de la empresa", True),
            ("El porcentaje de dividendos que reparte la empresa", False),
            ("La relación entre deuda y patrimonio neto", False),
            ("El precio comparado con su valor en libros", False),
        ],
    },
    # 4 - ETFs
    {
        "text": "¿Qué es un ETF (Exchange Traded Fund)?",
        "options": [
            ("Un fondo que cotiza en bolsa y replica un índice o canasta de activos", True),
            ("Un contrato de futuros sobre divisas", False),
            ("Un bono corporativo de tasa variable", False),
            ("Un depósito bancario con tasa garantizada", False),
        ],
    },
    # 5 - Riesgo soberano
    {
        "text": "¿Cuál es el principal riesgo de un bono soberano de un país emergente?",
        "options": [
            ("Riesgo de default o reestructuración de la deuda", True),
            ("Que el precio suba demasiado rápido", False),
            ("Que pague demasiados intereses", False),
            ("Que sea imposible venderlo antes del vencimiento", False),
        ],
    },
    # 6 - Finanzas personales
    {
        "text": "¿Qué representa el 'fondo de emergencia' en finanzas personales?",
        "options": [
            ("Reserva líquida equivalente a 3-6 meses de gastos esenciales", True),
            ("Dinero invertido en activos de alto riesgo para imprevistos", False),
            ("El límite máximo de una tarjeta de crédito", False),
            ("El ahorro destinado a vacaciones anuales", False),
        ],
    },
    # 7 - Interés compuesto
    {
        "text": "¿Qué es el interés compuesto?",
        "options": [
            ("Interés que se calcula sobre el capital más los intereses acumulados", True),
            ("Una tasa fija pactada al inicio del contrato", False),
            ("El interés que cobra el banco por un préstamo hipotecario", False),
            ("La diferencia entre tasa activa y pasiva de un banco", False),
        ],
    },
    # 8 - Inflación
    {
        "text": "¿Qué indica una inflación alta y sostenida sobre el dinero en efectivo?",
        "options": [
            ("Lo erosiona: el mismo dinero compra menos bienes con el tiempo", True),
            ("Lo fortalece porque sube la tasa de interés nominal", False),
            ("No tiene efecto si el dinero está en caja de ahorro", False),
            ("Lo protege porque el Estado garantiza su valor", False),
        ],
    },
    # 9 - Diversificación
    {
        "text": "¿Qué es la diversificación en una cartera de inversión?",
        "options": [
            ("Distribuir el capital en distintos activos para reducir el riesgo total", True),
            ("Concentrar todo en el activo con mayor rentabilidad histórica", False),
            ("Invertir solo en activos del mismo sector para maximizar ganancias", False),
            ("Cambiar de activos cada semana según las noticias del mercado", False),
        ],
    },
    # 10 - ONs
    {
        "text": "¿Qué son las Obligaciones Negociables (ONs) en Argentina?",
        "options": [
            ("Bonos corporativos emitidos por empresas privadas que cotizan en bolsa", True),
            ("Acciones preferidas de empresas del Estado", False),
            ("Letras del Banco Central en pesos ajustables", False),
            ("Contratos de futuros sobre commodities agrícolas", False),
        ],
    },
    # 11 - Riesgo y retorno
    {
        "text": "¿Qué relación existe generalmente entre riesgo y retorno en inversiones?",
        "options": [
            ("A mayor riesgo, mayor retorno potencial", True),
            ("A mayor riesgo, menor retorno potencial", False),
            ("El riesgo no tiene relación con el retorno esperado", False),
            ("El retorno es siempre igual independientemente del riesgo", False),
        ],
    },
    # 12 - Dólar MEP
    {
        "text": "¿Qué es el dólar MEP en Argentina?",
        "options": [
            ("El tipo de cambio obtenido comprando y vendiendo bonos en bolsa dentro del país", True),
            ("El tipo de cambio oficial del Banco Central para importaciones", False),
            ("Una cotización especial para turistas extranjeros", False),
            ("El precio del dólar en el mercado informal (blue)", False),
        ],
    },
    # 13 - Acciones y dividendos
    {
        "text": "¿Qué son los dividendos?",
        "options": [
            ("Parte de las ganancias de una empresa distribuida entre sus accionistas", True),
            ("El interés que paga un bono corporativo periódicamente", False),
            ("La diferencia entre el precio de compra y venta de una acción", False),
            ("Una comisión cobrada por el broker por operar acciones", False),
        ],
    },
    # 14 - Psicología del inversor
    {
        "text": "¿Cómo se llama el sesgo cognitivo que lleva a vender activos ganadores demasiado rápido y mantener los perdedores?",
        "options": [
            ("Efecto disposición", True),
            ("Aversión al riesgo", False),
            ("Anclaje de precio", False),
            ("Exceso de confianza", False),
        ],
    },
    # 15 - Bonos
    {
        "text": "¿Qué sucede con el precio de un bono cuando suben las tasas de interés?",
        "options": [
            ("El precio del bono baja", True),
            ("El precio del bono sube", False),
            ("El precio del bono no cambia", False),
            ("El bono se convierte automáticamente en acción", False),
        ],
    },
    # 16 - Índices
    {
        "text": "¿Qué representa el índice S&P 500?",
        "options": [
            ("Las 500 empresas de mayor capitalización bursátil de EE.UU.", True),
            ("Las 500 empresas más rentables del mundo", False),
            ("Un índice de bonos soberanos de 500 países emergentes", False),
            ("El precio promedio de las 500 materias primas más comercializadas", False),
        ],
    },
    # 17 - Merval
    {
        "text": "¿Qué es el índice MERVAL?",
        "options": [
            ("El principal índice bursátil de la Bolsa de Comercio de Buenos Aires", True),
            ("El índice de precios al consumidor que publica el INDEC", False),
            ("El tipo de cambio de referencia del Banco Central", False),
            ("Un índice de bonos soberanos argentinos en dólares", False),
        ],
    },
    # 18 - Plazo fijo UVA
    {
        "text": "¿Qué característica tiene un plazo fijo UVA en Argentina?",
        "options": [
            ("El capital ajusta por inflación (UVA) más una tasa de interés adicional", True),
            ("Paga una tasa fija en dólares garantizada por el BCRA", False),
            ("No tiene plazo mínimo y puede rescatarse en cualquier momento", False),
            ("Solo está disponible para empresas, no para personas físicas", False),
        ],
    },
    # 19 - FCI
    {
        "text": "¿Qué es un FCI Money Market en Argentina?",
        "options": [
            ("Un fondo de inversión de muy alta liquidez que invierte en activos de corto plazo en pesos", True),
            ("Un fondo que invierte exclusivamente en acciones del Merval", False),
            ("Un fondo de pensión administrado por el Estado", False),
            ("Un instrumento de inversión en dólares con plazo mínimo de 1 año", False),
        ],
    },
    # 20 - Apalancamiento
    {
        "text": "¿Qué significa operar con apalancamiento en los mercados financieros?",
        "options": [
            ("Operar con más capital del que se posee, usando deuda o margen del broker", True),
            ("Invertir solo en activos de bajo riesgo para preservar capital", False),
            ("Diversificar la cartera en distintas clases de activos", False),
            ("Reinvertir automáticamente los dividendos recibidos", False),
        ],
    },
    # 21 - Economía argentina
    {
        "text": "¿Qué mide el riesgo país de Argentina?",
        "options": [
            ("El diferencial de rendimiento de los bonos argentinos respecto a los bonos del Tesoro de EE.UU.", True),
            ("La diferencia entre el dólar blue y el dólar oficial", False),
            ("El índice de inflación mensual publicado por el INDEC", False),
            ("El nivel de reservas del Banco Central en relación al PBI", False),
        ],
    },
    # 22 - Criptomonedas
    {
        "text": "¿Qué es una stablecoin?",
        "options": [
            ("Una criptomoneda diseñada para mantener un valor estable, generalmente anclada al dólar", True),
            ("Una criptomoneda de alta volatilidad usada para especulación a corto plazo", False),
            ("El nombre técnico del Bitcoin en los mercados institucionales", False),
            ("Un token emitido por bancos centrales para reemplazar el efectivo", False),
        ],
    },
    # 23 - Finanzas personales
    {
        "text": "¿Qué describe la regla del 50/30/20 en finanzas personales?",
        "options": [
            ("Destinar 50% a necesidades, 30% a deseos y 20% a ahorro e inversión", True),
            ("Invertir 50% en renta fija, 30% en acciones y 20% en cash", False),
            ("Gastar no más del 50% del sueldo y ahorrar el resto igualmente dividido", False),
            ("Pagar 50% de impuestos, 30% de deudas y guardar 20% en efectivo", False),
        ],
    },
    # 24 - REITs
    {
        "text": "¿Qué son los REITs (Real Estate Investment Trusts)?",
        "options": [
            ("Fondos que invierten en propiedades inmobiliarias y distribuyen rentas a sus accionistas", True),
            ("Contratos de alquiler de propiedades comerciales con garantía del Estado", False),
            ("Bonos emitidos por constructoras para financiar proyectos inmobiliarios", False),
            ("Seguros hipotecarios obligatorios en EE.UU. para créditos de vivienda", False),
        ],
    },
    # 25 - Sesgo cognitivo
    {
        "text": "¿Qué es el 'efecto manada' en los mercados financieros?",
        "options": [
            ("La tendencia de los inversores a seguir las decisiones de la mayoría en lugar de analizar por cuenta propia", True),
            ("La caída simultánea de todos los activos en una crisis sistémica", False),
            ("La estrategia de comprar activos cuando todos los demás venden", False),
            ("El comportamiento de los mercados durante una burbuja especulativa", False),
        ],
    },
    # 26 - Letras del Tesoro
    {
        "text": "¿Qué son las LETES (Letras del Tesoro) en Argentina?",
        "options": [
            ("Instrumentos de deuda de corto plazo emitidos por el Tesoro Nacional", True),
            ("Billetes de alta denominación emitidos por el Banco Central", False),
            ("Letras de cambio usadas en el comercio exterior argentino", False),
            ("Un tipo de bono municipal emitido por provincias argentinas", False),
        ],
    },
    # 27 - Valor tiempo del dinero
    {
        "text": "¿Por qué $1.000 hoy valen más que $1.000 en un año?",
        "options": [
            ("Porque hoy pueden invertirse y generar rendimiento durante ese año", True),
            ("Porque los billetes físicos se deterioran con el tiempo", False),
            ("Porque el gobierno puede cambiar la moneda en cualquier momento", False),
            ("Porque el precio de los bienes siempre baja con el tiempo", False),
        ],
    },
    # 28 - Cartera 60/40
    {
        "text": "¿En qué consiste la estrategia de cartera 60/40?",
        "options": [
            ("60% en acciones para crecimiento y 40% en bonos para estabilidad", True),
            ("60% en activos locales y 40% en activos internacionales", False),
            ("60% en renta fija y 40% en criptomonedas para diversificar", False),
            ("Invertir el 60% del sueldo y gastar el 40% restante", False),
        ],
    },
    # 29 - Buy & Hold
    {
        "text": "¿En qué consiste la estrategia Buy & Hold?",
        "options": [
            ("Comprar activos y mantenerlos durante años sin importar la volatilidad del mercado", True),
            ("Comprar acciones cuando bajan y venderlas al primer rebote", False),
            ("Mantener siempre un 50% del portafolio en efectivo para oportunidades", False),
            ("Comprar solo cuando el mercado está en máximos históricos", False),
        ],
    },
    # 30 - Liquidez
    {
        "text": "¿Qué significa que un activo tiene alta liquidez?",
        "options": [
            ("Que puede convertirse en dinero rápidamente y sin pérdida significativa de valor", True),
            ("Que genera altos rendimientos en el corto plazo", False),
            ("Que está respaldado por el Banco Central del país emisor", False),
            ("Que su precio no varía con las condiciones del mercado", False),
        ],
    },
]


def resetear_y_agregar(apps, schema_editor):
    QuizQuestion = apps.get_model('calculadora', 'QuizQuestion')
    QuizOption = apps.get_model('calculadora', 'QuizOption')
    # Borrar todo
    QuizQuestion.objects.all().delete()
    # Insertar 30 nuevas
    for p in PREGUNTAS:
        q = QuizQuestion.objects.create(text=p["text"])
        for text, is_correct in p["options"]:
            QuizOption.objects.create(question=q, text=text, is_correct=is_correct)


def revertir(apps, schema_editor):
    QuizQuestion = apps.get_model('calculadora', 'QuizQuestion')
    QuizQuestion.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('calculadora', '0010_quiz_preguntas_iniciales'),
    ]

    operations = [
        migrations.RunPython(resetear_y_agregar, revertir),
    ]
