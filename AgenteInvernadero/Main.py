from agente import Invernadero, AgenteInvernadero
from Commands import CommandHandler


def main():
    """
    Función principal para configurar y ejecutar la simulación del invernadero
    y demostrar la capacidad de razonamiento por analogía del agente.
    """
    # Crear el entorno del invernadero.
    invernadero_simulado = Invernadero()

    # Crear el agente y asignarle un cultivo.
    # El agente usará el perfil de "default" por defecto, o el especificado.
    agente = AgenteInvernadero(invernadero_simulado, tipo_cultivo="default")

    # Crear el manejador de comandos y obtener la lista de nombres para mostrar.
    command_handler = CommandHandler(agente)
    comandos_dict = command_handler.get_commands_dict()
    nombres_comandos = command_handler.get_command_names()

    command_handler.responder("Que desea hacer:")
    print(f"(Comandos: !{', !'.join(nombres_comandos)})")

    while True:
        try:
            user_input = input("Usuario: ")

            if user_input.lower().startswith("!"):
                command_name = user_input[1:].lower()

                comando_func = comandos_dict.get(command_name)

                if comando_func:

                    if comando_func():
                        break
                else:
                    command_handler.responder(
                        f"Comando '{user_input}' no reconocido. Escribe !help para ver la lista de comandos."
                    )
            else:

                command_handler.responder(
                    "Entrada no reconocida como comando. Intente con !help para ver los comandos disponibles."
                )
        except KeyboardInterrupt:
            command_handler.responder("\n")
            comandos_dict["salir"]()
            break


if __name__ == "__main__":
    main()
