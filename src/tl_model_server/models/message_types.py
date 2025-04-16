import mysql.connector
from mysql.connector import Error
import os

class LogThreats:
    """Clase para almacenar los logs de las amenazas, recibe como parámetro el resultado del análisis de los mensajes"""

    def __init__(self):
        # Cargar las variables del archivo .env
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_DATABASE")

        try:
            # Intentar establecer la conexión a la base de datos
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.conn.is_connected():
                print("Conexión a la base de datos exitosa.")
                self.cursor = self.conn.cursor()

        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            self.conn = None

    def save_threat(self, message):
        """Guardar un log en la tabla de amenazas"""
        if self.conn:
            try:
                self.cursor.execute(
                    "INSERT INTO threats (message) VALUES (%s)",  # Tabla threats columna messages
                    (message,)
                )
                self.commit()
                print("Mensaje guardado correctamente.")
            except Error as e:
                print(f"Error al guardar el mensaje: {e}")

    def save_log(self):
        """Guardar un log en la tabla de logs"""
        if self.conn:
            try:
                self.cursor.execute(
                    "INSERT INTO logs (log) VALUES (%s)",  # Tabla logs columna log
                    (self.log,)
                )
                self.commit()
                print("Log guardado correctamente.")
            except Error as e:
                print(f"Error al guardar el log: {e}")

    def commit(self):
        """Confirmar los cambios en la base de datos"""
        if self.conn:
            try:
                self.conn.commit()
            except Error as e:
                print(f"Error al hacer commit: {e}")

    def close(self):
        """Cerrar la conexión con la base de datos"""
        if self.conn:
            try:
                self.conn.close()
                print("Conexión cerrada correctamente.")
            except Error as e:
                print(f"Error al cerrar la conexión: {e}")