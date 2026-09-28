from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "calculadora" / "templates" / "calculadora" / "Práctica de Importación - LifecycleArgentina WPC.html"
OUTPUT = ROOT / "static" / "docs" / "importacion-placas-wpc-lifecycleargentina.pptx"

NAVY = RGBColor(10, 35, 66)
GOLD = RGBColor(200, 150, 12)
LIGHT_GOLD = RGBColor(232, 184, 75)
WHITE = RGBColor(255, 255, 255)
INK = RGBColor(28, 43, 58)
MUTED = RGBColor(90, 100, 114)
PALE = RGBColor(245, 246, 248)


def add_text(slide, text, left, top, width, height, size, color, bold=False, font="Aptos", align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    paragraph = frame.paragraphs[0]
    paragraph.text = text
    paragraph.alignment = align
    paragraph.font.name = font
    paragraph.font.size = Pt(size)
    paragraph.font.bold = bold
    paragraph.font.color.rgb = color
    return box


def decorate(slide, number, total):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE
    top = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(0.18))
    top.fill.solid()
    top.fill.fore_color.rgb = GOLD
    top.line.fill.background()
    add_text(slide, "LIFECYCLEARGENTINA", 0.65, 0.25, 3.4, 0.35, 9, NAVY, True)
    add_text(slide, f"{number:02d} / {total:02d}", 11.85, 0.25, 0.8, 0.35, 8, MUTED, True, align=PP_ALIGN.RIGHT)
    line = slide.shapes.add_shape(1, Inches(0.65), Inches(7.08), Inches(12.0), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(226, 230, 234)
    line.line.fill.background()
    add_text(slide, "Práctica de Importación · Comercio Exterior · 2025", 0.65, 7.12, 5.5, 0.22, 7, MUTED)


SLIDES = [
    ("Resumen ejecutivo", [
        "Caso aplicado: importación marítima de 4.000 perfiles WPC desde China hacia Argentina.",
        "Objetivo: diversificar proveedores, ampliar especificaciones y reducir intermediación.",
        "Condición comercial propuesta: FOB Ningbo, un contenedor 40'HC y pago T/T 30% + 70%.",
        "Desembolso inicial estimado: USD 49.633,94; ingresos proyectados: USD 71.450,00.",
        "La viabilidad depende de validar NCM, intervenciones, costos logísticos y recupero fiscal.",
    ]),
    ("Empresa y problema", [
        "LifecycleArgentina comercializa e instala soluciones WPC para proyectos residenciales y comerciales.",
        "La dependencia de proveedores locales limita variedad, disponibilidad y capacidad de negociación.",
        "La importación directa se plantea como decisión de abastecimiento, no solo como reducción de precio.",
        "El proyecto integra producto, normativa, logística, finanzas y gestión de riesgos.",
    ]),
    ("Producto y propuesta de valor", [
        "2.500 unidades de decking hueco 140 × 25 × 5.800 mm, color teak.",
        "1.500 unidades de wall cladding 150 × 22 × 2.900 mm, color coffee brown.",
        "Matriz predominante de polietileno, fibras de madera y aditivos, sujeta a ficha técnica definitiva.",
        "Atributos comerciales: durabilidad, bajo mantenimiento, resistencia a humedad y variedad estética.",
    ]),
    ("Mercado: escenario académico", [
        "Demanda objetivo: vivienda, hotelería, gastronomía, paisajismo y espacios públicos.",
        "Las cifras de tamaño y crecimiento se usan como hipótesis de trabajo, no como estadísticas oficiales.",
        "La decisión real requiere validar importaciones por NCM, país y período con fuentes aduaneras.",
        "La ventaja esperada proviene de reducir intermediarios y ampliar la oferta de producto.",
    ]),
    ("Proveedor y abastecimiento", [
        "Origen propuesto: fabricante de Guangdong, con embarque por el puerto de Ningbo.",
        "Selección basada en ficha técnica, muestras, capacidad, certificaciones y referencias exportadoras.",
        "El Trader coordina cotización, comunicación, inspección y control en origen.",
        "La aprobación final exige muestra física e inspección previa al embarque.",
    ]),
    ("Clasificación arancelaria", [
        "NCM propuesta: 3916.20.90, demás perfiles de polímeros de etileno.",
        "Fundamento preliminar: texto de partida y subpartida, sección constante y matriz de PE; RGI 1 y 6.",
        "La composición, el proceso productivo y la función del artículo pueden modificar la clasificación.",
        "El despachante debe validar NCM, sufijos e intervenciones en SIM/Malvina antes de oficializar.",
    ]),
    ("Marco normativo", [
        "La RGC 5651/2025 dejó sin efecto el SEDI desde el 26 de febrero de 2025.",
        "La eliminación del SEDI no excluye controles o intervenciones específicos del producto.",
        "La declaración de valor OM 1993/1-A se integra cuando corresponde según las opciones del SIM.",
        "Los reglamentos técnicos alcanzados se controlan al uso o comercialización, según la norma aplicable.",
    ]),
    ("Condiciones comerciales", [
        "FOB Ningbo: el vendedor entrega a bordo; el comprador contrata flete y seguro internacional.",
        "Pago T/T: 30% de anticipo y 70% contra documentos de embarque.",
        "Operación en USD canalizada por entidad autorizada, bajo normativa BCRA vigente al pago.",
        "Seguro All Risk y control de calidad reducen el riesgo de daño o falta de conformidad.",
    ]),
    ("Flujo operativo", [
        "1. Validación técnica y aduanera.  2. Proforma, negociación y anticipo.",
        "3. Producción e inspección.  4. Embalaje, booking y embarque FOB.",
        "5. Pago del saldo y recepción documental.  6. Tránsito marítimo.",
        "7. Arribo, DIM, tributos y liberación.  8. Retiro y distribución.",
        "Plazo total estimado del caso: aproximadamente veinte semanas.",
    ]),
    ("Documentación crítica", [
        "Comercial: Proforma Invoice, Commercial Invoice y Packing List.",
        "Transporte: Bill of Lading, aviso de arribo, MANI SIM y Delivery Order.",
        "Aduanera: DIM, declaración de valor cuando corresponda y certificados/intervenciones aplicables.",
        "Riesgo documental: inconsistencias entre descripción, cantidades, peso, origen y condición de venta.",
    ]),
    ("Costos y tratamiento fiscal", [
        "CIF Buenos Aires: USD 28.657,00.",
        "DII y tasa de estadística: USD 4.871,69 de costo no recuperable estimado.",
        "Gastos adicionales: USD 3.532,00. Costo económico estimado: USD 37.060,69.",
        "IVA y percepciones: USD 12.573,25 como créditos/pagos a cuenta potencialmente recuperables.",
        "Desembolso inicial total: USD 49.633,94.",
    ]),
    ("Rentabilidad y sensibilidad", [
        "Ventas proyectadas: USD 71.450,00; excedente sobre caja inicial: USD 21.816,06.",
        "Retorno financiero sobre desembolso inicial: 43,95% antes de gastos comerciales e impuestos finales.",
        "Desembolso unitario prorrateado: USD 13,45 deck y USD 10,68 cladding.",
        "Variables críticas: tipo de cambio, flete, demoras, precio de venta y plazo de recupero fiscal.",
    ]),
    ("Riesgos y mitigación", [
        "Clasificación: validar muestra, ficha técnica y consulta SIM antes del embarque.",
        "Proveedor: auditoría, muestra aprobada, inspección y tolerancias en la orden de compra.",
        "Logística: seguro, días libres, documentación anticipada y provisión por demurrage.",
        "Finanzas: escenario base, pesimista y de estrés para tipo de cambio, flete y precio de venta.",
        "Cumplimiento: revisión aduanera, fiscal y cambiaria en la fecha efectiva de la operación.",
    ]),
    ("Conclusión", [
        "La operación es comercialmente atractiva bajo los supuestos del caso, pero no está libre de riesgos.",
        "La ventaja no depende solo del precio FOB: importan la clasificación, el costo total y la ejecución.",
        "La separación entre costo económico, impuestos recuperables y caja mejora la decisión financiera.",
        "Metodología: estudio de caso con experiencia operativa, fuentes oficiales y datos parcialmente simulados.",
        "Próximo paso: validación profesional de NCM, intervenciones y cotizaciones antes de comprometer fondos.",
    ]),
]


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    cover = prs.slides.add_slide(blank)
    cover.background.fill.solid()
    cover.background.fill.fore_color.rgb = NAVY
    band = cover.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(0.72))
    band.fill.solid()
    band.fill.fore_color.rgb = GOLD
    band.line.fill.background()
    add_text(cover, "LIFECYCLEARGENTINA", 0.75, 0.12, 5.0, 0.46, 15, NAVY, True)
    add_text(cover, "PRÁCTICA PROFESIONALIZANTE · COMERCIO INTERNACIONAL", 0.8, 1.35, 8.9, 0.45, 11, LIGHT_GOLD, True)
    add_text(cover, "Importación de\nPlacas WPC", 0.75, 1.9, 8.5, 2.0, 34, WHITE, True, "Aptos Display")
    add_text(cover, "Desde China hacia Argentina", 0.8, 4.05, 7.0, 0.55, 19, LIGHT_GOLD)
    add_text(cover, "FOB NINGBO   ·   NCM 3916.20.90   ·   1 × 40' FCL", 0.8, 5.05, 8.4, 0.5, 12, WHITE, True)
    add_text(cover, "Presentación ejecutiva · 2025", 0.8, 6.65, 4.5, 0.3, 9, RGBColor(180, 190, 202))

    total = len(SLIDES) + 1
    for number, (title, points) in enumerate(SLIDES, start=2):
        slide = prs.slides.add_slide(blank)
        decorate(slide, number, total)
        add_text(slide, title, 0.72, 0.72, 11.8, 0.7, 25, NAVY, True, "Aptos Display")
        accent = slide.shapes.add_shape(1, Inches(0.72), Inches(1.5), Inches(0.9), Inches(0.055))
        accent.fill.solid()
        accent.fill.fore_color.rgb = GOLD
        accent.line.fill.background()

        box = slide.shapes.add_shape(5, Inches(0.72), Inches(1.82), Inches(11.9), Inches(4.92))
        box.fill.solid()
        box.fill.fore_color.rgb = PALE
        box.line.color.rgb = RGBColor(226, 230, 234)
        frame = box.text_frame
        frame.clear()
        frame.margin_left = Inches(0.42)
        frame.margin_right = Inches(0.38)
        frame.margin_top = Inches(0.22)
        frame.margin_bottom = Inches(0.18)
        frame.word_wrap = True
        for idx, point in enumerate(points):
            paragraph = frame.paragraphs[0] if idx == 0 else frame.add_paragraph()
            paragraph.text = point
            paragraph.level = 0
            paragraph.font.name = "Aptos"
            paragraph.font.size = Pt(15)
            paragraph.font.color.rgb = INK
            paragraph.space_after = Pt(9)
            paragraph.text = f"•  {point}"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUTPUT)
    print(f"Created {OUTPUT} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    build()
