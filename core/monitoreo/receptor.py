"""
Receptor TCP del CCA.

- Escucha conexiones TCP.
- Por cada mensaje recibido: lo graba como un registro en la tabla Mensaje y responde OK.
- Cada pocos segundos escribe el latido en el archivo de control.

SUPUESTOS (ajustar cuando se conozca lo real):
- Cada mensaje termina con un salto de línea.
- Formato: tipo|id|origen|destino|monto|fechahora
- Respuesta: "OK" si se grabó, "ERROR" si no.

Ejecutar desde la carpeta de manage.py:
    python -m monitoreo.receptor
"""
import os
import socketserver
import threading
import time
from datetime import datetime

# --- Cargar Django para poder grabar en la tabla ---
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db import connection
from django.utils import timezone

from monitoreo.models import Mensaje
from monitoreo.control import marcar_operativo

# Valores fijos por ahora (después pasan a settings.py)
HOST = "0.0.0.0"
PUERTO = 5000
INTERVALO_LATIDO_S = 2


def latido():
    """Corre en paralelo para siempre: escribe el latido cada INTERVALO_LATIDO_S."""
    while True:
        marcar_operativo()
        time.sleep(INTERVALO_LATIDO_S)


def grabar_mensaje(linea):
    """Separa el mensaje en sus partes y lo graba. Si viene mal, lanza error."""
    partes = linea.split("|")

    if len(partes) != 6:
        raise ValueError(f"se esperaban 6 campos y llegaron {len(partes)}")

    tipo = partes[0]
    id_transaccion = partes[1]
    origen = partes[2]
    destino = partes[3]
    monto = int(partes[4])
    fecha_hora = datetime.strptime(partes[5], "%Y%m%d%H%M%S")

    Mensaje.objects.create(
        tipo=tipo,
        id_transaccion=id_transaccion,
        origen=origen,
        destino=destino,
        monto=monto,
        fecha_hora_origen=timezone.make_aware(fecha_hora),
        contenido=linea,
    )


class ManejadorCliente(socketserver.StreamRequestHandler):
    """Atiende una conexión. Se crea uno por cada cliente que se conecta."""

    def handle(self):
        ip = self.client_address[0]
        print(f"Conectado: {ip}")

        try:
            # Lee línea por línea mientras el cliente siga conectado
            for linea_bytes in self.rfile:
                linea = linea_bytes.decode("utf-8").strip()

                if linea == "":
                    continue

                # Aquí irían los mensajes de control (pedido de reenvío)

                try:
                    grabar_mensaje(linea)
                    self.wfile.write(b"OK\n")
                except Exception as error:
                    print(f"Mensaje con error desde {ip}: {error}")
                    self.wfile.write(b"ERROR\n")
        finally:
            # Cada conexión usa su propia conexión a la base; se cierra al terminar
            connection.close()
            print(f"Desconectado: {ip}")


class Servidor(socketserver.ThreadingTCPServer):
    allow_reuse_address = True   # permite reiniciar sin esperar a que se libere el puerto
    daemon_threads = True        # al cortar el programa, se cortan todas las conexiones


def main():
    servidor = Servidor((HOST, PUERTO), ManejadorCliente)

    hilo_latido = threading.Thread(target=latido, daemon=True)
    hilo_latido.start()

    print(f"Receptor escuchando en {HOST}:{PUERTO}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("Receptor detenido")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()