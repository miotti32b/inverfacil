INFOGRAFIAS = {
    1: {
        "tipo": "comparacion",
        "titulo": "Pasivos vs. Activos",
        "izquierda": {
            "titulo": "Pasivos",
            "nota": "te bajan el bolsillo",
            "flecha": "↓",
            "items": [
                ("🏠", "Renta"),
                ("💡", "Luz"),
                ("💧", "Agua"),
                ("⛽", "Gasolina"),
                ("📶", "Internet"),
            ],
        },
        "derecha": {
            "titulo": "Activos",
            "nota": "te suben el bolsillo",
            "flecha": "↑",
            "items": [
                ("💵", "Salario"),
                ("📈", "Utilidades"),
                ("🏪", "Ganancias de negocio"),
            ],
        },
    },
    2: {
        "tipo": "dona",
        "titulo": "La regla 50/30/20",
        "segmentos": [
            {"label": "Necesidades", "valor": 50, "color": "#0ea5e9"},
            {"label": "Gustos", "valor": 30, "color": "#f97316"},
            {"label": "Ahorro y deudas", "valor": 20, "color": "#22c55e"},
        ],
    },
    3: {
        "tipo": "grid",
        "titulo": "El triangulo de toda inversion",
        "items": [
            ("⚖️", "Riesgo"),
            ("💧", "Liquidez"),
            ("📈", "Rentabilidad"),
        ],
    },
    4: {
        "tipo": "grid",
        "titulo": "Tu caja de herramientas digital",
        "items": [
            ("📊", "Google Sheets"),
            ("🗂️", "Organizacion digital"),
            ("🤖", "Automatizaciones"),
            ("✨", "IA generativa"),
        ],
    },
    5: {
        "tipo": "grid",
        "titulo": "Las piezas de una app web",
        "items": [
            ("🧱", "HTML: estructura"),
            ("🎨", "CSS: diseno"),
            ("⚡", "JavaScript: interaccion"),
            ("🐍", "Python: logica"),
        ],
    },
    6: {
        "tipo": "grid",
        "titulo": "La IA aplicada a...",
        "items": [
            ("💬", "Prompts efectivos"),
            ("💼", "Negocios"),
            ("💰", "Finanzas"),
            ("📣", "Marketing"),
        ],
    },
    7: {
        "tipo": "flujo",
        "titulo": "De la idea al negocio",
        "pasos": [
            ("❗", "Problema"),
            ("💡", "Solucion"),
            ("🙋", "Cliente"),
            ("🧪", "MVP"),
        ],
    },
    8: {
        "tipo": "embudo",
        "titulo": "El embudo de ventas",
        "pasos": [
            {"label": "Atraccion", "color": "#22c55e", "ancho": 100},
            {"label": "Interes", "color": "#0ea5e9", "ancho": 78},
            {"label": "Decision", "color": "#f97316", "ancho": 56},
            {"label": "Accion", "color": "#111827", "ancho": 34},
        ],
    },
    9: {
        "tipo": "grid",
        "titulo": "Sistemas para escalar un negocio",
        "items": [
            ("🧾", "CRM"),
            ("🏭", "ERP"),
            ("📊", "Dashboards"),
            ("💬", "WhatsApp / Email automation"),
        ],
    },
    10: {
        "tipo": "grid",
        "titulo": "Los 4 pilares del recorrido",
        "items": [
            ("💰", "Finanzas"),
            ("💻", "Tecnologia"),
            ("🚀", "Emprendimiento"),
            ("🧭", "Decisiones"),
        ],
    },
}


def _preparar_donas():
    for infografia in INFOGRAFIAS.values():
        if infografia.get("tipo") != "dona":
            continue
        acumulado = 0
        partes = []
        for segmento in infografia["segmentos"]:
            inicio = acumulado
            acumulado += segmento["valor"]
            segmento["desde"] = inicio
            segmento["hasta"] = acumulado
            partes.append(f"{segmento['color']} {inicio}% {acumulado}%")
        infografia["gradiente_css"] = "conic-gradient(" + ", ".join(partes) + ")"


_preparar_donas()


def infografia_para_numero(numero):
    return INFOGRAFIAS.get(numero)
