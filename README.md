# Threat Log Model

Aplicacion que procesa trazas, las analiza y las reporta usando uno o varios modelos entrenados.

## Entorno de desarrollo

Prepara el entorno virtual local para instalar los paquetes necesarios.

### Requisitos previos

1. **Instalar Python**:
   - Asegúrate de tener Python instalado en tu sistema. Puedes descargarlo desde la [página oficial de Python](https://www.python.org/downloads/).
   - Durante la instalación, marca la opción **"Add Python to PATH"** para facilitar el uso de Python desde la terminal.

2. **Instalar el módulo `venv`**:
   - El módulo `venv` viene incluido en las versiones modernas de Python (3.3+). Si no está disponible, asegúrate de que tu instalación de Python incluye las herramientas necesarias.
   - En sistemas basados en Linux, puedes instalarlo con:

     ```bash
     sudo apt install python3-venv
     ```

3. **Gestionar múltiples versiones de Python** (opcional):
   - Si necesitas trabajar con diferentes versiones de Python, puedes usar herramientas como:
     - [pyenv](https://github.com/pyenv/pyenv): Una herramienta para instalar y gestionar múltiples versiones de Python.
     - [Anaconda](https://www.anaconda.com/): Una distribución de Python para ciencia de datos que incluye herramientas para gestionar entornos.

### Ejecuta entorno en local

```docker compose -f .\dev\docker-compose.yml up -d```

### Configura vscode

Para ejecutar con F5 el codigo en vscode crea la carpeta .vscode y el archivo como se indica.

```{
    "configurations": [
        {
            "name": "Python Debugger: Module",
            "type": "debugpy",
            "request": "launch",
            "module": "tl_model_server"
        }
    ]
}
```

## Estructura del mensaje `prediction_message`

El mensaje `prediction_message` es un JSON que contiene la información generada por el modelo después de analizar una traza. Su estructura es la siguiente:

```json
{
    "message": "string",          // Log de la amenaza analizada
    "prediction": "double",      // Nivel de amenaza detectado valor de 0 a 1
    "client_id": "string",          // Identificador del cliente asociado al mensaje
    "model": "string"           // Modelo usado para predecir el log

}
```

Asegúrate de que los campos sean consistentes con los datos generados por el modelo y que se ajusten a los requisitos de tu sistema.

## Ejemplo de docker compose 
´´´#docker compose yaml
services:
  # Kafka broker
  broker:
    image: apache/kafka-native
    container_name: kafka
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 500M
          cpus: '0.5'
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENERS: "CONTROLLER://localhost:9091,HOST://0.0.0.0:9092,DOCKER://0.0.0.0:9093"
      KAFKA_ADVERTISED_LISTENERS: "HOST://localhost:9092,DOCKER://broker:9093"
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: "CONTROLLER:PLAINTEXT,DOCKER:PLAINTEXT,HOST:PLAINTEXT"
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@localhost:9091"
      KAFKA_CONTROLLER_LISTENER_NAMES: "CONTROLLER"
      # required for single node cluster
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      # broker to broker listener
      KAFKA_INTER_BROKER_LISTENER_NAME: DOCKER
    ports: 
    - "9092:9092"
    
  # UI para ver administrar kafka
  kafka-ui:
    image: ghcr.io/kafbat/kafka-ui:latest
    container_name: kafka-ui
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 300M
          cpus: '0.5'
    depends_on: 
    - broker
    environment:
      DYNAMIC_CONFIG_ENABLED: "true"
      KAFKA_CLUSTERS_0_NAME: "aws-kafka"
      KAFKA_CLUSTERS_0_BOOTSTRAP_SERVERS: "broker:9093"
    ports: 
    - "8080:8080"

  # Crea topics nuevos al iniciar el contenedor
  kafka-init-topics:
    image: confluentinc/cp-kafka:7.2.1
    container_name: kafka-scripts
    depends_on:
      - broker
    command: "bash -c 'echo Waiting for Kafka to be ready... && \
               cub kafka-ready -b broker:9093 1 30 && \
               kafka-topics --create --topic customer_logs --partitions 1 --replication-factor 1 --if-not-exists --bootstrap-server broker:9093 && \
               kafka-topics --create --topic predicted_logs --partitions 1 --replication-factor 1 --if-not-exists --bootstrap-server broker:9093'"

  log-producer:
    image: ghcr.io/deathlockers/tlsender:main
    depends_on:
    - broker
    environment:
    - KAFKA_HOST=broker:9093
    - RUNNER_INTERVAL_SECONDS=15
    # - KAFKA_CONSUMER_TOPIC=customer_logs
    # - KAFKA_PRODUCER_TOPIC=predicted_logs
    volumes:
    - ./producer_logs:/data
networks:
  default:
    name: kafka_network
´´´