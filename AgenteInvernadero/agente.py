import logging
import random
import time
import os
from datetime import datetime
from gensim.models import Word2Vec, KeyedVectors

# Configuración del logging para guardar las decisiones del agente
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_dir, f"Agente_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filename=log_filename,
    filemode="w",
    encoding="utf-8",
)


# --------------------------------------------------------------
# CLASE PARA SIMULAR EL ENTORNO DEL INVERNADERO
# --------------------------------------------------------------
class Invernadero:
    def __init__(self, temperatura_inicial=40, humedad_inicial=55):
        self.temperatura = temperatura_inicial
        self.humedad = humedad_inicial
        self.calefactor_encendido = False
        self.ventilador_encendido = False
        self.humidificador_encendido = False
        logging.info(
            f"Invernadero inicializado. Temperatura°: {self.temperatura}°C, Humedad: {self.humedad}%"
        )

    def actualizar_estado(self):
        """
        Simula el cambio de T° y humedad basado en actuadores y factores externos.
        """

        if self.calefactor_encendido:
            self.temperatura += 0.8
            self.humedad -= 0.5
        if self.ventilador_encendido:
            self.temperatura -= 0.8
            self.humedad -= 1.5

        if self.humidificador_encendido:
            self.humedad += 1.5
            self.temperatura -= 0.2

        # Influencia externa aleatoria (clima)
        self.temperatura += random.uniform(-1.2, 1.2)
        self.humedad += random.uniform(-1.2, 1.2)

        # Limitar valores a rangos razonables
        self.temperatura = round(max(0, min(50, self.temperatura)), 2)
        self.humedad = round(max(0, min(100, self.humedad)), 2)

    def obtener_estado(self):
        """Devuelve el estado actual del invernadero."""
        return {
            "temperatura": self.temperatura,
            "humedad": self.humedad,
            "calefactor_encendido": self.calefactor_encendido,
            "ventilador_encendido": self.ventilador_encendido,
            "humidificador_encendido": self.humidificador_encendido,
        }


