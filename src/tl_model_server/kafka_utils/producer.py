import logging

from kafka import KafkaProducer

from tl_model_server.kafka_utils.config import KafkaConfig


class Producer:
    """Producer is a class that sends messages to a Kafka topic.
    It uses the KafkaProducer from the kafka-python library to send messages.
    The class is initialized with a client_id and optional configuration parameters.
    https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html
    Kafka parameters are readed from environment variables.
    """

    initialized = False
    producer = None

    def __init__(self, **kwargs):
        self.topic = kwargs["kafka_topic"] if "kafka_topic" in kwargs else "predicted_logs"
        self.kafka_config = KafkaConfig()
        if isinstance(kwargs, dict) or isinstance(kwargs, set):
            if "value_serializer" in kwargs:
                self.kafka_config.set_key("value_serializer", kwargs["value_serializer"])
        self.setup()

    def send(self, message):
        """Send a trace to the Kafka topic.
        Args:
            trace (str): The trace to send.
        """
        logging.debug("Sending trace to Kafka topic %s: %s", self.topic, message)

        if not self.initialized:
            raise ValueError("Kafka producer is not initialized. Call setup() before sending messages.")

        self.producer.send(self.topic, message)

    def setup(self):
        """Setup the Kafka producer.
        This method initializes the Kafka producer with the configuration parameters."""
        if self.producer is not None:
            return
        logging.info("\tInitializing...... Kafka producer..")
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
