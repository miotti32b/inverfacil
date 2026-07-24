# calculadora/forms.py
from django import forms
from .models import CarreraRata

class CarreraRataForm(forms.ModelForm):
    class Meta:
        model = CarreraRata
        fields = ['patrimonio_neto', 'ingreso_mensual', 'gasto_mensual', 'fuentes_ingreso', 'horas_trabajadas']
        widgets = {
            'patrimonio_neto': forms.TextInput(attrs={
                'placeholder': 'Suma tus vehiculos, propiedades, stock, todo lo que tengas..',
                'class': 'form-control'
            }),
            'ingreso_mensual': forms.TextInput(attrs={
                'placeholder': 'Cuánto ganas al mes',
                'class': 'form-control'
            }),
            'gasto_mensual': forms.TextInput(attrs={
                'placeholder': 'Cuánto gastas al mes',
                'class': 'form-control'
            }),
            'fuentes_ingreso': forms.NumberInput(attrs={
                'placeholder': 'Número de fuentes de ingreso',
                'class': 'form-control'
            }),
            'horas_trabajadas': forms.NumberInput(attrs={
                'placeholder': 'Cuántas horas trabajas al día',
                'class': 'form-control'
            }),
        }


from .models import ClientePerfil
from decimal import Decimal, InvalidOperation


