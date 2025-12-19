class Plan(models.Model):
    nombre = models.CharField(max_length=200)
    precio = models.IntegerField()

    def __str__(self):
        return self.nombre
