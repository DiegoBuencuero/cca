from django.contrib import admin
from .models import Mensaje


class MensajeAdmin(admin.ModelAdmin):
    list_display = ("recibido", "tipo", "id_transaccion",
                    "origen", "destino", "monto")
    search_fields = ("id_transaccion",)


admin.site.register(Mensaje, MensajeAdmin)