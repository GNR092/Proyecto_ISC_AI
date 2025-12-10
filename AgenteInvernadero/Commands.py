"""
Contiene la lógica y la estructura para manejar los comandos del sistema.
"""


class CommandHandler:
    """
    Clase que gestiona la declaración y ejecución de comandos.
    """

    def __init__(self, agente):
        """
        Inicializa el despachador de comandos registrando todos los comandos disponibles.

        Args:
            agente: La instancia del agente que los comandos podrían necesitar para operar.
        """
        self.agente = agente
        self._commands = {
            "simular": self.simulacion,
            "simulamanual": self.simulacion_manual,
            "analogia": self.realizar_analogia_cmd,
            "salir": self.salir,
            "help": self.help,
        }

    def responder(self, mensaje):
        """Imprime un mensaje estandarizado para el agente."""
        print(f"Agente: {mensaje}")

    def get_commands_dict(self):
        """Devuelve el diccionario de comandos."""
        return self._commands

    def get_command_names(self):
        """Devuelve una lista con los nombres de los comandos disponibles."""
        return list(self._commands.keys())

    def salir(self):
        """Imprime el mensaje de despedida y devuelve True para señalar que se debe salir."""
        self.responder("¡Hasta luego!")
        return True

    def help(self):
        """Muestra una lista de todos los comandos disponibles."""
        self.responder("Comandos disponibles:")

        for name in self.get_command_names():
            print(f"  !{name}")
        return False

    def simulacion_manual(self):
        """
        Ejecuta una simulación manual paso a paso donde el usuario introduce los valores.
        """
        try:
            self.responder(
                "Iniciando simulación manual. Escriba 'cancelar' en cualquier momento para salir."
            )

            perfiles = self.agente.get_perfiles_disponibles()
            self.responder("Perfiles de cultivo disponibles:")
            for perfil in perfiles:
                print(f"  - {perfil}")

            tipo_cultivo_elegido = ""
            while tipo_cultivo_elegido not in perfiles:
                entrada_cultivo = input(
                    f"Agente: Por favor, elija un cultivo de la lista: "
                ).lower()
                if entrada_cultivo == "cancelar":
                    self.responder("Simulación manual cancelada.")
                    return False
                if entrada_cultivo not in perfiles:
                    self.responder(
                        f"El cultivo '{entrada_cultivo}' no es un perfil válido."
                    )
                else:
                    tipo_cultivo_elegido = entrada_cultivo

            self.agente.set_cultivo(tipo_cultivo_elegido)
            self.responder(f"Cultivo '{tipo_cultivo_elegido}' seleccionado.")

            # 2. Bucle para pedir T° y H°
            while True:
                try:

                    temp_input = input(
                        f"Agente: Ingrese la TEMPERATURA actual (o 'cancelar'): "
                    ).lower()
                    if temp_input == "cancelar":
                        break
                    temperatura = float(temp_input)

                    hum_input = input(
                        f"Agente: Ingrese la HUMEDAD actual (o 'cancelar'): "
                    ).lower()
                    if hum_input == "cancelar":
                        break
                    humedad = float(hum_input)

                    # Procesar estado manual
                    self.agente.procesar_estado_manual(temperatura, humedad)

                except ValueError:
                    self.responder("Entrada inválida. Por favor, ingrese un número.")
                except Exception as e:
                    self.responder(f"Ocurrió un error inesperado: {e}")

            self.responder("Simulación manual finalizada.")

        except KeyboardInterrupt:
            print("\n")
            self.responder("Simulación manual cancelada por el usuario.")

        return False

    def simulacion(self):
        """
        Ejecuta una simulación pidiendo al usuario el tipo de cultivo y la duración.
        """
        try:
            # 1. Obtener y mostrar perfiles disponibles.
            perfiles = self.agente.get_perfiles_disponibles()
            self.responder("Perfiles de cultivo disponibles:")
            for perfil in perfiles:
                print(f"  - {perfil}")

            # 2. Pedir al usuario que elija un tipo de cultivo.
            tipo_cultivo_elegido = ""
            while tipo_cultivo_elegido not in perfiles:
                tipo_cultivo_elegido = input(
                    f"Agente: Por favor, elija un cultivo de la lista: "
                ).lower()
                if tipo_cultivo_elegido not in perfiles:
                    self.responder(
                        f"El cultivo '{tipo_cultivo_elegido}' no es un perfil válido."
                    )

            # 3. Pedir la duración de la simulación.
            duracion_seg = 0
            while duracion_seg <= 0:
                try:
                    duracion_input = input(
                        "Agente: Ingrese la duración de la simulación en segundos: "
                    )
                    duracion_seg = int(duracion_input)
                    if duracion_seg <= 0:
                        self.responder("La duración debe ser un número positivo.")
                except ValueError:
                    self.responder("Por favor, ingrese un número entero válido.")

            # 4. Configurar el agente y ejecutar la simulación.
            self.responder(
                f"\nConfigurando agente para simular el cultivo de '{tipo_cultivo_elegido}'..."
            )
            self.agente.set_cultivo(tipo_cultivo_elegido)
            self.agente.simular_un_dia(duracion_simulacion_seg=duracion_seg)

            return False
        except KeyboardInterrupt:
            print("\n\nComando 'simular' cancelado por el usuario.")
            return False

    def realizar_analogia_cmd(self):
        """
        Pide al usuario tres palabras para realizar una analogía semántica.
        """
        try:
            self.responder(
                "Iniciando comando de analogía. Escriba 'cancelar' para salir."
            )

            p1 = ""
            while not p1:
                p1_input = input(
                    "Agente: Ingrese la primera palabra (p1) (ej: 'temperatura', 'cancelar'): "
                ).lower()
                if p1_input == "cancelar":
                    self.responder("Comando de analogía cancelado.")
                    return False
                if not p1_input.strip():
                    self.responder("La palabra no puede estar vacía.")
                else:
                    p1 = p1_input

            p2 = ""
            while not p2:
                p2_input = input(
                    "Agente: Ingrese la segunda palabra (p2) (ej: 'calor', 'cancelar'): "
                ).lower()
                if p2_input == "cancelar":
                    self.responder("Comando de analogía cancelado.")
                    return False
                if not p2_input.strip():
                    self.responder("La palabra no puede estar vacía.")
                else:
                    p2 = p2_input

            p3 = ""
            while not p3:
                p3_input = input(
                    "Agente: Ingrese la tercera palabra (p3) (ej: 'humedad', 'cancelar'): "
                ).lower()
                if p3_input == "cancelar":
                    self.responder("Comando de analogía cancelado.")
                    return False
                if not p3_input.strip():
                    self.responder("La palabra no puede estar vacía.")
                else:
                    p3 = p3_input

            self.agente.realizar_analogia_semantica(p1, p2, p3)
            self.responder("Comando de analogía finalizado.")

        except KeyboardInterrupt:
            print("\n")
            self.responder("Comando de analogía cancelado por el usuario.")
        except Exception as e:
            self.responder(f"Ocurrió un error inesperado durante la analogía: {e}")

        return False