class ClientePerfilForm(forms.ModelForm):
    class Meta:
        model = ClientePerfil
        exclude = ["diagnosticos_realizados", "quiz_score_total", "total_referred", "referral_earnings"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        opcionales = [
            "diagnosticos_realizados", "quiz_score_total",
            "total_referred", "referral_earnings",
            "conocimiento_seguridad"
        ]
        for campo in opcionales:
            if campo in self.fields:
                self.fields[campo].required = False
    def clean(self):
        cleaned_data = super().clean()

        # Convertir campos numéricos vacíos a 0
        for field_name, value in cleaned_data.items():
            if value in (None, ""):
                field = self.fields.get(field_name)
                if isinstance(field, (forms.DecimalField, forms.IntegerField)):
                    cleaned_data[field_name] = 0

        # Valor por defecto si no respondió reacción ante pérdida
        if not cleaned_data.get("reaccion_perdida"):
            cleaned_data["reaccion_perdida"] = "nose"

        return cleaned_data
    

    # === BLOQUE 1: Datos básicos ===
    edad = forms.IntegerField(
        min_value=18, max_value=99,
        widget=forms.NumberInput(attrs={
            "class": "input-short",
            "placeholder": "Edad"
        })
    )

    hijos_a_cargo = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "input-short",
            "placeholder": "Personas a cargo"
        })
    )

    # === BLOQUE 2: Situación financiera ===
    ingreso_trabajo = forms.DecimalField(required=False, initial=0)
    ingreso_negocio = forms.DecimalField(required=False, initial=0)
    ingreso_rentas = forms.DecimalField(required=False, initial=0)
    ingreso_inversiones = forms.DecimalField(required=False, initial=0)
    ingreso_otros = forms.DecimalField(required=False, initial=0)

    gasto_necesarios = forms.DecimalField(required=False, initial=0)
    gasto_innecesarios = forms.DecimalField(required=False, initial=0)
    gasto_financieros = forms.DecimalField(required=False, initial=0)
    gasto_inversiones = forms.DecimalField(required=False, initial=0)

    patrimonio_vivienda = forms.DecimalField(required=False, initial=0)
    patrimonio_vehiculos = forms.DecimalField(required=False, initial=0)
    patrimonio_ahorros_local = forms.DecimalField(required=False, initial=0)
    patrimonio_ahorros_usd = forms.DecimalField(required=False, initial=0)
    patrimonio_inversiones = forms.DecimalField(required=False, initial=0)
    patrimonio_negocio = forms.DecimalField(required=False, initial=0)
    patrimonio_otros = forms.DecimalField(required=False, initial=0)

    deuda_tarjeta = forms.DecimalField(required=False, initial=0)
    deuda_auto = forms.DecimalField(required=False, initial=0)
    deuda_financiera = forms.DecimalField(required=False, initial=0)

    # === BLOQUE 3: Objetivos ===
    objetivos = forms.MultipleChoiceField(
        choices=[
            ("🏠 Comprar vivienda propia", "🏠 Comprar vivienda propia"),
            ("🚗 Adquirir vehículo", "🚗 Adquirir vehículo"),
            ("💸 Lograr independencia financiera", "💸 Lograr independencia financiera"),
            ("⏳ Alcanzar jubilación anticipada", "⏳ Alcanzar jubilación anticipada"),
            ("🌍 Viajar y disfrutar experiencias", "🌍 Viajar y disfrutar experiencias"),
            ("🎓 Invertir en educación o formación", "🎓 Invertir en educación o formación"),
            ("🚀 Desarrollar o expandir mi negocio", "🚀 Desarrollar o expandir mi negocio"),
            ("📈 Aumentar mis ahorros e inversiones", "📈 Aumentar mis ahorros e inversiones"),
            ("🧘‍♂️ Mejorar mi calidad y estabilidad de vida", "🧘‍♂️ Mejorar mi calidad y estabilidad de vida")
        ],
        widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona hasta 3"
    )
    REACCION_PERDIDA_CHOICES = [
    ("vender_todo", "🚨 Vendés todo para evitar más pérdidas"),
    ("vender_parte", "😬 Vendés una parte por precaución"),
    ("mantener", "😌 Mantenés la posición confiando en tu análisis"),
    ("comprar_mas", "🧠 Comprás más aprovechando el precio bajo"),
    ("esperar", "🕊️ No hacés nada, esperás a que se recupere"),
    ("analizar", "🧮 Analizás datos y buscás asesoramiento"),
    ("aportar_mas", "📉 Aumentás aportes para compensar la baja"),
    ("consultar", "💬 Consultás con otros antes de decidir"),
    ("ignorar", "🤷‍♂️ Ignorás el tema hasta que suba"),
]


    reaccion_perdida = forms.ChoiceField(
    choices=REACCION_PERDIDA_CHOICES,
    widget=forms.RadioSelect,
    required=True,
    )



    # === BLOQUE 4: Valores y decisiones ===
    importancia_dinero = forms.MultipleChoiceField(
        choices=[
            ("🛡️ Seguridad y tranquilidad", "🛡️ Seguridad y tranquilidad"),
            ("🕊️ Libertad y autonomía", "🕊️ Libertad y autonomía"),
            ("🎯 Lograr metas y crecimiento personal", "🎯 Lograr metas y crecimiento personal"),
            ("❤️ Disfrutar la vida y experiencias", "❤️ Disfrutar la vida y experiencias"),
            ("🌟 Reconocimiento o status", "🌟 Reconocimiento o status"),
            ("🤝 Ayudar a otros y generar impacto", "🤝 Ayudar a otros y generar impacto"),
            ("🏗️ Crear oportunidades o proyectos", "🏗️ Crear oportunidades o proyectos"),
            ("📚 Aprender y superarme", "📚 Aprender y superarme"),
            ("⚖️ Mantener equilibrio y estabilidad", "⚖️ Mantener equilibrio y estabilidad")
        ],
        widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona hasta 3"
    )

    uso_millon = forms.MultipleChoiceField(
        choices=[
            ("🌍 Viajar o vivir nuevas experiencias", "🌍 Viajar o vivir nuevas experiencias"),
            ("🏦 Guardar para emergencias o estabilidad", "🏦 Guardar para emergencias o estabilidad"),
            ("🏢 Invertir en un negocio o inmueble", "🏢 Invertir en un negocio o inmueble"),
            ("📊 Diversificar en distintos activos financieros", "📊 Diversificar en distintos activos financieros"),
            ("🎓 Invertir en educación o desarrollo personal", "🎓 Invertir en educación o desarrollo personal"),
            ("💞 Compartir o donar parte del dinero", "💞 Compartir o donar parte del dinero"),
            ("🧱 Construir o remodelar mi vivienda", "🧱 Construir o remodelar mi vivienda"),
            ("🚀 Financiar proyectos propios o familiares", "🚀 Financiar proyectos propios o familiares"),
            ("📉 Cancelar todas mis deudas", "📉 Cancelar todas mis deudas")
        ],
        widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona hasta 3"
    )

    resultados_emprendimientos = forms.MultipleChoiceField(
        choices=[
            ("❌ No tuve experiencias aún", "❌ No tuve experiencias aún"),
            ("📚 Estoy iniciando mi primer proyecto", "📚 Estoy iniciando mi primer proyecto"),
            ("💸 Fracasé pero aprendí del proceso", "💸 Fracasé pero aprendí del proceso"),
            ("⚙️ Mantengo un negocio rentable", "⚙️ Mantengo un negocio rentable"),
            ("🚀 Logré escalar o vender mi empresa", "🚀 Logré escalar o vender mi empresa"),
            ("🧭 Estoy planificando mi próximo emprendimiento", "🧭 Estoy planificando mi próximo emprendimiento"),
            ("🤝 Participo como socio o inversor", "🤝 Participo como socio o inversor"),
            ("📊 Dirijo o gestiono varios proyectos", "📊 Dirijo o gestiono varios proyectos"),
            ("🏛️ Fundé una empresa consolidada", "🏛️ Fundé una empresa consolidada")
        ],
        widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona hasta 3"
    )

    conocimiento_seguridad = forms.MultipleChoiceField(
        choices=[
            ("💵 Dólares en cuenta bancaria", "💵 Dólares en cuenta bancaria"),
            ("🇺🇸 Bonos del Tesoro de EE.UU.", "🇺🇸 Bonos del Tesoro de EE.UU."),
            ("🌾 Tierras o bienes raíces", "🌾 Tierras o bienes raíces"),
            ("🏭 Negocio propio consolidado", "🏭 Negocio propio consolidado"),
            ("🎓 Educación o conocimiento", "🎓 Educación o conocimiento"),
            ("🕒 Plazo fijo en dólares", "🕒 Plazo fijo en dólares"),
            ("🏦 Fondos comunes conservadores", "🏦 Fondos comunes conservadores"),
            ("💎 Oro u otros metales preciosos", "💎 Oro u otros metales preciosos"),
            ("🪙 Criptoactivos estables (stablecoins)", "🪙 Criptoactivos estables (stablecoins)")
        ],
        widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona hasta 3"
    )

    # === BLOQUE 5: Experiencia y formación ===
    experiencia_emprendimientos = forms.IntegerField(
        min_value=0, max_value=10, initial=0,
        widget=forms.NumberInput(attrs={"type": "range", "step": "1"})
    )

    nivel_formacion = forms.IntegerField(
        min_value=0, max_value=10, initial=5,
        widget=forms.NumberInput(attrs={"type": "range", "step": "1"})
    )


