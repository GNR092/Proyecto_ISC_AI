import sys
from gensim.models import Word2Vec

def inspect_model(model_path):
    """
    Loads a Word2Vec model and prints its metadata and some examples in Markdown format.
    """
    try:
        model = Word2Vec.load(model_path)
        
        print(f"# Reporte del Modelo Word2Vec: `{model_path}`")
        print("\nEste documento describe la arquitectura y las capacidades del modelo de lenguaje `invernadero.model`, que ha sido entrenado con textos relacionados con el manejo de invernaderos.")
        
        print("\n## Metadatos del Modelo\n")
        print(f"* **Tamaño del vocabulario:** {len(model.wv.key_to_index)} palabras únicas")
        print(f"* **Tamaño del vector (dimensionalidad):** {model.vector_size}")
        print(f"* **Algoritmo de entrenamiento:** {'Skip-gram (sg=1)' if model.sg else 'CBOW (sg=0)'}")
        print(f"* **Épocas de entrenamiento:** {model.epochs}")
        print(f"* **Tamaño de la ventana de contexto:** {model.window}")

        # Example vocabulary
        vocab_sample = list(model.wv.key_to_index.keys())[:20]
        print("\n## Muestra del Vocabulario (primeras 20 palabras)\n")
        print("```")
        print(", ".join(vocab_sample))
        print("```")

        # Example similarity queries
        print("\n## Ejemplos de Similitud Semántica\n")
        print("El modelo puede encontrar las palabras más cercanas a un término dado en el contexto de los documentos de entrenamiento.\n")
        
        test_words = ['temperatura', 'humedad', 'plaga', 'cultivo', 'riego', 'tomate']
        for word in test_words:
            if word in model.wv:
                try:
                    similar_words = model.wv.most_similar(word, topn=5)
                    print(f"### Palabras más similares a `{word}`:\n")
                    for sim_word, score in similar_words:
                        print(f"- `{sim_word}` (puntuación: {score:.4f})")
                    print("\n")
                except Exception as e:
                    print(f"No se pudieron encontrar palabras similares para '{word}': {e}\n")

    except Exception as e:
        print(f"## Error")
        print(f"No se pudo cargar o inspeccionar el modelo en `{model_path}`.")
        print(f"**Razón:** {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inspect_model(sys.argv[1])
    else:
        print("Uso: python inspect_model.py <ruta_del_modelo>")
        sys.exit(1)
