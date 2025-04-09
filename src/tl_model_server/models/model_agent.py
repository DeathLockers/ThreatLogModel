import importlib
import logging


class ModelsAgent:
    """Agent que carrega els models de disc
    Segons el tipus de missatge, el model a executar l'algorisme será diferent
    Aquest agent també serveix per entrenar els models"""
    model = None
    model_name = None
    def __init__(self, model_name):
        """Cargamos la infromación del modelo que queremos cargar"""
        self.model_name = model_name
        logging.info("Initializing ModelsAgent with model: %s", self.model_name)
        self.model_module = importlib.import_module(f"tl_model_server.models.{self.model_name}.model")

    def inference(self, message=None) -> dict:
        """Procesa el mensaje, asigna el trabajo al modelo disponible y del tipo adecuado
        Si localiza una amenaza, envía una alerta de amenaza detectada mediante el productor
        Args:
            message (str): Mensaje a procesar
        Returns:
            dict: Mensaje procesado, con la respuesta del modelo si es amenaza o no
        """

        logging.info("Processing message: %s", message)
        clean_message = self.model_module.process_msg(message)  # Procesar el mensaje
        prediction = self.model.predict(clean_message)
        return {"status": int(prediction[0]), "message": message, "clean_message": clean_message, "model": self.model_name}

    def train(self, model_name, data_path):
        """
        Entrena y guarda un modelo por defecto en el caso de que no haya ninguno con el csv de logs
        Args:
            model_name (str): Nombre del modelo a entrenar
            data_path (str): Ruta al csv de logs
        Returns:
            Tuple: (accuracy, precision) del modelo entrenado
            
        """
        try:
            logging.info("Training model: %s with data in %s", model_name, data_path)
            self.model_name = model_name
            self.model_module = importlib.import_module(f"tl_model_server.models.{model_name}.model")
            return self.model_module.train(model_name, data_path)
        except Exception as e:
            logging.error("No ha funcionado el entrenamiento del modelo.")
            raise


    def load_model(self, model_name:str = None):
        """Carga el modelo de disco"""
        try:
            logging.info("Loading model: %s", f"tl_model_server.models.{model_name}.model")
            if model_name is not None:
                self.model_name = model_name
                self.model_module = importlib.import_module(f"tl_model_server.models.{self.model_name}.model")
                model_name = 1
            if self.model is None and model_name == 1:
                self.model = self.model_module.load_model(model_name)
        except Exception as e:
            logging.error("No ha funcionado la carga del modelo.")
            raise


if __name__ == "__main__":
    agent = ModelsAgent("model_v1")
    # agent.train("model_v1", "train_logs.csv")
    agent.load_model()

    logging.info(agent.inference("message test"))