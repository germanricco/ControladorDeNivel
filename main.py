#Importar librerias
from pathlib import Path
import sys
import os
import time
import threading

#Obtener directorios
directorio_actual = os.getcwd()
path_actual = Path(directorio_actual)
path_arduino = path_actual / "src"

#Importar módulos      
sys.path.append(str(directorio_actual))
from Arduino import Arduino
from Protocolo import Protocolo


arduino = Arduino(port="COM3", baudrate=9600, sketch_path=path_arduino)
#arduino.subir_sketch()  #* Comentar para no actualizar sketch

ejecutando = True

# Crear un lock para el puerto serial
lock = threading.Lock()

def solicitar_valor (arduino, num_direccion, parametro, tiempo_espera):
    """
    Solicita un valor específico al Arduino
    -'arduino': objeto arduino conectado
    -'num_dirección': direccion del dispositivo (como entero)
    -'parametro': Parametro a solicitar (por ej. 'D')
    -'tiempo_espera': Entre que envia el mensaje y recibe la respuesta
    """
    
    # Crear la trama de solicitud
    trama_solicitud = Protocolo.crear_trama_solicitud(num_direccion, parametro)
    with lock:
        # Enviar y recibir trama
        arduino.flushInput()
        arduino.enviar_datos(trama_solicitud)
        time.sleep(tiempo_espera)
        respuesta = arduino.recibir_datos()
                
        # Verificar si la trama de respuesta tiene algo y es valida
    if respuesta and Protocolo.verificar_trama(respuesta, num_direccion, parametro):
        # Extraer e imprime el valor
        if (len(parametro) == 2):
            valor_str = respuesta[4:len(respuesta)]
            valor = int(valor_str)
            return valor
        else:
            valor_str = respuesta[3:len(respuesta)]
            valor = int(valor_str)    
            return valor
    else:
        print("Error. Al recibir trama distancia.")

def actualizar_valores (arduino, periodo_solicitud, tiempo_espera):
    """"Hilo que solicita valores periodicamente al Arduino"""
    global ejecutando
    # Defino antes del bucle
    ultimo_tiempo_solicitud = time.time()

    while ejecutando:
        tiempo_actual = time.time()
        if not arduino.is_connected():
            print("Arduino desconectado. No se pudo solicitar valores.")
            break

        if tiempo_actual - ultimo_tiempo_solicitud >= periodo_solicitud:

            distancia = solicitar_valor(arduino, 1, 'D', tiempo_espera)
            if distancia is not None:
                print(f"Distancia: {distancia}")

            contador_inferior = solicitar_valor(arduino, 1, 'CI', tiempo_espera)
            if contador_inferior is not None:
                print(f"Contador Inferior: {contador_inferior}")

            contador_superior = solicitar_valor(arduino, 1, 'CS', tiempo_espera)
            if contador_superior is not None:
                print(f"Contador Superior: {contador_superior}")

            posicion_servo = solicitar_valor(arduino, 1, 'M', tiempo_espera)
            if posicion_servo is not None:
                print(f"Posición Servo: {posicion_servo}")

            # Actualizo tiempos
            ultimo_tiempo_solicitud = tiempo_actual
        
        #Espera
        time.sleep(0.2)

def main():
    global ejecutando
    arduino.conectar()

    #Intentar reconectar si no hay conexion
    if not arduino.is_connected():
        print("Conexion inicial fallida. Intentando reconectar")
        if not arduino.reconectar(intentos=5, delay=2):
            print("No se pudo establecer la conexión con el Arduino. Saliendo del programa.")
            return

    # Configuracion
    periodo_solicitud = 5  # Intervalo en segundos entre solicitudes
    tiempo_espera = 0.5  # Tiempo de espera en segundos para la respuesta

    try:
        actualizar_valores(arduino, periodo_solicitud, tiempo_espera)

    except KeyboardInterrupt:
        print("Cerrando Aplicacion")
        arduino.desconectar()


if __name__ == "__main__":
    main()
