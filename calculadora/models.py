from django.db import models

# Create your models here.

class CarreraRata(models.Model):
    patrimonio_neto = models.DecimalField(max_digits=12, decimal_places=2)
    ingreso_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    gasto_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    fuentes_ingreso = models.IntegerField()
    horas_trabajadas = models.DecimalField(max_digits=4, decimal_places=2)
    categoria_final = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Categoría {self.categoria_final} - PN: {self.patrimonio_neto}"


class CarreraRata(models.Model):
    patrimonio_neto = models.DecimalField(max_digits=12, decimal_places=2)
    ingreso_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    gasto_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    fuentes_ingreso = models.IntegerField()
    horas_trabajadas = models.DecimalField(max_digits=4, decimal_places=2)
    categoria_final = models.CharField(max_length=50, blank=True)

    def calcular_categoria(self):
        # Categorías basadas en Patrimonio Neto
        if self.patrimonio_neto < 5000:
            categoria_pn = 1
        elif 5000 <= self.patrimonio_neto < 15000:
            categoria_pn = 2
        elif 15000 <= self.patrimonio_neto < 30000:
            categoria_pn = 3
        elif 30000 <= self.patrimonio_neto < 65000:
            categoria_pn = 4
        elif 65000 <= self.patrimonio_neto < 150000:
            categoria_pn = 5
        elif 150000 <= self.patrimonio_neto < 350000:
            categoria_pn = 6
        elif 350000 <= self.patrimonio_neto < 800000:
            categoria_pn = 7
        else:
            categoria_pn = 8

        # Repetimos para Ingreso Mensual, Gasto Mensual, etc.
        # Este es un ejemplo para Ingreso Mensual

        if self.ingreso_mensual < 500:
            categoria_im = 1
        elif 500 <= self.ingreso_mensual < 1500:
            categoria_im = 2
        elif 1500 <= self.ingreso_mensual < 3000:
            categoria_im = 3
        elif 3000 <= self.ingreso_mensual < 5000:
            categoria_im = 4
        elif 5000 <= self.ingreso_mensual < 10000:
            categoria_im = 5
        elif 10000 <= self.ingreso_mensual < 20000:
            categoria_im = 6
        elif 20000 <= self.ingreso_mensual < 50000:
            categoria_im = 7
        else:
            categoria_im = 8

        # gasto mensual...
        
        if self.gasto_mensual < 500:
            categoria_gm = 1
        elif 500 <= self.gasto_mensual < 1500:
            categoria_gm = 2
        elif 1500 <= self.gasto_mensual < 3000:
            categoria_gm = 3
        elif 3000 <= self.gasto_mensual < 5000:
            categoria_gm = 4
        elif 5000 <= self.gasto_mensual < 10000:
            categoria_gm = 5
        elif 10000 <= self.gasto_mensual < 20000:
            categoria_gm = 6
        elif 20000 <= self.gasto_mensual < 50000:
            categoria_gm = 7
        else:
            categoria_gm = 8


        # fuentes ingreso...
        if self.fuentes_ingreso < 2:
            categoria_fi = 1
        elif 2 <= self.fuentes_ingreso < 3:
            categoria_fi = 2
        elif 3 <= self.fuentes_ingreso < 4:
            categoria_fi = 3
        elif 4 <= self.fuentes_ingreso < 5:
            categoria_fi = 4
        elif 5 <= self.fuentes_ingreso < 6:
            categoria_fi = 5
        elif 6 <= self.fuentes_ingreso < 7:
            categoria_fi = 6
        elif 7 <= self.fuentes_ingreso < 8:
            categoria_fi = 7
        else:
            categoria_fi = 8
            
         # hora laburadas...
        if self.horas_trabajadas < 2:
            categoria_hl = 8
        elif 2 <= self.horas_trabajadas < 3:
            categoria_hl = 7
        elif 3 <= self.horas_trabajadas < 4:
            categoria_hl = 6
        elif 4 <= self.horas_trabajadas < 5:
            categoria_hl = 5
        elif 5 <= self.horas_trabajadas < 6:
            categoria_hl = 4
        elif 6 <= self.horas_trabajadas < 7:
            categoria_hl = 3
        elif 7 <= self.horas_trabajadas < 8:
            categoria_hl = 2
        else:
            categoria_hl = 1
        
        # Sumar todos los puntajes
        puntaje_total = categoria_pn + categoria_im + categoria_gm + categoria_fi + categoria_hl# + otros puntajes 

        # Asignar una categoría final basada en el puntaje total
        if puntaje_total <= 10:
            self.categoria_final = "Rata de por vida"
        elif 11 <= puntaje_total <= 15:
            self.categoria_final = "Rata Clásica"
        elif 16 <= puntaje_total <= 20:
            self.categoria_final = "Rata Consciente"
        elif 21 <= puntaje_total <= 25:
            self.categoria_final = "Rata Inteligente"
        else:
            self.categoria_final = "Rata Dorada"

        

    def save(self, *args, **kwargs):
        self.calcular_categoria()
        super(CarreraRata, self).save(*args, **kwargs)
