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
