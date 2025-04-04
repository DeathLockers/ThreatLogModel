
import os
import sys

from tl_model_server.agents.model_agent import ModelsAgent

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
import logging

# https://docs.python.org/3/library/asyncio-task.html#asyncio.Semaphore
semaphore = asyncio.Semaphore(os.getenv("MAX_CONCURRENT_TASKS", 3))

from tl_model_server.kafka.consumer import Consumer
from tl_model_server.kafka.producer import Producer
from tl_model_server.models import load_models

# Crear clientes kafka para consumir mensajes
consumers = [Consumer() for _ in range(1, 3)]

# Crear productor kafka para enviar amenazas
producer = Producer()



# Loads the models inside this component, sends inference task to it
model_agent = ModelsAgent()

# Crear 

for consumer in consumers:
    consumer.setup()

def inference(consume_task) -> asyncio.Future:
    """Procesa el mensaje, asigna el trabajo al modelo disponible y del tipo adecuado
    """
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
    logging.info(f"Starting sender {producer.client_id}...")
    try:
        tasks = [consumer.get_message()]
        while True:
            try:
                done, futures = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for message in done:
                    if message.type == "consumer":
                        futures.append(inference(message))
                    elif message.type == "ModelsAgent":
                        # Enviar mensaje a kafka
                        futures.append(prdocue_message(message))
                    elif message.type == "producer":
                        # Seguir escucahndo mensajes
                        futures.append(consumer.get_message())
                # Limpiar tareas completadas
                tasks = list(futures)
            except Exception as e:
                logging.error(f"Error: {str(e)} while processing file messages", e)
                continue
    except Exception as e:
        logging.error(f"Error initializing sender: {e}", e)

if __name__ == "__main__":

    # Thrreads send logs through fluentbit to defined endpoint
    asyncio.run(run())