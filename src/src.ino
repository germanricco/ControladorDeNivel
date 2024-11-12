// IMPORTAR LIBRERIAS
#include <arduino.h>
#include <Servo.h>

// CLASES
class SensorUltrasonico {
    private:
        unsigned int Eco;       
        unsigned int Trig;  

        unsigned long intervalo;    //intervalo mínimo de tiempo entre mediciones
        unsigned long tiempo_anterior;
        unsigned long tiempo_actual;

        unsigned int distancia;

        //unsigned long tiempo_inicio_estado;

        bool mensajeEnviado;    //booleano para evitar envios repetidos innecesarios

    public:
        SensorUltrasonico(unsigned int echo_pin, unsigned int trig_pin);
        bool actualizar(unsigned long periodo_muestreo);
        unsigned int medirDistancia();
};

//Constructor de sensor ultrasonico
SensorUltrasonico::SensorUltrasonico(unsigned int eco_pin, unsigned int trig_pin) {
    Eco = eco_pin;
    Trig = trig_pin;
    tiempo_anterior = 0;
    distancia = 0;
    intervalo = 1000;   //predeterminado 1s.
    mensajeEnviado = false;

    pinMode(Eco, INPUT);
    pinMode(Trig, OUTPUT);
}

//Método que verifica si debe o nó realizar la medición en función de frecuencia de muestreo. Si la realiza devuelve True
bool SensorUltrasonico::actualizar(unsigned long periodo_muestreo){
    intervalo = periodo_muestreo;
    tiempo_actual = millis();
    if (tiempo_actual - tiempo_anterior >= intervalo){
        tiempo_anterior = tiempo_actual;
        return true;  //medicion realizada
    }
    return false;
}

//Método que mide y devuelve la distancia en cm.
unsigned int SensorUltrasonico::medirDistancia(){
    //Devuelve distancia medida
    digitalWrite(Trig, HIGH);
    delay(1);
    digitalWrite(Trig, LOW);
    unsigned int duracion = pulseIn(Eco, HIGH); // devuelve tiempo en us

    // calcular distancia
    distancia = duracion / 58.2;
    return distancia;
}

class Led{
    private:
        int pin;
        bool estado; //true = encendido, false = apagado
    public:
        Led(unsigned int _pin);
        void alternar();
        void titilar(int delayTime = 250);
};

//Constructor de Led
Led::Led(unsigned int _pin){
  pin = _pin;
  estado = false;
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
}

void Led::alternar(){
  estado != estado;
  digitalWrite(pin, estado ? HIGH : LOW);
}

void Led::titilar(int delayTime){
  for (int i = 0; i < 2; i++) {
    digitalWrite(pin, HIGH);
    delay(delayTime);
    digitalWrite(pin, LOW);
    delay(delayTime);
  }
}


// CONSTANTES Y VARIABLES GLOBALES
const uint8_t MI_DIRECCION = 1;
const unsigned int TRIG_PIN = 10;       //Pin Trigger de sensor ultrasonico
const unsigned int ECO_PIN = 11;        //Pin Echo de sensor ultrasonico
const unsigned int LED1_PIN = 12;
const unsigned long TIMEOUT_MS = 1000;  //Tiempo máximo para recibir la trama



// PINES PARA LOS LEDS
int leds[]={2,3,4,5,6,7};
//PIN PARA LA BOMBA
int bomba=9;
//AUXILIARES
bool modo_manual = false; // Inicialmente en automático
int porcentaje;



unsigned long periodo_muestreo = 200;   //Tiempo para tomar una nueva medicion de distancia

int inicio = 1;                       //VD. modificable. controla inicio de programa.
unsigned int distancia_anterior = 0;
unsigned int distancia_actual = 0;    //VA. pedible. contiene ultima distancia medida
unsigned float umbral_inf = 15;         //VD. modificable
unsigned float umbral_sup = 60;         //VD. modificable
unsigned int cont_inf = 0;            //VD. pedible. almacena las veces que se supera el lim. inferior
unsigned int cont_sup = 0;            //VD. pedible. almacena las veces que se supera el lim. superior

unsigned int margen_histeresis = 1;   //VD. modificable. margen de histeresis para evitar incrementos multiples debido a pequeñas oscilaciones.

String trama_recibida = "";   //Trama recibida en string normal
String parametro;             //Parametro recibido
String valor_consigna;        //Valor que se debera asignar al parametro

