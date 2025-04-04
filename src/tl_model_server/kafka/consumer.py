import logging

from kafka import KafkaConsumer
from tl_model_server.kafka.config import KafkaConfig


class Consumer:
    """KafkaSender is a class that sends messages to a Kafka topic.
    It uses the KafkaConsumer from the kafka-python library to send messages.
    The class is initialized with a client_id and optional configuration parameters.
    https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html
    Kafka parameters are readed from environment variables.
    """
    initialized = False
    consumer = None
    def __init__(self, **kwargs):
        """Initialize the Kafka consumer with the given configuration parameters.
        Args:
            **kwargs: Optional configuration parameters for the Kafka consumer.
            log_alert: The Kafka topic to send messages to. Default is 'log_alert'.
        """
        self.kafka_config = KafkaConfig()
        
        self.topics = kwargs['customer_logs'] if 'customer_logs' in kwargs else 'log_alert'

    def get_message(self) -> str:
        """Send a trace to the Kafka topic.
        Args:
            trace (str): The trace to send.
        """
        logging.info(f"Sending trace to Kafka topic {self.topics}")
        if not self.initialized:
            raise ValueError("Kafka consumer is not initialized. Call setup() before sending messages.")
        
        record = self.consumer.poll(max_records=1)

        if not record:
            logging.info("No records found")
            return None
        
        for topic_partition, messages in record.items():
            for message in messages:
                logging.info(f"Received message: {message.value}")
                yield message.value.decode('utf-8')

    def setup(self):
        """Setup the Kafka consumer.
        This method initializes the Kafka consumer with the configuration parameters."""
        if self.consumer is not None:
            return
        logging.info("Kafka consumer is not initialized. Initializing...")
        self.consumer = KafkaConsumer(**self.kafka_config.args)
        self.initialized = True

    def stop(self):
        """Stop the Kafka consumer.
        This method flushes and closes the Kafka consumer."""
        if self.consumer is None:
            return
        logging.info("Stopping Kafka consumer...")
        self.consumer.flush()
        self.consumer.close()
        self.consumer = None
