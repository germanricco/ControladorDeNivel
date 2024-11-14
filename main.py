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
lista_mediciones = []
lista_umbral_inferior = []
lista_umbral_superior = []

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

        #!print(f"Respuesta recibida: {respuesta}")
                
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
            # Solicitar y actualizar distancia
            distancia = solicitar_valor(arduino, 1, 'D', tiempo_espera)
            if distancia is not None:
                try:
                    app.distancia.set(f"Distancia: {distancia} cm")
                    #Agrego medicion a lista
                    lista_mediciones.append(int(distancia))
                except Exception as e:
                    app.distancia.set("Error al actualizar")

            # Solicitar y actualizar porcentaje de llenado
            porcentaje = solicitar_valor(arduino, 1, 'P', tiempo_espera)
            if porcentaje is not None:
                try:
                    app.porcentaje.set(f"Porcentaje de Llenado: {porcentaje}%")
                except Exception as e:
                    app.distancia.set("Error al actualizar")

            # Solicitar y actualizar contador_inferior
            contador_inferior = solicitar_valor(arduino, 1, 'CI', tiempo_espera)
            if contador_inferior is not None:
                try:
                    app.contador_inf.set(f"Contador Inferior: {contador_inferior}")
                except Exception as e:
                    app.contador_inf.set("Error al actualizar")

            # Solicitar y actualizar contador_superior
            contador_superior = solicitar_valor(arduino, 1, 'CS', tiempo_espera)
            if contador_superior is not None:
                try:
                    app.contador_sup.set(f"Contador Superior: {contador_superior}")
                except Exception as e:
                    app.contador_sup.set("Error al actualizar")

            # Solicitar y actualizar el estado manual o automatico
            modo_manual = solicitar_valor(arduino, 1, "M", tiempo_espera)
            if modo_manual is not None:
                try:
                    app.modo_manual.set(f"Modo Manual: {modo_manual}")
                except Exception as e:
                    app.modo_manual.set("Error al actualizar")

            bomba_prendida = solicitar_valor(arduino, 1, "B", tiempo_espera)
            if bomba_prendida is not None:
                try:
                    app.bomba_prendida.set(f"Estado Bomba: {bomba_prendida}")
                except Exception as e:
                    app.bomba_prendida.set("Error al actualizar")

            # Solicitar y actualizar umbral_inferior
            umbral_inferior = solicitar_valor(arduino, 1, 'UI', tiempo_espera)
            if umbral_inferior is not None:
                try:
                    app.umbral_inf.set(f"Umbral Inferior: {umbral_inferior} cm")
                    #Agrego umbral a lista
                    lista_umbral_inferior.append(umbral_inferior)
                except Exception as e:
                    app.umbral_inf.set("Error al actualizar")

            # Solicitar y actualizar umbral_superior
            umbral_superior = solicitar_valor(arduino, 1, 'US', tiempo_espera)
            if umbral_superior is not None:
                try:
                    app.umbral_sup.set(f"Umbral Superior: {umbral_superior} cm")
                    #Agrego umbral a lista
                    lista_umbral_superior.append(int(umbral_superior))
                except Exception as e:
                    app.umbral_sup.set("Error al actualizar")  

            # Solicitar margen de histeresis
            margen_histeresis = solicitar_valor(arduino, 1, "H", tiempo_espera)
            if margen_histeresis is not None:
                try:
                    app.margen_hist.set(f"Histeresis: {margen_histeresis} cm")
                except Exception as e:
                    app.margen_hist.set("Error al actualizar")

            

            # Actualizo tiempos
            ultimo_tiempo_solicitud = tiempo_actual
        
        #Espera
        time.sleep(0.1)

def cerrar_aplicacion(arduino, ventana):
    global ejecutando
    ejecutando = False

    # Frena actualización del gráfico (dejar de solicitar valores)
    if ventana.id_actualizar_grafico:
        ventana.after_cancel(ventana.id_actualizar_grafico)  # Cancela la actualización del gráfico

    print("Cerrando conexion con Arduino")
    if arduino.is_connected():
        arduino.desconectar()
        
    print("Aplicación cerrada.")
    ventana.destroy()


def main():
    # Configuración inicial
    global ejecutando
    ejecutando = True

    arduino = Arduino(port="COM7", baudrate=28800, sketch_path=path_arduino)
    #*arduino.subir_sketch()

    arduino.conectar()

    #Intentar reconectar si no hay conexion
    if not arduino.is_connected():
        print("Conexion inicial fallida. Intentando reconectar")
        if not arduino.reconectar(intentos=5, delay=2):
            print("No se pudo establecer la conexión con el Arduino. Saliendo del programa.")
            return
        
    periodo_solicitud = 1  # Intervalo en segundos entre solicitudes
    tiempo_espera = 0.2  # Tiempo de espera en segundos para la respuesta

    app = MonitorGUI(arduino, enviar_comando, lista_mediciones, lista_umbral_inferior, lista_umbral_superior)

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
    


