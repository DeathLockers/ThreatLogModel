import logging

from kafka import KafkaProducer
from tl_model_server.kafka.config import KafkaConfig


class Producer:
    """Producer is a class that sends messages to a Kafka topic.
    It uses the KafkaProducer from the kafka-python library to send messages.
    The class is initialized with a client_id and optional configuration parameters.
    https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html
    Kafka parameters are readed from environment variables.
    """
    initialized = False
    producer = None
    client_id = None
    def __init__(self, client_id, **kwargs):
        self.topic = 'log_alert'
        self.kafka_config = KafkaConfig()
        self.client_id = client_id
        if isinstance(kwargs, dict) or isinstance(kwargs, set):
            if 'value_serializer' in kwargs:
                self.kafka_config.set_key('value_serializer', kwargs['value_serializer'])


    def send(self, trace:str):
        """Send a trace to the Kafka topic.
        Args:
            trace (str): The trace to send.
        """
        logging.info(f"Sending trace to Kafka topic {self.topic}: {trace}")

        if not self.initialized:
            raise ValueError("Kafka producer is not initialized. Call setup() before sending messages.")
        
        raise NotImplementedError("Añade aquí tu código, cambia los parametros de envió de tramas")
        self.producer.send(self.topic, {
            'trace': trace,
            'client_id': self.client_id
        })

    def setup(self):
        """Setup the Kafka producer.
        This method initializes the Kafka producer with the configuration parameters."""
        if self.producer is not None:
            return
        logging.info("Kafka producer is not initialized. Initializing...")
        self.producer = KafkaProducer(**self.kafka_config.args)
        self.initialized = True

    def stop(self):
        """Stop the Kafka producer.
        This method flushes and closes the Kafka producer."""
        if self.producer is None:
            return
        logging.info("Stopping Kafka producer...")
        self.producer.flush()
        self.producer.close()
        self.producer = None
