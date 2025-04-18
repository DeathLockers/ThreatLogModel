import logging
import os
from pathlib import Path
import joblib
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report

model_zoo = os.environ.get("MODEL_ZOO", "src/tl_model_server/data")

# Cargamos el modelo de embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def process_msg(message: str) -> dict:
    pipeline = load_model("model_v1")
    scaler = pipeline['scaler']
    encoder_service = pipeline['encoder_service']
    original_message = message
    logging.info("Procesando el siguiente mensaje --------> %s",message)
    parts = message.strip().split(",")
    message = {
        "timestamp": parts[0],
        "host": parts[1],
        "service": parts[2],
        "pid": parts[3],
        "message": parts[4]
    }



    try:
        message['host'] = hash(message["host"])

        timestamp_str = message["timestamp"]
        timestamp = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
        message["day_of_week"] = timestamp.weekday() + 1
        message["day"] = timestamp.day
        message["month"] = timestamp.month
        message["hour"] = timestamp.hour
        message["minute"] = timestamp.minute
        message["second"] = timestamp.second

        # Service encoding
        service_encoded = encoder_service.transform([[message["service"]]])[0]

        # Embedding del mensaje
        message_embedding = embedding_model.encode(message["message"])

        # Construimos el vector final
        input_vector = np.concatenate([
            [message['host']],
            service_encoded,
            [message["pid"]],
            [message["day_of_week"], message["day"], message["month"],
             message["hour"], message["minute"], message["second"]],
            message_embedding  # embedding de 384 dimensiones
        ])

        # Escalado
        input_scaled = scaler.transform([input_vector])

        return {
            "message": input_scaled[0],
            "original_message": original_message
        }

    except Exception as e:
        logging.error("Error processing message %s: %s", message["host"], str(e), e)
        raise


def train(model_name, data_path):
    logging.info("Training model: %s with data in %s", model_name, data_path)

    df = pd.read_csv(get_data_path(model_name, data_path))

    encoder_service = OrdinalEncoder()
    scaler = StandardScaler()

    df["host"] = df["host"].apply(lambda x: hash(x))
    df["pid"] = df["pid"].astype(int)

    # Codificamos el servicio
    df[["service"]] = encoder_service.fit_transform(df[["service"]])

    # Embeddings del mensaje
    embeddings = embedding_model.encode(df["message"].tolist())
    embeddings_df = pd.DataFrame(embeddings, columns=[f"emb_{i}" for i in range(embeddings.shape[1])])

    # Unimos al resto del dataset
    x = pd.concat([df.drop(["message", "target", "time_delta"], axis=1).reset_index(drop=True), embeddings_df], axis=1)
    y = df["target"]

    print("Distribución de clases:")
    print(y.value_counts(normalize=True))  # porcentaje

    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print(X_train_scaled.shape)

    classifier = DecisionTreeClassifier(    random_state=42,
    class_weight='balanced',
    max_depth=10,  # Limitar la profundidad máxima
    min_samples_split=10,  # Número mínimo de muestras para dividir un nodo
    min_samples_leaf=5  # Número mínimo de muestras por hoja)
    )
    classifier.fit(X_train_scaled, y_train)

    joblib.dump({
        'model': classifier,
        'scaler': scaler,
        'encoder_service': encoder_service
    }, get_joblib_path(model_name))

    predictions = classifier.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, average='weighted')

    print(confusion_matrix(y_test, predictions))
    print(classification_report(y_test, predictions))


    return accuracy, precision



def load_model(model_name):
    logging.info("Loading model: %s", model_name)
    model_path = get_joblib_path(model_name)
    return joblib.load(model_path)


def get_joblib_path(model_name: str) -> str:
    script_dir = Path(__file__).resolve().parent.parent.parent
    model_path = script_dir / "data" / model_name / "pipeline.joblib"
    return str(model_path)


def get_data_path(model_name, data_path):
    relative_path = os.path.join(model_zoo, model_name, data_path)
    return os.path.abspath(relative_path)