from .models import Company


class CompanyValuationForm(forms.ModelForm):
    EMPLOYEE_CHOICES = [
        (1, "Solo yo"),
        (3, "2 a 3"),
        (8, "4 a 10"),
        (20, "11 a 25"),
        (45, "26 a 60"),
        (90, "61 a 120"),
        (180, "121 a 250"),
        (350, "251 a 500"),
        (750, "Mas de 500"),
    ]
    YEARS_CHOICES = [
        (0, "Estoy empezando"),
        (1, "Menos de 1 anio"),
        (3, "1 a 3 anios"),
        (6, "4 a 7 anios"),
        (10, "8 a 12 anios"),
        (16, "13 a 20 anios"),
        (25, "21 a 30 anios"),
        (40, "31 a 50 anios"),
        (65, "Mas de 50 anios"),
    ]
    GROWTH_CHOICES = [
        (Decimal("-0.10"), "Cayendo fuerte"),
        (Decimal("-0.03"), "Leve baja"),
        (Decimal("0.00"), "Estable"),
        (Decimal("0.05"), "Crecimiento suave"),
        (Decimal("0.10"), "Buen ritmo"),
        (Decimal("0.18"), "Muy buen ritmo"),
        (Decimal("0.28"), "Escalando"),
        (Decimal("0.40"), "Hipercrecimiento"),
        (Decimal("0.60"), "Explosivo"),
    ]
    PERCENT_SCALE = [
        (0, "Nada"),
        (12, "Muy bajo"),
        (25, "Bajo"),
        (38, "Medio bajo"),
        (50, "Medio"),
        (62, "Medio alto"),
        (75, "Alto"),
        (88, "Muy alto"),
        (100, "Maximo"),
    ]
    LEGAL_STRUCTURE_CHOICES = [
        ("monotributo_a", "Monotributo clase A"),
        ("monotributo_b", "Monotributo clase B"),
        ("monotributo_c", "Monotributo clase C"),
        ("monotributo_d", "Monotributo clase D"),
        ("monotributo_e", "Monotributo clase E"),
        ("monotributo_f", "Monotributo clase F"),
        ("monotributo_g", "Monotributo clase G"),
        ("monotributo_h", "Monotributo clase H"),
        ("monotributo_i", "Monotributo clase I"),
        ("monotributo_j", "Monotributo clase J"),
        ("monotributo_k", "Monotributo clase K"),
        ("responsable_inscripto", "Responsable inscripto"),
        ("sociedad_hecho", "Sociedad de hecho"),
        ("sociedad_simple", "Sociedad simple / seccion IV"),
        ("srl", "SRL"),
        ("sas", "SAS"),
        ("sa", "SA"),
        ("sau", "SAU"),
        ("cooperativa", "Cooperativa"),
        ("asociacion_civil", "Asociacion civil"),
        ("fundacion", "Fundacion"),
        ("ute", "UTE"),
        ("fideicomiso", "Fideicomiso"),
        ("grupo_empresario", "Grupo empresario"),
        ("multinacional", "Multinacional"),
    ]
    QUOTE_REASON_FORM_CHOICES = [
        ("inversores", "Inversores"),
        ("curiosidad", "Curiosidad"),
        ("venta", "Venta"),
        ("competencia", "Competencia"),
        ("expansion", "Expansion"),
        ("socios", "Socios"),
        ("ordenar", "Ordenar"),
        ("marca", "Marca"),
        ("sucesion", "Sucesion"),
    ]
    COMPETITIVE_ADVANTAGE_CHOICES = [
        ("marca", "Marca conocida"),
        ("costos", "Costos bajos"),
        ("ubicacion", "Ubicacion clave"),
        ("tecnologia", "Tecnologia propia"),
        ("equipo", "Equipo fuerte"),
        ("comunidad", "Comunidad fiel"),
        ("datos", "Datos propios"),
        ("proveedores", "Red de proveedores"),
        ("velocidad", "Velocidad de ejecucion"),
    ]

    legal_structure = forms.ChoiceField(
        label="Tipo de sociedad juridica",
        choices=LEGAL_STRUCTURE_CHOICES,
        widget=forms.Select(),
    )
    quote_reason = forms.MultipleChoiceField(
        label="Motivo de la cotizacion",
        choices=QUOTE_REASON_FORM_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "card-radio"}),
    )
    competitive_advantage = forms.MultipleChoiceField(
        label="Ventajas principales",
        choices=COMPETITIVE_ADVANTAGE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "card-radio"}),
    )
    employees = forms.IntegerField(
        label="Cantidad de empleados",
        min_value=1,
        widget=forms.NumberInput(attrs={"min": "1", "step": "1", "inputmode": "numeric"}),
    )
    years_active = forms.IntegerField(
        label="Anios activa",
        min_value=0,
        widget=forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
    )
    growth_rate = forms.ChoiceField(
        label="Ritmo de crecimiento",
        choices=GROWTH_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "card-radio"}),
    )
    market_scope_current = forms.ChoiceField(
        label="Alcance actual",
        choices=Company.MARKET_SCOPE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "card-radio"}),
    )
    market_scope_future = forms.ChoiceField(
        label="Alcance objetivo a 12/24 meses",
        choices=Company.MARKET_SCOPE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "card-radio"}),
    )
    digitalization = forms.ChoiceField(
        label="Nivel de digitalizacion",
        choices=PERCENT_SCALE,
        widget=forms.RadioSelect(attrs={"class": "card-radio"}),
    )
    customer_concentration = forms.ChoiceField(
        label="Concentracion de clientes",
        choices=PERCENT_SCALE,
        widget=forms.RadioSelect(attrs={"class": "card-radio"}),
    )

    class Meta:
        model = Company
        fields = [
            "name",
            "market_visibility",
            "legal_structure",
            "sector",
            "quote_reason",
            "revenue",
            "revenue_next_24m",
            "employees",
            "employees_next_24m",
            "years_active",
            "growth_rate",
            "ebitda_margin",
            "gross_margin",
            "debt_level",
            "total_assets",
            "active_customers",
            "active_customers_next_24m",
            "perceived_valuation",
            "perceived_valuation_reason",
            "competitive_advantage",
            "market_scope_current",
            "market_scope_future",
            "digitalization",
            "customer_concentration",
        ]
        labels = {
            "name": "Nombre de la empresa",
            "market_visibility": "Visibilidad inicial",
            "legal_structure": "Tipo de sociedad juridica",
            "sector": "Sector",
            "quote_reason": "Motivo de la cotizacion",
            "revenue": "Facturacion anual en USD",
            "revenue_next_24m": "Facturacion objetivo a 12/24 meses en USD",
            "employees": "Cantidad de empleados actual",
            "employees_next_24m": "Empleados objetivo a 12/24 meses",
            "years_active": "Anios activa",
            "growth_rate": "Crecimiento esperado",
            "ebitda_margin": "% margen neto sobre facturacion",
            "gross_margin": "% ganancia bruta",
            "debt_level": "Deuda total en USD",
            "total_assets": "Activos totales en USD",
            "active_customers": "Clientes activos actuales",
            "active_customers_next_24m": "Clientes objetivo a 12/24 meses",
            "perceived_valuation": "Cuanto crees que vale tu empresa en USD",
            "perceived_valuation_reason": "Por que crees que vale eso",
            "competitive_advantage": "Ventajas principales",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ej: Mi pyme SRL"}),
            "sector": forms.RadioSelect(attrs={"class": "card-radio"}),
            "revenue": forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
            "revenue_next_24m": forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
            "ebitda_margin": forms.NumberInput(attrs={"min": "-100", "max": "100", "step": "1", "inputmode": "numeric"}),
            "gross_margin": forms.NumberInput(attrs={"min": "-100", "max": "100", "step": "1", "inputmode": "numeric"}),
            "debt_level": forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
            "total_assets": forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
            "active_customers": forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
            "active_customers_next_24m": forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
            "employees_next_24m": forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
            "perceived_valuation": forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
            "perceived_valuation_reason": forms.Textarea(attrs={"rows": 3, "placeholder": "Ej: marca, cartera de clientes, activos, ubicacion, traccion o tecnologia propia."}),
        }

    def clean_quote_reason(self):
        values = self.cleaned_data["quote_reason"]
        if len(values) > 2:
            raise forms.ValidationError("Elegi hasta 2 motivos.")
        return ",".join(values)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in (
            "revenue_next_24m",
            "employees_next_24m",
            "active_customers_next_24m",
            "perceived_valuation_reason",
        ):
            self.fields[field_name].required = False

    def clean_competitive_advantage(self):
        values = self.cleaned_data["competitive_advantage"]
        if len(values) > 2:
            raise forms.ValidationError("Elegi hasta 2 ventajas.")
        return ",".join(values)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.quote_reason = self.cleaned_data.get("quote_reason", "")
        instance.competitive_advantage = self.cleaned_data.get("competitive_advantage", "")
        instance.ticker = ""
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def clean_growth_rate(self):
        return Decimal(str(self.cleaned_data["growth_rate"])).quantize(Decimal("0.0001"))

    def clean_ebitda_margin(self):
        return (Decimal(str(self.cleaned_data["ebitda_margin"])) / Decimal("100")).quantize(Decimal("0.0001"))

    def clean_gross_margin(self):
        return (Decimal(str(self.cleaned_data["gross_margin"])) / Decimal("100")).quantize(Decimal("0.0001"))

    def clean_employees(self):
        return int(self.cleaned_data["employees"])

    def clean_years_active(self):
        return int(self.cleaned_data["years_active"])


