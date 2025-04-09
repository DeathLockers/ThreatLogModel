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

from tl_model_server.kafka.consumer import Consumer
from tl_model_server.kafka.producer import Producer
from tl_model_server.models.model_agent import ModelsAgent
from tl_model_server.models.message_types import LogThreats

# Crear clientes kafka para consumir mensajes
consumer = Consumer()

# Crear productor kafka para enviar amenazas
producer = Producer()

# Loads the models inside this component, sends inference task to it
model_agent = ModelsAgent()

model_agent.load_model("model_v1") # Cargar el modelo que queremos usar

# Gestor de guardado de amenazas en la base de datos
log_threats = LogThreats()


async def run():
    """Run the sender in an asynchronous loop"""
    logging.info("Starting sender ...")
    try:
        if log_threats.conn:
            logging.info("Connection to database established")
            while True:
                try:
                    for message in consumer.poll():
                        if message is None:
                            logging.info("Consumer couldn't find any message")
                            continue


                        # Analizar la traza
                        threat = model_agent.inference(message) # Devuelve un dict {"status": 1, "message": message}

                        # Guardar mensaje en amenazas y en logs

                        if threat["status"] == 1:
                            logging.info("Threat detected for message: %s", message)
                            producer.send(message)
                            # Guardar el mensaje en la base de datos
                            log_threats.save_threat(threat["message"])
                            logging.info("Threat message saved to database")
                        else:
                            logging.info("No threat detected for message: %s", message)
                            # Guardar el mensaje en la base de datos
                        log_threats.save_log(message)
                        logging.info("Log message saved to database")

                        # Enviar el mensaje al topic de amenazas
                        producer.send(threat) # Como le enviamos la amenaza a kafka??
                        logging.info("Message sent to Kafka topic")
                except Exception as e:
                    logging.error("Error: %s while processing file messages", e)
                    continue
        else:
            logging.error("Error: No connection to database")
    except Exception as e:
        logging.error("Error initializing sender: %s", e)
    finally:
        logging.info("Sender stopped")
        if log_threats:
            log_threats.close()



if __name__ == "__main__":
    # Thrreads send logs through fluentbit to defined endpoint
    asyncio.run(run())
