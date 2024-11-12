import tkinter as tk

class MonitorGUI(tk.Tk):
    #Constructor para inicializar la clase
    def __init__(self, arduino, enviar_comandos):
        super().__init__() # Llama al constructor de la clase base (tk.Tk)

        # Parámetros para actualizar valores
        self.arduino = arduino
        self.enviar_comandos = enviar_comandos

        # Configuracion de la ventana principal
        self.title("Test Aplication")
        self.geometry("800x600")

        # -- FRAME SUPERIOR --
        self.frame1 = tk.Frame(self, bg="gray")
        self.frame1.pack(side="top", fill="both", expand=True)

        #Frame Variables
        self.frameVariables = tk.Frame(self, bg="darkgray")
        self.frameVariables.place(relx=0, rely=0, relwidth=0.3, relheight=1)
        
        #Título de Frame Variables
        self.lblVariables = tk.Label(self.frameVariables,
                                     text="Variables",
                                     bg='lightgreen',
                                     font=('times', 24))
        self.lblVariables.grid(padx=10, pady=10, row=0)

        #* Repetir esta estructura para el resto de variables
        #Label variable de Distancia
        self.lbl_distancia = tk.Label(self.frameVariables)
        self.lbl_distancia.grid(padx=10, pady=10, row=1, columnspan=2)
        #Incicializar la variable distancia
        self.distancia = tk.StringVar()
        self.distancia.set("Cargando")
        self.lbl_distancia["textvariable"] = self.distancia

        #Label variable contador inf
        self.lbl_contador_inf = tk.Label(self.frameVariables)
        self.lbl_contador_inf.grid(padx=10, pady=10, row=2, columnspan=2)
        #Incicializar la variable contador_inf
        self.contador_inf = tk.StringVar()
        self.contador_inf.set("Cargando")
        self.lbl_contador_inf["textvariable"] = self.contador_inf

        #Label variable contador sup
        self.lbl_contador_sup = tk.Label(self.frameVariables)
        self.lbl_contador_sup.grid(padx=10, pady=10, row=3, columnspan=2)
        #Incicializar la variable contador_sup
        self.contador_sup = tk.StringVar()
        self.contador_sup.set("Cargando")
        self.lbl_contador_sup["textvariable"] = self.contador_sup

        """
        #Título de Frame Parámetros
        self.lblParametros = tk.Label(self.frameVariables,
                                      text="Parámetros",
                                      bg='lightblue',
                                      font=('times', 24))
        
        self.lblParametros.grid(padx=10, pady=10, row=2)

        #Label parametro umbral inferior
        self.lbl_umbral_inf = tk.Label(self.frameVariables)
        self.lbl_umbral_inf.grid(padx=10, pady=10, row=3)
        #Incicializar la variable umbral_inferior
        self.umbral_inf = tk.StringVar()
        self.umbral_inf.set("Cargando")
        self.lbl_umbral_inf["textvariable"] = self.umbral_inf

        #Label parametro umbral superior
        self.lbl_umbral_superior = tk.Label(self.frameVariables)
        self.lbl_umbral_superior.grid(padx=10, pady=10, row=4)
        #Incicializar la variable umbral_superior
        self.umbral_superior = tk.StringVar()
        self.umbral_superior.set("Cargando")
        self.lbl_umbral_superior["textvariable"] = self.umbral_superior
        """

        # -- FRAME INFERIOR --
        self.frame2 = tk.Frame(self, bg="blue")
        self.frame2.place(relx=0, rely=0.95, relwidth=1, relheight=0.05)
        
        # Mensaje Ingrese un comando
        self.lblComando = tk.Label(self.frame2, text="Ingrese un Comando: ")
        self.lblComando.config(font=('arial', 12))
        self.lblComando.anchor("nw")
        self.lblComando.place(relx=0, rely=0, relwidth=0.3, relheight=1)

        #Caja de Texto para ingresar el comando
        self.EntradaComando = tk.Entry(self.frame2)
        self.EntradaComando.config(font=('arial', 12))
        self.EntradaComando.place(relx=0.3, rely=0, relwidth=0.2, relheight=1)
        #Crea la variable para almacernar el comando ingresado
        self.comando = tk.StringVar()
        self.comando.set("")
        self.EntradaComando["textvariable"] = self.comando

        #Boton Enviar
        #utilizo función enviar_comandos(arduino, app, comando, tiempo_espera)
        self.BotonEnviar = tk.Button(self.frame2, text="Enviar", command=lambda: self.enviar_comandos(arduino, self, self.EntradaComando.get()))
        self.BotonEnviar.config(font=('arial', 12))
        self.BotonEnviar.place(relx=0.5, rely=0, relwidth=0.1, relheight=1)

        #Label variable de respuesta
        self.lbl_respuesta = tk.Label(self.frame2)
        self.lbl_respuesta.config(font=('arial', 12), fg='red')
        self.lbl_respuesta.place(relx=0.6, rely=0, relwidth=0.4, relheight=1)
        #Incicializar la variable respuesta
        self.respuesta = tk.StringVar()
        self.respuesta.set("RTA.")
        self.lbl_respuesta["textvariable"] = self.respuesta


    """
    def enviar_comando(self):
        comando = self.EntradaComando.get().strip()
        if not comando:
            self.lbl_respuesta.config(text="Sin Respuesta")
            return

        self.arduino.enviar_datos(comando) #* Se puede modificar para enviar el comando más resumido
        # Enviar el comando al Arduino
        #trama = f":1{comando}\r"
        #self.arduino.enviar_datos(trama)

        # Bloquea momentáneamente para recibir la respuesta
        self.after(int(self.tiempo_espera * 1000), self.recibir_respuesta)

    #* Terminar!
    def recibir_respuesta(self):
        respuesta = self.arduino.recibir_datos()
        if respuesta:
            self.lbl_respuesta.config(text=f"Respuesta: {respuesta}")
        else:
            self.lbl_respuesta.config(text="No se recibió respuesta del Arduino.")
    """