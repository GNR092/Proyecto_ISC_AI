import os

def split_text_file(input_file_path, output_directory, chunk_size=50000):
    """
    Lee un archivo de texto, lo divide en fragmentos de un tamaño especificado
    y guarda cada fragmento en un archivo nuevo en un directorio de salida.

    Args:
        input_file_path (str): La ruta al archivo de texto de entrada.
        output_directory (str): La ruta al directorio donde se guardarán los archivos de salida.
        chunk_size (int): El tamaño de cada fragmento en caracteres.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo de entrada '{input_file_path}' no se encontró.")
        return
    except Exception as e:
        print(f"Error al leer el archivo '{input_file_path}': {e}")
        return

    num_chunks = (len(content) + chunk_size - 1) // chunk_size

    for i in range(num_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(content))
        chunk = content[start:end]

        output_file_name = f"output_part_{i+1}.txt"
        output_file_path = os.path.join(output_directory, output_file_name)

        try:
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                outfile.write(chunk)
            print(f"Fragmento {i+1} guardado en '{output_file_path}'")
        except Exception as e:
            print(f"Error al escribir el fragmento {i+1} en '{output_file_path}': {e}")

if __name__ == "__main__":
    input_file = "AgenteInvernadero/inv.txt"
    output_dir = "AgenteInvernadero/output_chunks"
    
    split_text_file(input_file, output_dir)
