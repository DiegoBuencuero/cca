import os
import time
 # ahora fijo
ARCHIVO_CONTROL = "estado_receptor.txt"
TIMEOUT_S = 10


def marcar_operativo():
    """La llama el receptor cada x segundos -  meter parametro configurable?."""
    temporal = ARCHIVO_CONTROL + ".tmp" #Solo existe un instante y sirve para que Django nunca lea el archivo a medio escribir.

    archivo = open(temporal, "w") #lo crea si no existe y lo vacía si existe, y deja escribir
    archivo.write(str(time.time()))
    archivo.close()

    # Reemplaza de una vez para que nunca se lea a medio escribir
    os.replace(temporal, ARCHIVO_CONTROL)


def esta_operativo():
    try:
        archivo = open(ARCHIVO_CONTROL)
        contenido = archivo.read()
        archivo.close()
    except FileNotFoundError:
        return False

    try:
        ultima_senal = float(contenido)
    except ValueError:
        return False

    segundos_sin_senal = time.time() - ultima_senal

    if segundos_sin_senal > TIMEOUT_S:
        return False

    return True