from .models import CompanyValuationReview


class CompanyValuationReviewForm(forms.ModelForm):
    class Meta:
        model = CompanyValuationReview
        fields = ["perceived_value", "reason"]
        labels = {
            "perceived_value": "Valor percibido por el fundador",
            "reason": "Motivo de la revision",
        }
        widgets = {
            "perceived_value": forms.NumberInput(attrs={"min": "1", "step": "1", "inputmode": "numeric"}),
            "reason": forms.Textarea(attrs={"rows": 4, "placeholder": "Contanos por que la valuacion automatica no representa bien a la empresa."}),
        }


class CompanyIpoUpdateForm(forms.Form):
    update_type = forms.ChoiceField(
        label="Tipo de novedad",
        choices=[
            ("info", "Informacion relevante"),
            ("problema", "Problema detectado"),
            ("solucion", "Nueva solucion"),
            ("hito", "Hito comercial"),
            ("finanzas", "Dato financiero"),
        ],
    )
    impact = forms.ChoiceField(
        label="Impacto esperado",
        choices=[
            ("positivo", "Positivo"),
            ("neutral", "Neutral"),
            ("negativo", "Negativo"),
        ],
    )
    title = forms.CharField(
        label="Titulo",
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Ej: Nuevo contrato con cadena regional"}),
    )
    description = forms.CharField(
        label="Detalle",
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Describe que cambio y por que podria afectar el valor de la empresa."}),
    )


