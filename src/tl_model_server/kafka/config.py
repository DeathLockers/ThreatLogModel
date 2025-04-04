import json
import os


class KafkaConfig:
    """KafkaConfig is a class that holds the configuration parameters for the Kafka producer.
    It reads the parameters from environment variables.
    The class is initialized with the following parameters extracted from os environment variables:
    - bootstrap_servers: The Kafka broker address. KAFK_HOST
    - acks: The number of acknowledgments the producer requires the leader to have received before considering a request complete. KAFKA_ACKS
        - 1 means the leader will write the record to its local log but will respond without awaiting full acknowledgement from all followers.
        - 0 means the leader will not wait for any acknowledgment from the broker.
        - -1 means the leader will block until all in-sync replicas have acknowledged the record.
    - value_serializer: The serializer for the value of the message. Default is json.dumps.
    - security_protocol: The protocol used to communicate with the broker. Default is PLAINTEXT.
    - sasl_plain_username: The username for SASL authentication. KAFFKA_USER
    - sasl_plain_password: The password for SASL authentication. KAFFKA_PASSWORD
    """
    args = {}
    KOWN_SECURITY_PROTOCOLS = ['PLAINTEXT', 'SASL_SSL']

    def __init__(self):
        self.set_key('bootstrap_servers', self._get('KAFKA_HOST', raise_if_missing=True))
        self.set_key('acks', self._get('KAFKA_ACKS', 1))
        self.set_key('client_id', self._get('KAFKA_MODEL_CLIENT', 'model_alerts'))
        self.set_key('value_serializer', lambda v: json.dumps(v).encode('utf-8'))
        security_protocol = self._get('security_protocol', 'PLAINTEXT')
        if security_protocol:
            security_protocol = security_protocol.upper()
            if security_protocol not in self.KOWN_SECURITY_PROTOCOLS:
                raise ValueError(f"Invalid security protocol: {security_protocol}. Must be one of {self.KOWN_SECURITY_PROTOCOLS}")

            self.set_key('security_protocol', security_protocol)
            if security_protocol == 'SASL_SSL':
                self.set_key('sasl_plain_username', self._get('KAFFKA_USER'))
                self.set_key('sasl_plain_password', self._get('KAFFKA_PASSWORD'))
                self.user = self._get('KAFFKA_PASSWORD')

    def set_key(self, key, value):
        """Set a key-value pair in the configuration dictionary.
        If the value is None, raise a ValueError."""
        if value:
            self.args[key] = value

    def _get(self, key, default = None, raise_if_missing=False):
        """Get the value of a key from the environment variables."""
        value =  os.environ.get(key, default)
        if raise_if_missing and value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value