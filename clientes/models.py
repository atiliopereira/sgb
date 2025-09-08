from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    ruc = models.CharField(max_length=20)
    email = models.EmailField(
        blank=True,
        null=True,
    )
    numero_liquidacion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.nombre
