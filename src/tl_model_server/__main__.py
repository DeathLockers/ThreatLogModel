import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if not __package__:
    """https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/#running-a-command-line-interface-from-source-with-src-layout"""
    # Make CLI runnable from source tree with
    #    python src/package
    package_source_path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, package_source_path)

# load environment variables from .env file if exists
from dotenv import load_dotenv

load_dotenv()

# Controls parallelism and concurrency of the model server
import asyncio
import json
from tl_model_server.kafka_utils.consumer import Consumer
from tl_model_server.kafka_utils.producer import Producer
from tl_model_server.models.model_agent import ModelsAgent
from tl_model_server.models.message_types import LogThreats

# Crear clientes kafka para consumir mensajes
consumer = Consumer(**{
    "kafka_topic": os.getenv("KAFKA_CONSUMER_TOPIC", "customer_logs")
})

# Crear productor kafka para enviar amenazas
producer = Producer(**{
    "kafka_topic": os.getenv("KAFKA_PRODUCER_TOPIC", "predicted_logs")
})

# Loads the models inside this component, sends inference task to it
model_agent = ModelsAgent("model_v1")

model_agent.load_model("model_v1") # Cargar el modelo que queremos usar

# Gestor de guardado de amenazas en la base de datos
log_threats = LogThreats()


async def run():
    """Run the sender in an asynchronous loop"""
    logging.info("Starting sender ...")
    try:
        while True:
            try:
                for message in consumer.poll():
                    if message is None:
                        logging.info("Consumer couldn't find any message")
                        continue

                    trace = message["trace"]
                    # Analizar la traza
                    prediction_message = model_agent.inference(trace) 
                    # Añadir client_id
                    logging.info("contenido de la prediccion %s", prediction_message)
                    prediction_message["client_id"] = message["client_id"]
                    # Pasar mensaje a json
                    # el producer ya genera los mensajes en formato json
                    # json_prediction = json.dumps(prediction_message)
                    
                    # Enviar el mensaje al topic de amenazas
                    producer.send(prediction_message) 
                    logging.info("Message sent to Kafka topic")
            except Exception as e:
                logging.error("Error: %s while processing file messages", e)
                continue
    except Exception as e:
        logging.error("Error initializing sender: %s", e)
    finally:
        logging.info("Sender stopped")
        if log_threats:
            log_threats.close()



if __name__ == "__main__":
    # Thrreads send logs through fluentbit to defined endpoint
    asyncio.run(run())
