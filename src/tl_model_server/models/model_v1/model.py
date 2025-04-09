import logging
import os
import joblib
import pandas as pd
from sklearn.calibration import LabelEncoder
from sklearn.discriminant_analysis import StandardScaler
from sklearn.metrics import precision_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

model_zoo = os.environ.get("MODEL_ZOO", "src/tl_model_server/data")


from datetime import datetime
import hashlib
import logging

label_encoder_message = None
label_encoder_service = None
scaler = None


def process_msg(message = None)-> dict:
    # Ejemplo msg: Feb 26 1:06:58	db-server-02	vsftpd	5846	1	Anonymous user from 220.135.151.1 executed: LIST
    """
    Procesa el mensaje para dejarlo en un formato correcto para que lo pueda consumir 
    el modelo.

    Args:
        message (str): Mensaje a procesar
    Returns:
        dict: Mesnaje procesado.
    """

    # message = {"timestamp": "Feb 26 1:06:58", "host": "db-server-02", "service": "vsftpd", "pid": 5846, "message": "Anonymous user from 220.135.151.1 executed: LIST"}
    # previous_timestamp = ""

    try:
        message['host'] = hashlib.sha256(message["host"].encode()).hexdigest()  # Utilizar 'hash' para asignar un número único a cada servidor

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
        msg = [message["message"]]
        service = [message["service"]]
        message['message'] = int(label_encoder_message.transform(msg)[0])
        message['service'] = int(label_encoder_service.transform(service)[0])

        # Escalamos los datos
        del message["timestamp"]
        msg_scaled = scaler.transform([list(message.values())])

        return msg_scaled

    except Exception as e:
        logging.error("Error processing message %s: %s",message["host"], str(e), e)
        raise

def train(model_name, data_path):
    """
    Entrena y guarda un modelo por defecto en el caso de que no haya ninguno con el csv de logs
    Args:
        
    """
    try:
        logging.info("Training model: %s with data in %s", model_name, data_path)

        # Cargar los datos
        df = pd.read_csv(get_data_path(model_name, data_path))

        label_encoder_message = LabelEncoder()
        label_encoder_service = LabelEncoder()
        scaler = StandardScaler()

        # Label encoding para las columnas 'message' y 'service'
        label_encoder_message.fit(df["message"])
        df["message"] = label_encoder_message.fit_transform(df["message"])

        label_encoder_service.fit(df["service"])
        df["service"] = label_encoder_service.fit_transform(df["service"])

        # Separar las características y la variable objetivo
        y = df['target']
        x = df.drop(['target', 'time_delta'], axis=1)

        # División del conjunto de datos en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

        # Normalización de los datos
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Crear y entrenar el clasificador
        classifier = DecisionTreeClassifier(random_state=42)
        classifier.fit(X_train_scaled, y_train)

        # Guardamos todo el pipeline y los encoders
        joblib.dump({
            'model': classifier,
            'scaler': scaler,
            'label_encoder_message': label_encoder_message,
            'label_encoder_service': label_encoder_service
        }, get_joblib_path(model_name))

        # Realizar predicciones
        predicciones = classifier.predict(X_test_scaled)

        # Calcular las métricas de rendimiento
        accuracy = accuracy_score(y_test, predicciones)
        precision = precision_score(y_test, predicciones, average='weighted')

        return accuracy, precision

    except Exception as e:
        logging.error("Error: No ha funcionado la creación de un modelo por defecto.")
        return {"error": f"Default model not created: {str(e)}"}

def load_model( model_name):
    """Carga el modelo de disco"""
    logging.info("Loading model: %s", f"tl_model_server.models.{model_name}.model")
    model_path = get_joblib_path(model_name)

    # Load the pipeline from the located path
    pipeline = joblib.load(model_path)
    scaler = pipeline['scaler']
    label_encoder_message = pipeline['label_encoder_message']
    label_encoder_service = pipeline['label_encoder_service']
    return pipeline['model']

def get_joblib_path(model_name):
    """Get the path to the joblib file"""
    return os.path.join(model_zoo, model_name, "pipeline.joblib")

def get_data_path(model_name, data_path):
    """Get the path to the data file"""
    relative_path = os.path.join(model_zoo, model_name, data_path)
    absolute_path = os.path.abspath(relative_path)
    return absolute_path