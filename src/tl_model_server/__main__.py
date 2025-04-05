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

# Crear clientes kafka para consumir mensajes
consumer = Consumer()

# Crear productor kafka para enviar amenazas
producer = Producer()


# Loads the models inside this component, sends inference task to it
model_agent = ModelsAgent()


def inference(consume_task) -> asyncio.Future:
    """Procesa el mensaje, asigna el trabajo al modelo disponible y del tipo adecuado"""
    if consume_task.done():
        return asyncio.create_task(model_agent.inference(consume_task.message))
    else:
        # TODO: Revisar que ha pasado, como recuperamos el error
        logging.error("Error: Algo fue mal con el mensaje de entrada %s", consume_task)
        return asyncio.create_task(consumer.get_message())


def prdocue_message(inference_task) -> asyncio.Future:
    """Produce el mensaje de salida del modelo al topic correspondiente"""
    if inference_task.done():
        return asyncio.create_task(producer.send(inference_task.message))
    else:
        # TODO: Revisar que ha pasado, como recuperamos el error
        logging.error("Error: Algo fue mal con el mensaje de entrada %s", inference_task)
        return asyncio.create_task(consumer.get_message())


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

                    threat = model_agent.inference(message)
                    if threat is None:
                        logging.info("Model couldn't find any threat for messages:")
                        logging.info(message)
                        continue

                    producer.send(threat)
                # Limpiar tareas completadas
            except Exception as e:
                logging.error("Error: %s while processing file messages", e)
                continue
    except Exception as e:
        logging.error("Error initializing sender: %s", e)


if __name__ == "__main__":
    # Thrreads send logs through fluentbit to defined endpoint
    asyncio.run(run())