float incremento=(umbral_sup-umbral_inf)/6;

//FUNCIONES AUXILIARES

bool recibir_mensaje(){
  trama_recibida = "";
  unsigned long start_time = millis();

  //retraso para asegurar que la trama llegue completa antes de procesarla
  delay(20);

  //leer todos los caracteres disponibles en el puerto serial
  while (Serial.available() > 0 && (millis() - start_time) < TIMEOUT_MS){
      char c = Serial.read();
      trama_recibida += c;
  }

  trama_recibida.trim(); //eliminar espacios y saltos de linea
  
  //verificar si la trama comienza con ':' y termina con \r
  if (trama_recibida.startsWith(":")){
    //verificar si la direccion es correcta
    if (trama_recibida[1] == (MI_DIRECCION) + '0' || trama_recibida[1] == "00"){
      return true;
    }else{
      Serial.println("Este mensaje no es para mi.");
      return false;
    }
  }else{
    Serial.println("La trama recibida no comienza con ':'.");
    return false;
  }
}

bool identificar_tipo_mensaje(String& parametro, String& valor_consigna){
  //obtiene el primer valor sin importar el tipo de mensaje
  parametro = trama_recibida[2];

  //Una solicitud tiene máx 4 caracteres (por ej. ':1CI'). Si tiene 5 o más es consigna
  if (trama_recibida.length() >= 5){
    //actualizo valor_consigna tomando desde el 3 elemento hasta el ultimo
    valor_consigna = trama_recibida.substring(3, trama_recibida.length());
    return true;
  }else{
    if (trama_recibida.length()==4){
      parametro += trama_recibida[3];
    }
    return false;
  }
}

void procesar_solicitud(String parametro){
  //Eliminar caracteres invisibles
  parametro.trim();

  //distancia
  if (parametro == "D"){
    respuesta_solicitud(parametro, distancia_actual);
  }
  //contadores
  else if(parametro == "CI"){
    respuesta_solicitud(parametro, cont_inf);
  }else if(parametro == "CS"){
    respuesta_solicitud(parametro, cont_sup);
  }
  //umbrales
  else if(parametro == "UI"){
    respuesta_solicitud(parametro,  umbral_inf);
  }else if(parametro == "US"){
    respuesta_solicitud(parametro, umbral_sup);
  }else{
    Serial.println("Parametro desconocido en solicitud.");
  }
}

void respuesta_solicitud(String parametro, int valor) {
    //Formatear el mensaje de respuesta como una cadena concatenando:
    String respuesta = ":";
    respuesta += String(MI_DIRECCION);
    respuesta += parametro;
    respuesta += String(valor);
    respuesta += '\r';

    //Serial.print("Enviando respuesta: ");
    Serial.println(respuesta);
}

void procesar_consigna(String parametro, String valor_consigna){
  //Eliminar caracteres invisibles
  parametro.trim();
  valor_consigna.trim();

  //Convertir String valor_consigna a entero
  int valor_numerico = valor_consigna.toInt();

  //Procesar el parametro y actualizar variable correspondiente
  if (parametro == "I"){
    umbral_inf = valor_numerico;
    Serial.println("Valor de umbral inferior modificado");
    respuesta_consigna(parametro, valor_consigna);
  }else if (parametro == "S"){
    umbral_sup = valor_numerico;
    Serial.println("Valor de umbral superior modificado");
    respuesta_consigna(parametro, valor_consigna);
  }else if (parametro == "H"){
    margen_histeresis = valor_numerico;
    respuesta_consigna(parametro, valor_consigna);
  }
  else{
    Serial.println("Parametro desconocido en consigna.");
  }
}

void respuesta_consigna(String parametro, String valor_consigna){
  String respuesta = "";
  respuesta += ":";
  respuesta += String(MI_DIRECCION);
  respuesta += parametro;
  respuesta += String(valor_consigna);
  respuesta += '\r';

  Serial.println(respuesta);
}

