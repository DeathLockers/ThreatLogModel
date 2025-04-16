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
