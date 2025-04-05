import asyncio
import logging
from typing import Any

from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord

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
        self.kafka_config = KafkaConfig(mode="consumer")

        self.topic = kwargs["kafka_topic"] if "kafka_topic" in kwargs else "customer_logs"
        self.setup()

    def poll(self) -> dict[str, Any]:
        """Send a trace to the Kafka topic.
        Args:
            trace (str): The trace to send.
        """
        logging.info("Sending trace to Kafka topic %s", self.topic)
        if not self.initialized:
            raise ValueError("Kafka consumer is not initialized. Call setup() before sending messages.")

        for message in self.consumer:
            yield message.value

    def setup(self):
        """Setup the Kafka consumer.
        This method initializes the Kafka consumer with the configuration parameters."""
        if self.consumer is not None:
            return
        logging.info("Kafka conbsumer is not initialized")
        logging.info("\tInitializing...... Kafka consumer is not initialized..")
        self.consumer = KafkaConsumer(self.topic, **self.kafka_config.args)
        # self.consumer.subscribe([self.topic])
        logging.info("Kafka consumer initialized with topic: %s", self.topic)
        logging.info("Subscribed topics: %s", self.consumer.subscription())
        logging.info("Partitions for topic %s: %s", self.topic, self.consumer.partitions_for_topic(self.topic))
        logging.info("Partitions assigned to the consumer: %s", self.consumer.assignment())
        
        
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