class CompanyShareStructureForm(forms.Form):
    total_shares = forms.IntegerField(
        label="Cantidad total de acciones",
        min_value=100,
        max_value=1000000000,
        widget=forms.NumberInput(attrs={"min": "100", "step": "100", "inputmode": "numeric"}),
    )
    public_float_percent = forms.DecimalField(
        label="% liberado al mercado",
        min_value=Decimal("0"),
        max_value=Decimal("100"),
        decimal_places=2,
        max_digits=5,
        widget=forms.NumberInput(attrs={"min": "0", "max": "100", "step": "0.5", "inputmode": "decimal"}),
    )


from .models import CapitalOffering, InvestorProfile, OfferingEvidence


class CapitalOfferingForm(forms.ModelForm):
    DEFAULT_CAPITAL_TARGET = Decimal("10000000")

    class Meta:
        model = CapitalOffering
        fields = [
            "documentation_status",
            "instrument_stage",
            "summary",
            "location",
            "founder_name",
            "public_contact",
            "capital_target",
            "minimum_reservation",
            "offered_percent",
            "expansion_plan",
            "use_of_funds",
            "milestone_1",
            "milestone_2",
            "milestone_3",
            "reporting_frequency",
            "information_commitment",
            "shareholder_decisions",
            "capital_release_terms",
            "risks",
            "contract_terms",
        ]
        labels = {
            "documentation_status": "Estado documental",
            "instrument_stage": "Servicio opcional si ambas partes avanzan",
            "summary": "Que hace la empresa y por que abre su capital",
            "location": "Ciudad y provincia",
            "founder_name": "Nombre publico del fundador",
            "public_contact": "Canal de contacto publico",
            "capital_target": "Capital buscado",
            "minimum_reservation": "Reserva minima por persona",
            "offered_percent": "Porcentaje ofrecido",
            "expansion_plan": "Plan de expansion",
            "use_of_funds": "Uso detallado del capital",
            "milestone_1": "Hito 1",
            "milestone_2": "Hito 2",
            "milestone_3": "Hito 3",
            "reporting_frequency": "Frecuencia de reportes",
            "information_commitment": "Informacion que se publicara",
            "shareholder_decisions": "Decisiones que se informaran o consultaran",
            "capital_release_terms": "Reglas para liberar el capital",
            "risks": "Riesgos principales",
            "contract_terms": "Condiciones de contacto y compromisos iniciales",
        }
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 4}),
            "capital_target": forms.NumberInput(attrs={"min": "1", "step": "1", "placeholder": "10000000"}),
            "minimum_reservation": forms.NumberInput(attrs={"min": "1", "step": "1"}),
            "offered_percent": forms.NumberInput(attrs={"min": "0.01", "max": "100", "step": "0.01"}),
            "expansion_plan": forms.Textarea(attrs={"rows": 5}),
            "use_of_funds": forms.Textarea(attrs={"rows": 5}),
            "information_commitment": forms.Textarea(attrs={"rows": 4}),
            "shareholder_decisions": forms.Textarea(attrs={"rows": 4}),
            "capital_release_terms": forms.Textarea(attrs={"rows": 4}),
            "risks": forms.Textarea(attrs={"rows": 5}),
            "contract_terms": forms.Textarea(attrs={"rows": 8}),
        }

    def clean(self):
        cleaned = super().clean()
        target = cleaned.get("capital_target")
        minimum = cleaned.get("minimum_reservation")
        offered_percent = cleaned.get("offered_percent")
        if target is not None and target <= 0:
            self.add_error("capital_target", "El capital buscado debe ser mayor a cero.")
        if minimum is not None and minimum <= 0:
            self.add_error("minimum_reservation", "La reserva minima debe ser mayor a cero.")
        if target and minimum and minimum > target:
            self.add_error("minimum_reservation", "La reserva minima no puede superar el capital buscado.")
        if offered_percent is not None and not Decimal("0") < offered_percent <= Decimal("100"):
            self.add_error("offered_percent", "El porcentaje ofrecido debe estar entre 0 y 100.")
        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["capital_target"].initial = self.DEFAULT_CAPITAL_TARGET