# --------------------------------------------------------------
# CLASE PARA EL AGENTE INTELIGENTE
# --------------------------------------------------------------
class AgenteInvernadero:
    """
    Agente inteligente que toma decisiones para regular la temperatura y humedad
    del invernadero basándose en un sistema de reglas para un cultivo específico.
    """

    PERFILES_CULTIVO = {
        "tomate": {"temp_min": 13, "temp_max": 26, "hum_min": 40, "hum_max": 60},
        "lechuga": {"temp_min": 10, "temp_max": 20, "hum_min": 50, "hum_max": 80},
        "pepino": {"temp_min": 18, "temp_max": 28, "hum_min": 65, "hum_max": 75},
        "default": {"temp_min": 20, "temp_max": 25, "hum_min": 60, "hum_max": 70},
    }

    def __init__(self, invernadero, tipo_cultivo="tomate"):
        self.invernadero = invernadero
        self.tipo_cultivo = tipo_cultivo.lower()
        self.modelo_vectores = None

        perfil = self.PERFILES_CULTIVO.get(
            self.tipo_cultivo, self.PERFILES_CULTIVO["default"]
        )
        self.temp_optima_min = perfil["temp_min"]
        self.temp_optima_max = perfil["temp_max"]
        self.hum_optima_min = perfil["hum_min"]
        self.hum_optima_max = perfil["hum_max"]

        logging.info(f"Agente creado para cultivo de '{self.tipo_cultivo}'.")
        logging.info(
            f"T° óptima: [{self.temp_optima_min}-{self.temp_optima_max}°C], "
            f"Humedad óptima: [{self.hum_optima_min}-{self.hum_optima_max}%]"
        )

    def set_cultivo(self, tipo_cultivo):
        """
        Cambia el cultivo del agente y actualiza los parámetros óptimos.
        """
        self.tipo_cultivo = tipo_cultivo.lower()
        perfil = self.PERFILES_CULTIVO.get(
            self.tipo_cultivo, self.PERFILES_CULTIVO["default"]
        )
        self.temp_optima_min = perfil["temp_min"]
        self.temp_optima_max = perfil["temp_max"]
        self.hum_optima_min = perfil["hum_min"]
        self.hum_optima_max = perfil["hum_max"]

        logging.info(f"Agente reconfigurado para cultivo de '{self.tipo_cultivo}'.")
        logging.info(
            f"Nueva T° óptima: [{self.temp_optima_min}-{self.temp_optima_max}°C], "
            f"Nueva Humedad óptima: [{self.hum_optima_min}-{self.hum_optima_max}%]"
        )

    @classmethod
    def get_perfiles_disponibles(cls):
        """Devuelve los nombres de los perfiles de cultivo disponibles."""
        return list(cls.PERFILES_CULTIVO.keys())

    def _cargar_modelo_vectores(self):
        """Carga el modelo Word2Vec si aún no ha sido cargado."""
        if self.modelo_vectores is None:
            model_path = "invernadero.model"
            print(f"\nIntentando cargar el modelo de lenguaje desde: {model_path}")
            try:
                full_model = Word2Vec.load(model_path)
                self.modelo_vectores = full_model.wv
                print("✅ Modelo de lenguaje cargado exitosamente.")
            except Exception as e:
                print(
                    f"❌ ADVERTENCIA: No se pudo cargar el modelo desde '{model_path}'."
                )
                print(f"   Razón: {e}")
                print(
                    "   Por favor, asegúrese de que el archivo 'invernadero.model' exista y sea un modelo Word2Vec válido."
                )
                print("   La funcionalidad de analogía no estará disponible.")
                return False
        return True

    def realizar_analogia_semantica(self, p1_es_a, p2_como, p3_es_a):
        """
        Realiza una analogía semántica del tipo "p1 es a p2 como X es a p3".
        """
        print("\n--- Iniciando Prueba de Analogía Semántica ---")
        if not self._cargar_modelo_vectores():
            return

        try:
            # La función most_similar busca X en la ecuación: p1 - p2 + p3 = X
            resultado = self.modelo_vectores.most_similar(
                positive=[p1_es_a, p3_es_a], negative=[p2_como], topn=1
            )
            palabra_resultante, score = resultado[0]
            print(
                f"🧠 ANALOGÍA: '{p1_es_a}' es a '{p2_como}' como '{palabra_resultante.upper()}' es a '{p3_es_a}'. (Confianza: {score:.2f})"
            )
        except KeyError as e:
            print(
                f"🤔 La palabra '{e.args[0]}' no se encuentra en el vocabulario del modelo."
            )
        except Exception as e:
            print(f"❌ Ocurrió un error inesperado al realizar la analogía: {e}")

    def _motor_inferencia_temperatura(self, estado):
        """Decide la acción para la temperatura."""
        temp = estado["temperatura"]
        if temp > self.temp_optima_max and not estado["ventilador_encendido"]:
            return "encender_ventilador"
        elif temp < self.temp_optima_min and not estado["calefactor_encendido"]:
            return "encender_calefactor"
        elif self.temp_optima_min <= temp <= self.temp_optima_max:
            if estado["ventilador_encendido"]:
                return "apagar_ventilador"
            if estado["calefactor_encendido"]:
                return "apagar_calefactor"
        return "ninguna_temp"

    def _motor_inferencia_humedad(self, estado):
        """Decide la acción para la humedad."""
        hum = estado["humedad"]
        # Usa el ventilador para bajar la humedad
        if hum > self.hum_optima_max and not estado["ventilador_encendido"]:
            return "encender_ventilador_humedad"
        elif hum < self.hum_optima_min and not estado["humidificador_encendido"]:
            return "encender_humidificador"
        elif self.hum_optima_min <= hum <= self.hum_optima_max:
            if estado["ventilador_encendido"]:
                # Solo apaga el ventilador si la temperatura también es óptima
                if (
                    self.temp_optima_min
                    <= estado["temperatura"]
                    <= self.temp_optima_max
                ):
                    return "apagar_ventilador"
            if estado["humidificador_encendido"]:
                return "apagar_humidificador"
        return "ninguna_hum"

    def _ejecutar_acciones(self, acciones):
        """Ejecuta las acciones decididas y actualiza el estado del invernadero."""
        for accion in acciones:
            # --- Acciones de Temperatura y Humedad ---
            if accion == "encender_ventilador":
                self.invernadero.ventilador_encendido = True
                self.invernadero.calefactor_encendido = False
                logging.info(
                    f"DECISIÓN (T°={self.invernadero.temperatura}°C): ALTA. Encendiendo ventilador."
                )
            elif accion == "encender_ventilador_humedad":
                self.invernadero.ventilador_encendido = True
                self.invernadero.calefactor_encendido = False
                logging.info(
                    f"DECISIÓN (H={self.invernadero.humedad}%): ALTA. Encendiendo ventilador para reducir humedad."
                )
            elif accion == "encender_calefactor":
                self.invernadero.calefactor_encendido = True
                self.invernadero.ventilador_encendido = False
                logging.info(
                    f"DECISIÓN (T°={self.invernadero.temperatura}°C): BAJA. Encendiendo calefactor."
                )
            elif accion == "apagar_ventilador":
                self.invernadero.ventilador_encendido = False
                logging.info(f"DECISIÓN (T° y H° ÓPTIMAS): Apagando ventilador.")
            elif accion == "apagar_calefactor":
                self.invernadero.calefactor_encendido = False
                logging.info(
                    f"DECISIÓN (T°={self.invernadero.temperatura}°C): ÓPTIMA. Apagando calefactor."
                )
            elif accion == "encender_humidificador":
                self.invernadero.humidificador_encendido = True
                logging.info(
                    f"DECISIÓN (H={self.invernadero.humedad}%): BAJA. Encendiendo humidificador."
                )
            elif accion == "apagar_humidificador":
                self.invernadero.humidificador_encendido = False
                logging.info(
                    f"DECISIÓN (H={self.invernadero.humedad}%): ÓPTIMA. Apagando humidificador."
                )

    def procesar(self):
        """Paso principal del agente: percibe, decide y actúa."""
        estado = self.invernadero.obtener_estado()
        accion_temp = self._motor_inferencia_temperatura(estado)
        accion_hum = self._motor_inferencia_humedad(estado)

        acciones_netas = {accion_temp, accion_hum}
        acciones_netas.discard("ninguna_temp")
        acciones_netas.discard("ninguna_hum")

        if not acciones_netas:
            logging.info(
                f"INFO (T°={estado['temperatura']}°C, H={estado['humedad']}%): Estable. No se requieren acciones."
            )
        else:
            self._ejecutar_acciones(list(acciones_netas))

    def procesar_estado_manual(self, temperatura, humedad):
        """
        Procesa un estado de T° y H° proporcionado manualmente, decide y actúa.
        Muestra el estado de los actuadores después de actuar.
        """
        # Crear un diccionario de estado con los valores manuales
        # y el estado real de los actuadores para los motores de inferencia.
        estado_actual_actuadores = self.invernadero.obtener_estado()
        estado_manual = {
            "temperatura": temperatura,
            "humedad": humedad,
            "calefactor_encendido": estado_actual_actuadores["calefactor_encendido"],
            "ventilador_encendido": estado_actual_actuadores["ventilador_encendido"],
            "humidificador_encendido": estado_actual_actuadores[
                "humidificador_encendido"
            ],
        }

        logging.info(f"PROCESO MANUAL: T°={temperatura}°C, H={humedad}%")

        accion_temp = self._motor_inferencia_temperatura(estado_manual)
        accion_hum = self._motor_inferencia_humedad(estado_manual)

        acciones_netas = {accion_temp, accion_hum}
        acciones_netas.discard("ninguna_temp")
        acciones_netas.discard("ninguna_hum")

        if not acciones_netas:
            logging.info(f"INFO MANUAL: Estable. No se requieren acciones.")
            print("--- Agente no requiere acción ---")
        else:
            self._ejecutar_acciones(list(acciones_netas))

        # Mostrar el resultado de las acciones
        estado_final_actuadores = self.invernadero.obtener_estado()
        print("--- Resultado de la Acción del Agente ---")
        print(
            f"Calefactor: {'ON' if estado_final_actuadores['calefactor_encendido'] else 'OFF'} | "
            f"Ventilador: {'ON' if estado_final_actuadores['ventilador_encendido'] else 'OFF'} | "
            f"Humidificador: {'ON' if estado_final_actuadores['humidificador_encendido'] else 'OFF'}"
        )

    def simular_un_dia(self, duracion_simulacion_seg=60):
        """Ejecuta un ciclo de simulación para un "día"."""
        print(f"--- Iniciando Simulación para: {self.tipo_cultivo.upper()} ---")
        print(
            f"La simulación durará {duracion_simulacion_seg} segundos. Revise 'invernadero.log' para detalles."
        )
        try:
            inicio = time.time()
            while time.time() - inicio < duracion_simulacion_seg:
                self.procesar()
                self.invernadero.actualizar_estado()

                estado = self.invernadero.obtener_estado()
                print(
                    f"T: {estado['temperatura']:>5.2f}°C | H: {estado['humedad']:>5.2f}% | "
                    f"Calefactor: {'ON' if estado['calefactor_encendido'] else 'OFF'} | "
                    f"Ventilador: {'ON' if estado['ventilador_encendido'] else 'OFF'} | "
                    f"Humidif.: {'ON' if estado['humidificador_encendido'] else 'OFF'}"
                )

                time.sleep(0.500)
        except KeyboardInterrupt:
            print("\n--- Simulación Interrumpida por el Usuario ---")

        print(f"--- Simulación para {self.tipo_cultivo.upper()} Finalizada ---")
