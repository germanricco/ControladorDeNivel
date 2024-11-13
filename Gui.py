import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MonitorGUI(tk.Tk):
    #Constructor para inicializar la clase
    def __init__(self, arduino, enviar_comandos, lista_mediciones, lista_umbral_inferior, lista_umbral_superior):
        super().__init__() # Llama al constructor de la clase base (tk.Tk)

        # Parámetros para actualizar valores
        self.arduino = arduino
        self.enviar_comandos = enviar_comandos
        self.lista_mediciones = lista_mediciones
        self.lista_umbral_inferior = lista_umbral_inferior
        self.lista_umbral_superior = lista_umbral_superior

        self.id_actualizar_grafico = None  # ID para la tarea programada

        # Configuracion de la ventana principal
        self.title("Monitor Arduino - Nivel de Tanque")
        self.geometry("800x600")

        # -- FRAME SUPERIOR --
        self.frame1 = tk.Frame(self, bg="gray")
        self.frame1.pack(side="top", fill="both", expand=True)

        #Frame para la gráfica
        self.frameGrafica = tk.Frame(self, bg="white")
        self.frameGrafica.place(relx=0.3, rely=0, relwidth=0.7, relheight=0.8)

        #Inicializar el grafico
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.ax.set_title("Distancia en función del tiempo")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Distancia (cm)")
        self.grafico = FigureCanvasTkAgg(self.fig, master=self.frameGrafica)
        self.grafico.get_tk_widget().pack(fill='both', expand=True)

        self.actualizar_grafico()

        #Frame Variables
        self.frameVariables = tk.Frame(self, bg="darkgray")
        self.frameVariables.place(relx=0, rely=0, relwidth=0.3, relheight=1)
        
        #Título de Frame Variables
        self.lblVariables = tk.Label(self.frameVariables,
                                     text="Variables",
                                     bg='lightgreen',
                                     font=('times', 24))
        self.lblVariables.pack(pady=10)

        #Label variable de Distancia
        self.lbl_distancia = tk.Label(self.frameVariables)
        self.lbl_distancia.pack(pady=5)
        #Incicializar la variable
        self.distancia = tk.StringVar()
        self.distancia.set("Cargando")
        self.lbl_distancia["textvariable"] = self.distancia

        #Label variable porcentaje
        self.lbl_porcentaje = tk.Label(self.frameVariables)
        self.lbl_porcentaje.pack(pady=5)
        #Inicializar la variable
        self.porcentaje = tk.StringVar()
        self.porcentaje.set("Cargando")
        self.lbl_porcentaje["textvariable"] = self.porcentaje

        #Label variable contador inf
        self.lbl_contador_inf = tk.Label(self.frameVariables)
        self.lbl_contador_inf.pack(pady=5)
        #Incicializar la variable
        self.contador_inf = tk.StringVar()
        self.contador_inf.set("Cargando")
        self.lbl_contador_inf["textvariable"] = self.contador_inf

        #Label variable contador sup
        self.lbl_contador_sup = tk.Label(self.frameVariables)
        self.lbl_contador_sup.pack(pady=5)
        #Incicializar la variable
        self.contador_sup = tk.StringVar()
        self.contador_sup.set("Cargando")
        self.lbl_contador_sup["textvariable"] = self.contador_sup

        #Título de Frame Parámetros
        self.lblParametros = tk.Label(self.frameVariables,
                                      text="Parámetros",
                                      bg='lightblue',
                                      font=('times', 24))
        self.lblParametros.pack(pady=10)

        #Label parametro umbral inferior
        self.lbl_umbral_inf = tk.Label(self.frameVariables)
        self.lbl_umbral_inf.pack(pady=5)
        #Incicializar la variable umbral_inferior
        self.umbral_inf = tk.StringVar()
        self.umbral_inf.set("Cargando")
        self.lbl_umbral_inf["textvariable"] = self.umbral_inf

        #Label parametro umbral superior
        self.lbl_umbral_sup = tk.Label(self.frameVariables)
        self.lbl_umbral_sup.pack(pady=5)
        #Incicializar la variable umbral_superior
        self.umbral_sup = tk.StringVar()
        self.umbral_sup.set("Cargando")
        self.lbl_umbral_sup["textvariable"] = self.umbral_sup

        #Label parametro margen_histeresis
        self.lbl_margen_hist = tk.Label(self.frameVariables)
        self.lbl_margen_hist.pack(pady=5)
        #Inicializar la variable margen_histeresis
        self.margen_hist = tk.StringVar()
        self.margen_hist.set("Cargando")
        self.lbl_margen_hist["textvariable"] = self.margen_hist


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

    def actualizar_grafico(self):
        """
        Actualiza el gráfico con los valores de lista_mediciones.
        """
        self.ax.clear()  # Limpia el gráfico anterior

        #Grafica de distancia
        self.ax.plot(self.lista_mediciones, marker="o", linestyle="-", color="b")  # Redibuja el gráfico
        self.ax.set_title("Distancia en función del tiempo")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Distancia (cm)")

        #Grafica de umbral inferior
        self.ax.plot(self.lista_umbral_inferior, linestyle="--", color="r", label="Umbral Inferior")

        #Grafica de umbral superior
        self.ax.plot(self.lista_umbral_superior, linestyle="--", color="g", label="Umbral Superior")

        # Configuracion de leyenda
        self.ax.legend(loc="upper right")
        self.ax.set_title("Distancia en función del tiempo")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Distancia (cm)")

        #Redibuja
        self.grafico.draw()

        # Guarda el ID de la proxima llamada, actualiza el gráfico cada 1s
        self.id_actualizar_grafico = self.after(1000, self.actualizar_grafico)