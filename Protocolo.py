
class Protocolo:
    
    # Funcion para crear la trama de solicitud completa
    @staticmethod
    def crear_trama_solicitud(direccion, parametro):
        # Formatear la trama según el protocolo de solicitud
        trama = f":{direccion}{parametro}\r"
        return trama

    # Funcion para crear la trama de consigna completa
    @staticmethod
    def crear_trama_consigna(direccion, parametro, valor):
        # Formatear la trama según el protocolo de consigna
        trama = f":{direccion}{parametro}{valor}\r"
        return trama

    def verificar_trama(trama, direccion, parametro):
        """
        Verifica si la trama recibida es válida.
        - `trama`: la trama recibida.
        - `direccion`: dirección esperada.
        - `parametro`: parámetro solicitado.

        Retorna True si la trama es válida, False en caso contrario.
        """
        
        inicio = ':'
        fin = '\r'

        # Verificar que la trama comience con ':' y termine con '\r'
        if not trama.startswith(inicio):
            print("Error: Trama no comienza con ':'. ")
            return False

        # Verificar que la dirección en la trama sea la misma que la esperada
        if trama[1] != str(direccion):
            print(f"Error: Dirección incorrecta en la trama. Esperado: {direccion}, Recibido: {trama[1]}")
            return False

        # Verificar que el parámetro en la trama sea el mismo que el esperado
        if trama[2:2+len(parametro)] != parametro:
            print(f"Error: Parámetro incorrecto en la trama. Esperado: {parametro}, Recibido: {trama[2]}")
            return False

        # Verificar que la parte del valor sea numérica
        valor_str = trama[2+len(parametro):len(trama)]  # Extrae el valor

        if not valor_str.isdigit():
            print(f"Error: Valor no numérico en la trama. Recibido: {valor_str}")
            return False

        # Si pasa todas las verificaciones, la trama es válida
        return True