void indicador_nivel(){

  if(distancia>umbral_sup){                          //distancia maxima , apaga los LEDs
    for(int k=0;k<=5;k++){ 
      digitalWrite(leds[k],LOW);
      }
  } 
  else if(distancia>(umbral_inf+incremento*5)){                   // primer nivel encender LED 1.
    digitalWrite(leds[0], HIGH);
    for(int k=1;k<=5;k++){ 
      digitalWrite(leds[k],LOW);
    }
  } 
  else if(distancia>(umbral_inf+incremento*4)){                     // 2do nivel encender LED 2 y asi con los demas LED etc...
    for(int k=0;k<=1;k++){ 
      digitalWrite(leds[k],HIGH);} 
    for(int k=2;k<=5;k++) 
    {digitalWrite(leds[k],LOW);}
   } 
  else if(distancia>(umbral_inf+incremento*3)){                   //3er LED
    for(int k=0;k<=2;k++){ 
      digitalWrite(leds[k],HIGH);} 
    for(int k=3;k<=5;k++){ 
      digitalWrite(leds[k],LOW);}
   } 
  else if(distancia>(umbral_inf+incremento*2)){                     //4to LED
    for(int k=0;k<=3;k++){
      digitalWrite(leds[k],HIGH);} 
    for(int k=4;k<=5;k++){ 
      digitalWrite(leds[k],LOW);}
   } 
  else if(distancia>(umbral_inf+incremento)){                    //5to LED
    for(int k=0;k<=4;k++){ 
      digitalWrite(leds[k],HIGH);} 
    digitalWrite(leds[5],LOW);
   } 
  else if(distancia>umbral_inf){                      //6to LED
    for(int k=0;k<=5;k++){ 
      digitalWrite(leds[k],HIGH);} 
   } 
  
}

void bombita(){
  if(!modo_manual){
    if(distancia_actual>umbral_inf){          //CORTA LA SEÑAL DEL RELE
      digitalWrite(bomba, HIGH);
    }
    else{
      digitalWrite(bomba, LOW);
      }
}
}

void leer_comandos() {
    if (Serial.available() > 0) {
        String comando = Serial.readStringUntil('\n');
        comando.trim(); // Elimina espacios en blanco

        if (comando == "ON") {
            digitalWrite(bomba, HIGH);
            modo_manual = true; // Cambia a modo manual
        } else if (comando == "OFF") {
            digitalWrite(bomba, LOW);
            modo_manual = true; // Cambia a modo manual
        } else if (comando == "AUTO") {
            modo_manual = false; // Cambia a modo automático
        }
    }
}


// CONSTRUIR OBJETOS
SensorUltrasonico sensorDistancia(ECO_PIN, TRIG_PIN);
Led led_azul(LED1_PIN);

// PROGRAMA PRINCIPAL
void setup(){
    Serial.begin(9600);

    //Salidas para los leds
    for(int pin=2;pin<=7;pin++)
      pinMode(pin,OUTPUT);

    //SALIDA PARA EL RELÉ QUE ACTIVA LA BOMBA
    pinMode(bomba, OUTPUT);
}   

void loop(){
  while(inicio == 1){
    //Verificar si hay algo en el puerto serial
    if (Serial.available() > 0){
      //Verificar que el mensaje sea válido
      if(recibir_mensaje()){
        //Verificar tipo de mensaje
        bool es_consigna = identificar_tipo_mensaje(parametro, valor_consigna);
        if (es_consigna){
          //procesar consigna numerica
          procesar_consigna(parametro, valor_consigna);
        }else{
          //procesar solicitud
          procesar_solicitud(parametro);
        }
      }else{
        Serial.println("Trama no valida.");
      }
    }

    //Si el tiempo es mayor al periodo de muestreo
    if (sensorDistancia.actualizar(periodo_muestreo)){
      distancia_actual = sensorDistancia.medirDistancia();
      //Verificar si cruza umbral inferior
      if (distancia_actual < (umbral_inf - margen_histeresis) && distancia_anterior >= umbral_inf){
        led_azul.titilar(100);
        cont_inf += 1;
        
      //Verificar si cruza umbral superior
      }else if(distancia_actual > (umbral_sup + margen_histeresis) && distancia_anterior < umbral_sup){
        led_azul.titilar(100);
        cont_sup += 1;
        
      }
      porcentaje=map(distancia_actual,umbral_sup,umbral_inf,0,100);
      Serial.print("El tanque está al ");
      Serial.print(porcentaje);
      Serial.print("%");
      Serial.println();
      indicador_nivel();
      bombita();      // AVERGASTON
      leer_comandos();
      
      //Actualiza la distancia
      distancia_anterior = distancia_actual;
    }
  }

}