class CapitalReservationForm(forms.Form):
    amount = forms.DecimalField(
        label="Monto tentativo para comprar acciones",
        min_value=Decimal("1"),
        max_digits=16,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"min": "1", "step": "1", "inputmode": "decimal"}),
    )
    accept_contract = forms.BooleanField(
        label="Lei esta version del contrato de compromisos y entiendo que la compra se instrumenta despues entre partes.",
    )


class InvestorProfileForm(forms.ModelForm):
    class Meta:
        model = InvestorProfile
        fields = ["full_name", "document_id", "tax_id", "phone", "city", "risk_acknowledged", "data_consent"]
        labels = {
            "full_name": "Nombre real completo",
            "document_id": "DNI o documento",
            "tax_id": "CUIT/CUIL",
            "phone": "Telefono",
            "city": "Ciudad",
            "risk_acknowledged": "Entiendo que esta solicitud no transfiere acciones ni dinero y que toda inversion posterior tiene riesgo.",
            "data_consent": "Acepto que InverFacil registre estos datos para identificar solicitudes de compra e interesados.",
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("risk_acknowledged"):
            self.add_error("risk_acknowledged", "Debes aceptar el aviso de riesgo para reservar.")
        if not cleaned.get("data_consent"):
            self.add_error("data_consent", "Debes aceptar el tratamiento de datos para identificar la reserva.")
        return cleaned


class OfferingEvidenceForm(forms.ModelForm):
    class Meta:
        model = OfferingEvidence
        fields = ["evidence_type", "title", "description", "status", "file", "external_url"]
        labels = {
            "evidence_type": "Tipo",
            "title": "Titulo",
            "description": "Descripcion",
            "status": "Estado de verificacion",
            "file": "Archivo",
            "external_url": "Link externo",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("file") and not cleaned.get("external_url"):
            self.add_error("file", "Agrega un archivo o un link externo.")
        return cleaned


class OfferingQuestionForm(forms.Form):
    question = forms.CharField(
        label="Pregunta publica al fundador",
        max_length=1000,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Escribi una pregunta concreta sobre el negocio, los riesgos o el contrato."}),
    )


class OfferingAnswerForm(forms.Form):
    answer = forms.CharField(
        label="Respuesta publica",
        max_length=3000,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
