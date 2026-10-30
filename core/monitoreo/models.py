from django.db import models


class Mensaje(models.Model):
    recibido = models.DateTimeField(auto_now_add=True, db_index=True)
    tipo = models.CharField(max_length=10)
    id_transaccion = models.CharField(max_length=20)
    origen = models.CharField(max_length=3)
    destino = models.CharField(max_length=3)
    monto = models.BigIntegerField()
    fecha_hora_origen = models.DateTimeField()

    contenido = models.TextField()

    class Meta:
        db_table = "mensaje"
        ordering = ["-recibido"]

    def __str__(self):
        return f"{self.recibidoen:%d-%m-%Y %H:%M:%S} {self.tipo} {self.id_transaccion}"