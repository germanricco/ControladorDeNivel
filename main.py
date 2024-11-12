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
from Gui import MonitorGUI

#Variables Globales
ejecutando = True

# Crear un lock para el puerto serial
lock = threading.Lock()

def enviar_comando (arduino, app, comando, tiempo_espera=0.2):
    with lock:
        arduino.flushInput()
        arduino.enviar_datos(comando)
        time.sleep(tiempo_espera)
        respuesta_consigna = arduino.recibir_datos()

    #La respuesta de arduino debe ser un eco del comando enviado
    if (respuesta_consigna and respuesta_consigna == comando):
        app.respuesta.set("Parametro modificado correctamente")
    else:
        app.respuesta.set("No se pudo ejecutar el comando")



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
        print("Error. Al recibir trama respuesta. ")

def actualizar_valores (arduino, app, periodo_solicitud, tiempo_espera):
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
            #1. Solicitar y actualizar distancia
            distancia = solicitar_valor(arduino, 1, 'D', tiempo_espera)
            if distancia is not None:
                try:
                    app.distancia.set(f"Distancia: {distancia} cm")
                except Exception as e:
                    app.distancia.set("Error al actualizar")

            #2. Solicitar y actualizar contador_inferior
            contador_inferior = solicitar_valor(arduino, 1, 'CI', tiempo_espera)
            if contador_inferior is not None:
                try:
                    app.contador_inf.set(f"Contador Inferior: {contador_inferior}")
                except Exception as e:
                    app.contador_inf.set("Error al actualizar")

            #3. Solicitar y actualizar contador_superior
            contador_superior = solicitar_valor(arduino, 1, 'CS', tiempo_espera)
            if contador_superior is not None:
                try:
                    app.contador_sup.set(f"Contador Superior: {contador_superior}")
                except Exception as e:
                    app.contador_sup.set("Error al actualizar")
            """
            # Solicitar el valor del umbral inferior
            umbral_superior = solicitar_valor(arduino, 1, 'UI', tiempo_espera)
            if umbral_superior is not None:
                try:
                    app.umbral_sup.set(f"Umbral Superior: {umbral_superior} cm")
                except Exception as e:
                    app.umbral_sup.set("Error al actualizar")
            """

            # Actualizo tiempos
            ultimo_tiempo_solicitud = tiempo_actual
        
        #Espera
        time.sleep(0.1)

def cerrar_aplicacion(arduino, ventana):
    global ejecutando
    ejecutando = False
    arduino.desconectar()
    ventana.destroy()
    print("Aplicación cerrada.")

def main():
    # Configuración inicial
    global ejecutando
    ejecutando = True

    arduino = Arduino(port="COM3", baudrate=9600, sketch_path=path_arduino)
    #*arduino.subir_sketch()

    arduino.conectar()

    #Intentar reconectar si no hay conexion
    if not arduino.is_connected():
        print("Conexion inicial fallida. Intentando reconectar")
        if not arduino.reconectar(intentos=5, delay=2):
            print("No se pudo establecer la conexión con el Arduino. Saliendo del programa.")
            return
        
    periodo_solicitud = 2  # Intervalo en segundos entre solicitudes
    tiempo_espera = 0.5  # Tiempo de espera en segundos para la respuesta

    app = MonitorGUI(arduino, enviar_comando)

    app.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(arduino, app))
        
    # Iniciar el hilo para actualizar los valores en el GUI con la función actualizar_valores
    hilo_actualizar = threading.Thread(target=actualizar_valores, args=(arduino, app, periodo_solicitud, tiempo_espera), daemon=True)
    hilo_actualizar.start()

    try:
        app.mainloop()

    except KeyboardInterrupt:
        # Manejo de interrupción con CTRL+C
        print("\nCerrando Aplicacion")
        arduino.desconectar()

if __name__ == "__main__":
    main()
    


