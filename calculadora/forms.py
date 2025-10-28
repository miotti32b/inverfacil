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

from django import forms
from .models import ClientePerfil
from decimal import Decimal, InvalidOperation

from django import forms
from .models import ClientePerfil

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

    reaccion_perdida = forms.ChoiceField(
        choices=[
            ("retiro", "🚪 Retiro todo"),
            ("mantengo", "🕒 Mantengo y espero"),
            ("aporto", "📉 Aporto más"),
            ("nose", "❓ No sé"),
        ],
        widget=forms.RadioSelect
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

    # --- Conversión automática de vacíos a 0 ---
    def clean(self):
        cleaned_data = super().clean()

        for field_name, value in cleaned_data.items():
            # Para campos numéricos vacíos → 0
            if value in (None, ""):
                field = self.fields.get(field_name)
                if isinstance(field, (forms.DecimalField, forms.IntegerField)):
                    cleaned_data[field_name] = 0

        return cleaned_data
