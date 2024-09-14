from django.db import models

class CarreraRata(models.Model):
    patrimonio_neto = models.DecimalField(max_digits=12, decimal_places=2)
    ingreso_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    gasto_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    fuentes_ingreso = models.IntegerField()
    horas_trabajadas = models.DecimalField(max_digits=4, decimal_places=2)
    categoria_final = models.CharField(max_length=50, blank=True)

    def calcular_categoria(self):
        def asignar_categoria(valor, rangos):
            for i, rango in enumerate(rangos, start=1):
                if valor < rango:
                    return i
            return len(rangos) + 1

        # Definir los rangos para cada parámetro
        rangos_pn = [5000, 15000, 30000, 65000, 150000, 350000, 800000]
        rangos_im = [500, 1500, 3000, 5000, 10000, 20000, 50000]
        rangos_gm = [500, 1500, 3000, 5000, 10000, 20000, 50000]
        rangos_fi = [2, 3, 4, 5, 6, 7, 8]
        rangos_hl = [2, 3, 4, 5, 6, 7, 8]

        # Calcular las categorías
        categoria_pn = asignar_categoria(self.patrimonio_neto, rangos_pn)
        categoria_im = asignar_categoria(self.ingreso_mensual, rangos_im)
        categoria_gm = asignar_categoria(self.gasto_mensual, rangos_gm)
        categoria_fi = asignar_categoria(self.fuentes_ingreso, rangos_fi)
        categoria_hl = 9 - asignar_categoria(self.horas_trabajadas, rangos_hl)  # Invertir la categoría de horas trabajadas

        # Sumar todos los puntajes
        puntaje_total = categoria_pn + categoria_im + categoria_gm + categoria_fi + categoria_hl

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

    def __str__(self):
        return f"Categoría {self.categoria_final} - PN: {self.patrimonio_neto}"

    def save(self, *args, **kwargs):
        self.calcular_categoria()
        super(CarreraRata, self).save(*args, **kwargs)
