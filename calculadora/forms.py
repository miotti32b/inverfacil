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

class ClientePerfilForm(forms.ModelForm):
    class Meta:
        model = ClientePerfil
        exclude = ["perfil_asignado", "feedback", "creado_en"]

    # --- Bloque 1 – Datos básicos ---
    estado_civil = forms.ChoiceField(
        choices=[
            ("soltero", "Soltero"),
            ("casado", "Casado"),
            ("pareja", "En pareja"),
            ("otro", "Otro"),
        ],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # --- Bloque 3 – Objetivos ---
    objetivos = forms.MultipleChoiceField(
        choices=[
            ("vivienda", "Comprar vivienda"),
            ("vehiculo", "Comprar vehículo"),
            ("independencia", "Independencia financiera"),
            ("jubilacion", "Jubilarme anticipadamente"),
            ("viajar", "Viajar"),
            ("educar", "Educar a mis hijos"),
            ("negocio", "Emprender un negocio"),
            ("vida", "Mejorar mi nivel de vida"),
            ("ahorro", "Aumentar mi ahorro/inversiones"),
            ("otro", "Otro"),
        ],
        widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona hasta 3"
    )

    plazo_inversion = forms.ChoiceField(
        choices=[
            ("corto", "Corto (< 2 años)"),
            ("mediano", "Mediano (2-7 años)"),
            ("largo", "Largo (> 7 años)"),
        ],
        widget=forms.RadioSelect
    )

    # --- Bloque 4 – Perfil psicológico ---
    reaccion_perdida = forms.ChoiceField(
        choices=[
            ("retiro", "Retiro todo para no perder más"),
            ("mantengo", "Mantengo y espero"),
            ("aporto", "Aporto más para aprovechar"),
            ("nose", "No sabría qué hacer"),
        ],
        widget=forms.RadioSelect
    )

    importancia_dinero = forms.MultipleChoiceField(
        choices=[
            ("seguridad", "Seguridad y tranquilidad"),
            ("libertad", "Libertad y oportunidades"),
            ("disfrute", "Disfrute y experiencias"),
            ("status", "Poder y status"),
            ("metas", "Herramienta para lograr mis metas"),
            ("ayuda", "Medio para ayudar a otros"),
        ],
        widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona 2"
    )

    uso_millon = forms.MultipleChoiceField(
        choices=[
            ("viajes", "Lo gasto en viajes/compras/experiencias"),
            ("emergencias", "Lo guardo para emergencias"),
            ("negocio", "Lo invierto en un negocio o inmuebles"),
            ("diversifico", "Lo diversifico en inversiones financieras"),
            ("donar", "Lo dono o comparto con familia/causas"),
            ("educacion", "Lo uso para capacitarme"),
        ],
        widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona 2"
    )

    conocimiento_acciones = forms.ChoiceField(
        choices=[
            ("financiar", "Para obtener financiamiento y crecer"),
            ("pagar", "Para pagar deudas"),
            ("dividendos", "Para repartir dividendos"),
            ("nose", "No sé"),
        ],
        widget=forms.RadioSelect
    )

    conocimiento_seguridad = forms.MultipleChoiceField(
        choices=[
            ("usd", "Dólares en banco"),
            ("tesoro", "Bonos del Tesoro de EE.UU."),
            ("tierras", "Tierras"),
            ("negocio", "Negocio propio"),
            ("educacion", "Educación"),
            ("pfusd", "Plazo fijo en dólares"),
        ],
        widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona 2"
    )

    # --- Bloque 5 – Preferencias ---
    liquidez = forms.ChoiceField(
        choices=[
            ("alta", "Alta (dinero disponible siempre)"),
            ("media", "Media (puedo esperar algunos meses)"),
            ("baja", "Baja (puedo bloquear mi dinero varios años)"),
        ],
        widget=forms.RadioSelect
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
