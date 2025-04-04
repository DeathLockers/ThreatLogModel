import asyncio
import logging
import os
from tl_model_server.kafka.consumer import Consumer
from tl_model_server.kafka.producer import Producer

class KafkaAgent:
    """
    Agente encargado de enviar y recibir mensajes a través de Kafka.
    Este agente procesará los mensajes de un archivo los analizará y enviará al servicio local encargado de procesar los mensajes.
    """
    def __init__(self, config):
        self.file = config['runner']['filePath']
        if not self.file:
            raise ValueError("File path is required")
        
        if not os.path.exists(self.file):
            raise ValueError(f"File {self.file} does not exist")
        
        self.interval = config['runner']['interval']
        self.client_id = config['client_id']
        self.consumer = Consumer()
        self.producer = Producer()
        self.running = True

    async def run(self):
        """Run the sender in an asynchronous loop"""
        logging.info(f"Starting sender {self.client_id}...")
        try:
            self.consumer.setup()
            self.producer.setup()
            while self.running:
                try:
                    message = await self.consumer.get_message()
                    await asyncio.sleep(self.interval)
                    if not self.running:
                        break
                except Exception as e:
                    logging.error(f"Error: {str(e)} while processing file messages", e)
                    continue
                await asyncio.sleep(self.interval*10)
            try:
                self.consumer.stop()
                self.producer.stop()
            except Exception as e:
                logging.error(f"Error stopping consumer/producer: {e}", e)
        except Exception as e:
            logging.error(f"Error initializing sender: {e}", e)

    def stop(self):
        """Stop the sender gracefully"""
        logging.info(f"Stopping sender {self.client_id}...")
        self.running = False

    @staticmethod
    def build():
        """Create a sender runner"""
        logging.info(f"Creating Agent runner")

        return KafkaAgent({
            'runner':{
                'interval': int(os.getenv('RUNNER_INTERVAL_SECONDS', 5))
                }
            }
        )