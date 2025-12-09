# --- Función para cargar una receta desde un PDF (Simulación) ---

def cargar_receta_desde_pdf(self, ruta_archivo):
    """
    Simula la extracción, procesamiento y estructuración de una receta
    desde un archivo PDF.
    """
    
    # 1. Extracción de texto (Simulación usando un string multi-línea)
    # En un código real, usarías 'pdfminer.six' aquí.
    texto_extraido = (
        "Título: Ensalada de Quinoa Fresca\n"
        "Ingredientes:\n"
        "1 taza de quinoa\n"
        "200 gramos de queso feta\n"
        "1 pepino en cubos\n"
        "Jugo de 1 limón\n"
        "Pasos:\n"
        "1. Cocinar la quinoa. 2. Mezclar todos los ingredientes. 3. Servir fría."
    )
    
    # 2. Procesamiento y Estructuración (El 'Agente' de PLN)
    
    datos_estructurados = {
        "nombre": "",
        "ingredientes": [],
        "pasos": [],
        "dieta": "variable" # La dieta es incierta a menos que se use IA avanzada
    }
    
    lineas = texto_extraido.split('\n')
    modo = None # Controla si estamos extrayendo ingredientes o pasos
    
    for linea in lineas:
        linea = linea.strip()
        if not linea: continue

        if linea.startswith("Título:"):
            datos_estructurados["nombre"] = linea.split("Título:")[1].strip()
            modo = None
        elif linea.startswith("Ingredientes:"):
            modo = "ingredientes"
        elif linea.startswith("Pasos:"):
            modo = "pasos"
        elif modo == "ingredientes" and linea:
            # Aquí se aplicaría PLN para separar cantidad de ingrediente (ej. '1 taza' de 'quinoa')
            datos_estructurados["ingredientes"].append(linea)
        elif modo == "pasos" and linea:
            datos_estructurados["pasos"].append(linea)


    # 3. Integración a la Base de Conocimiento del Agente
    if datos_estructurados["nombre"]:
        receta_key = datos_estructurados["nombre"].lower().replace(' ', '_')
        self.recetas_base[receta_key] = {
            "ingredientes": [self._limpiar_ingrediente(i) for i in datos_estructurados["ingredientes"]],
            "dieta": datos_estructurados["dieta"],
            "tiempo": 40, # Asumimos un valor inicial si no se extrae
            "dificultad": "estimada"
        }
        return f"✅ Receta '{datos_estructurados['nombre']}' extraída y añadida al conocimiento del {self.nombre}."
    else:
        return "❌ Error: No se pudo identificar el título de la receta en el PDF."

def _limpiar_ingrediente(self, texto):
    """Función de limpieza: intenta aislar solo el nombre del ingrediente."""
    # Esto es una simplificación muy básica para el ejemplo
    palabras_clave = ["taza", "gramos", "cuchara", "de"]
    for p in palabras_clave:
        if p in texto:
            return texto.split(p)[-1].strip()
    return texto.strip()

# --- Fin del módulo de PDF ---