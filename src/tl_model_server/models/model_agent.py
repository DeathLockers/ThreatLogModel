import asyncio
import enum
import logging
import random
import struct
import socket
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from sklearn.pipeline import Pipeline


class ModelResults(enum.Enum):
    """Enum for model results"""
    THREAT = 2
    NO_THREAT = 1


class ModelsAgent:
    """Agent que carrega els models de disc
    Segons el tipus de missatge, el model a executar l'algorisme será diferent
    Aquest agent també serveix per entrenar els models"""

    def __init__(self):
        """Cargamos la infromación del modelo que queremos cargar"""
        self.pipeline = joblib.load('pipeline.joblib')
        self.model = self.pipeline['model']
        self.scaler = self.pipeline['scaler']
        self.label_encoder_message = self.pipeline['label_encoder_message']
        self.label_encoder_service = self.pipeline['label_encoder_service']


    def inference(self, message=None) -> dict:
        """Procesa el mensaje, asigna el trabajo al modelo disponible y del tipo adecuado
        Si localiza una amenaza, envía una alerta de amenaza detectada mediante el productor
        Args:
            message (str): Mensaje a procesar
        Returns:
            dict: Mensaje procesado, con la respuesta del modelo si es amenaza o no
        """

        logging.info("Processing message: %s", message)
        msg_scaled = self.process_msg()
        prediction = self.model.predict(msg_scaled)
        return {"status": int(prediction[0]), "message": message}

    def process_msg(self, message = None)-> dict:
        # Ejemplo msg: Feb 26 1:06:58	db-server-02	vsftpd	5846	1	Anonymous user from 220.135.151.1 executed: LIST
        """
        Procesa el mensaje para dejarlo en un formato correcto para que lo pueda consumir 
        el modelo.

        Args:
            message (str): Mensaje a procesar
        Returns:
            dict: Mesnaje procesado.
        """

        message = {"timestamp": "Feb 26 1:06:58", "host": "db-server-02", "service": "vsftpd", "pid": 5846, "message": "Anonymous user from 220.135.151.1 executed: LIST"}
        # previous_timestamp = ""

        try:
            if (message["host"].startswith("ip-")):
                # Convertir IP a formato numero
                ip = message["host"].split('-')[-4:]
                ip = '.'.join(ip)  # Convertir a formato estándar de IP
                message["host"] = int(struct.unpack("!I", socket.inet_aton(ip))[0]) # Añadir numero anonimizado de ip

            else:
                message['host'] = hash(message["host"])  # Utilizar 'hash' para asignar un número único a cada servidor

            # Extraer componentes de fecha y hora
            timestamp_str = message["timestamp"]
            timestamp_format = "%b %d %H:%M:%S"  # El formato es 'Mes Día Hora:Minuto:Segundo'
            timestamp = datetime.strptime(timestamp_str, timestamp_format)
            # Añadir columnas
            message["day_of_week"] = timestamp.weekday() + 1 # Del 1 al 7
            message["day"] = timestamp.day
            message["month"] = timestamp.month
            message["hour"] = timestamp.hour
            message["minute"] = timestamp.minute
            message["second"] = timestamp.second

            # Usar label encoder para las columnas categoricas
            label_encoder_message = LabelEncoder()
            label_encoder_service = LabelEncoder()
            msg = [message["message"]]
            service = [message["service"]]
            message['message'] = int(self.label_encoder_message.transform(msg)[0])
            message['service'] = int(self.label_encoder_service.transform(service)[0])

            # Escalamos los datos
            del message["timestamp"]
            msg_scaled = self.scaler.transform([list(message.values())])

            return msg_scaled

        except Exception as e:
            print(f"Error processing message {message["host"]}: {e}")
            return None  # En caso de error, devolver None

    def train(self, name):
        """Carga un modelo y lo entrena con los datos de la base de datos"""
        logging.info("Training model: %s", name)
        # Aquí puedes añadir el código para cargar y entrenar el modelo
        # Por ejemplo, cargar datos de la base de datos y entrenar un modelo
        # Puedes usar pandas para cargar los datos y sklearn para entrenar el modelo
        # Guarda el modelo entrenado en disco
        return {"status": 1, "message": "Model trained successfully"}

    def default_model(self, data=None):
    """
    Entrena y guarda un modelo por defecto en el caso de que no haya ninguno con el csv de logs
    Args:
        
    """
    try:
        logging.info("Training model: %s with data: %s", model_name, data)

        # Cargar los datos
        df = pd.read_csv("./train_logs.csv")

        # Label encoding para las columnas 'message' y 'service'
        self.label_encoder_message.fit(df["message"])
        df["message"] = self.label_encoder_message.fit_transform(df["message"])

        self.label_encoder_service.fit(df["service"])
        df["service"] = self.label_encoder_service.fit_transform(df["service"])

        # Separar las características y la variable objetivo
        y = df['target']
        x = df.drop(['target', 'time_delta'], axis=1)

        # División del conjunto de datos en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

        # Normalización de los datos
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Crear y entrenar el clasificador
        classifier = DecisionTreeClassifier(random_state=42)
        classifier.fit(X_train_scaled, y_train)

        # Guardamos todo el pipeline y los encoders
        joblib.dump({
            'model': classifier,
            'scaler': scaler,
            'label_encoder_message': self.label_encoder_message,
            'label_encoder_service': self.label_encoder_service
        }, 'pipeline.joblib')

        # Realizar predicciones
        predicciones = classifier.predict(X_test_scaled)

        # Calcular las métricas de rendimiento
        accuracy = accuracy_score(y_test, predicciones)
        precision = precision_score(y_test, predicciones, average='weighted')

        return accuracy, precision

    except Exception as e:
        logging.error("Error: No ha funcionado la creación de un modelo por defecto.")
        return {"error": f"Default model not created: {str(e)}"}