import serial
import time
import subprocess   #para manejar compilación y subida de sketch a Arduino

class Arduino:
    """
    Clase para controlar Arduino utilizando puerto USB

    Argumentos:
        -port: puerto USB donde está conectado arduino.
        -baudrate: velocidad de conexion.
        -fqbn: modelo de arduino.
        -sketch_path: path al archivo .ino
        -connection: booleando para verificar si placa Arduino esta o no conectado
    Metodos:
        -conectar(self): establece conexion con el Arduino a través de puerto serial.
        -reconectar(self, intentos=5, delay=2): intenta reconectar el arduino.
        -desconectar(self): cierra la conexion serial con el Arduino.
        -subir_sketch(self): compila y sube el sketch al Arduino.
        -is_connected(self): comprueba si la conexion serial está abierta.
        -recibir_datos(self): lee datos de arduino por puerto serial.
        -enviar_datos(): envia datos por puerto serial
        -flushInput(self): Limpia el buffer de entrada

    """
    def __init__(self, port='/dev/ttyACM0', baudrate=9600, fqbn='arduino:avr:uno', sketch_path='ruta_del_sketch.ino'):
        self.port = port
        self.baudrate = baudrate
        self.fqbn = fqbn
        self.sketch_path = sketch_path
        self.connection = None

    def conectar(self):
        """Establece una conexión con el Arduino a través del puerto serial."""
        try:
            self.connection = serial.Serial(self.port, self.baudrate)
            print(f"Conectado a Arduino en {self.port} a {self.baudrate} baudios.")
            time.sleep(2)  # Esperar para asegurar la conexión con el Arduino
        except Exception as e:
            print(f"Error al conectar: {e}")

    def reconectar(self, intentos=5, delay=2):
        """
        Intenta reconectar el Arduino un número específico de veces.
        - `intentos`: Número de intentos de reconexión.
        - `delay`: Tiempo de espera entre intentos en segundos.
        """
        for intento in range(1, intentos + 1):
            print(f"Intentando reconectar... (Intento {intento} de {intentos})")
            self.conectar()
            if self.is_connected():
                print("Reconexión exitosa.")
                return True
            print(f"Fallo en la reconexión. Esperando {delay} segundos para reintentar...")
            time.sleep(delay)
        
        print("No se pudo establecer la conexión después de varios intentos.")
        return False  # Retorna False si no se pudo reconectar

    def desconectar(self):
        """Cierra la conexión serial con el Arduino."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Conexion cerrada.")

    def subir_sketch(self):
        """Compila y sube el sketch a la placa Arduino."""
        if self.is_connected():
            self.connection.close()

        compile_command = ["C:\\Program Files\\Arduino\\arduino-cli_1.0.4_Windows_64bit\\arduino-cli.exe", "compile", "--fqbn", self.fqbn, self.sketch_path]
        upload_command = ["C:\\Program Files\\Arduino\\arduino-cli_1.0.4_Windows_64bit\\arduino-cli.exe", "upload", "-p", self.port, "--fqbn", self.fqbn, self.sketch_path]

        #Compilar
        print("Compilando el codigo de Arduino...")
        result = subprocess.run(compile_command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error de compilacion: {result.stderr}")
            return False

        #Subir a Arduino
        print("Subiendo el codigo al Arduino...")
        result = subprocess.run(upload_command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error al subir: {result.stderr}")
            return False
        else:
            print("Subida exitosa.")
            return True
        
    def is_connected(self):
        """Comprueba si la conexión serial está abierta."""
        return self.connection and self.connection.is_open

    def enviar_datos(self, trama):
        # Envia una trama al Arduino en formato ASCII decimal.
        if self.is_connected():
            try:
                # Enviar la trama completa
                self.connection.write(trama.encode('ascii'))

            except serial.SerialException as e:
                print(f"Error al enviar datos: {e}")
        else:
            print("No hay conexion establecida para enviar datos.")

    def recibir_datos(self):
        # Recibir trama del Arduino
        if self.is_connected():
            try:
                # Leer hasta el carácter '\r', decodificar bytes según ascii y eliminar espacios
                trama = self.connection.read_until(b'\r').decode('ascii')
                if trama.endswith('\r'):
                    trama = trama.strip()
                    return trama
                else:
                    print("Error. el mensaje no termina con '\r'. ")
                    return None
            
            except serial.SerialException as e:
                print(f"Error al recibir datos: {e}")
                return None
        else:
            print("No hay conexion establecida para recibir datos. ")
            return None
        
    def flushInput(self):
        """Limpia el búfer de entrada del puerto serial."""
        if self.connection and self.connection.is_open:
            self.connection.reset_input_buffer()

