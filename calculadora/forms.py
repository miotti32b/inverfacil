# calculadora/forms.py
from django import forms
from .models import CarreraRata

class CarreraRataForm(forms.ModelForm):
    class Meta:
        model = CarreraRata
        fields = ['patrimonio_neto', 'ingreso_mensual', 'gasto_mensual', 'fuentes_ingreso', 'horas_trabajadas']
        