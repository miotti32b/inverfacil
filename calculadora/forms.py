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
