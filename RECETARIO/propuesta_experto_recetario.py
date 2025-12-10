# -*- coding: utf-8 -*-
"""
SE-ARC Final: Flujo completo de ejecución.
1. Interfaz de selección de ingredientes.
2. Lectura y carga de reglas desde PDF.
3. Inferencia Hacia Adelante con margen de 2 faltantes.
"""

from PyPDF2 import PdfReader
import os

class SistemaExpertoARC:
    
    def __init__(self, ruta_pdf):
        self.hechos = set() 
        self.hechos_historial = set()
        self.reglas = []     
        self.ingredientes_maestros = self._get_master_ingredients()
        self.MAX_FALTANTES = 2 # Margen de error de 2 ingredientes
        self.ruta_pdf = ruta_pdf
        
        print(f"🤖 SE-ARC inicializado. Máx. de faltantes tolerados: {self.MAX_FALTANTES}")

    def _get_master_ingredients(self):
        """Lista maestra de ingredientes para el menú de selección."""
        return [
            "Huevo", "Harina", "Leche", "Azucar", "Mantequilla", "Fresa", 
            "Chocolate", "Limón", "Miel", "Queso", "Vainilla", "Canela", 
            "Nuez", "Agua", "Jamon", "Sartén"
        ]

    # --- 2. Lógica para Leer PDF (Carga de la Base de Conocimiento) ---
    def cargar_base_conocimiento(self):
        """Lee el PDF, extrae el texto y lo convierte en reglas de producción."""
        
        ruta_absoluta = os.path.abspath(self.ruta_pdf)
        print(f"--- 📄 Leyendo PDF en: {ruta_absoluta} ---")
        
        texto_pdf = ""
        try:
            with open(ruta_absoluta, 'rb') as file:
                reader = PdfReader(file)
                for page in reader.pages:
                    texto_pdf += page.extract_text()
        except FileNotFoundError:
            print(f"❌ Error: Archivo PDF no encontrado en '{ruta_absoluta}'.")
            return False
        except Exception as e:
            print(f"❌ Error al leer PDF: {e}")
            return False
        
        reglas_extraidas = []
        recetas_encontradas = texto_pdf.split("###RECETA_INICIO###")
        
        for i, bloque in enumerate(recetas_encontradas):
            if not bloque.strip(): continue
            
            partes = bloque.strip().split("###INGREDIENTES###")
            if len(partes) != 2: continue

            condiciones_str = partes[0].replace('\n', ' ').strip()
            conclusion_str = partes[1].replace('\n', ' ').strip()
            
            # Limpieza y estructuración
            condiciones = [c.strip() for c in condiciones_str.split(' Y ')]
            
            if condiciones and conclusion_str:
                reglas_extraidas.append((f'PDF_R{i}', condiciones, conclusion_str))
        
        if reglas_extraidas:
            self.reglas = reglas_extraidas
            print(f"✅ Se cargaron {len(self.reglas)} reglas del PDF.")
            return True
        else:
            print("⚠️ El PDF no contenía recetas en el formato esperado.")
            return False

    # --- 3. Lógica de Inferencia Hacia Adelante con Margen de Error ---
    def inferencia_hacia_adelante(self):
        """
        Aplica Inferencia Hacia Adelante y almacena los platos viables,
        respetando el MAX_FALTANTES.
        """
        nuevos_hechos_inferidos = True
        iteraciones = 0
        candidatas_faltantes = {}
        
        print("\n--- 🔎 Ejecutando Inferencia Hacia Adelante (Data-Driven) ---")
        
        while nuevos_hechos_inferidos and iteraciones < 10:
            nuevos_hechos_inferidos = False
            hechos_anteriores = len(self.hechos)
            
            for id_regla, condiciones, conclusion in self.reglas:
                
                if conclusion not in self.hechos:
                    
                    ingredientes_faltantes = set()
                    cumple_condiciones = True
                    
                    for condicion in condiciones:
                        # Chequeo de Negación
                        if condicion.startswith('NO:'):
                            if condicion[3:] in self.hechos:
                                cumple_condiciones = False
                                break
                        # Chequeo de Positivo
                        elif condicion not in self.hechos:
                            if condicion.startswith('Ingrediente('):
                                ingredientes_faltantes.add(condicion)
                            else:
                                cumple_condiciones = False
                                break 
                    
                    # Aplicar Regla y Tolerancia:
                    num_faltantes = len(ingredientes_faltantes)

                    if cumple_condiciones and num_faltantes <= self.MAX_FALTANTES:
                        
                        # A. Inferencia Completa (0 Faltantes)
                        if num_faltantes == 0:
                            self.hechos.add(conclusion)
                            print(f"  [+] Regla {id_regla} activada: {conclusion} (Completo)")
                            nuevos_hechos_inferidos = True
                        
                        # B. Almacenar Candidata (1 o 2 Faltantes)
                        elif conclusion.startswith('Plato('):
                            candidatas_faltantes[conclusion] = ingredientes_faltantes
            
            if len(self.hechos) > hechos_anteriores:
                nuevos_hechos_inferidos = True
                
            iteraciones += 1

        # --- Reporte Final ---
        salida = "\n" + "=" * 60
        salida += f"\n--- 🍽️ RESULTADOS DEL AGENTE SE-ARC (Máx. {self.MAX_FALTANTES} Faltantes) ---"
        
        platos_completos = [h for h in self.hechos if h.startswith('Plato(')]
        
        salida += "\n\n✅ Platos que PUEDES hacer AHORA MISMO (0 Faltantes):"
        if platos_completos:
            salida += "\n- " + "\n- ".join([p.split('(')[1].replace(')', '') for p in platos_completos])
        else:
            salida += "\n- Ninguno inferido directamente."
            
        salida += "\n" + "-" * 40
        salida += "\n⚠️ Platos VIABLES con Tareas Pendientes (1 o 2 Faltantes):"
        
        if candidatas_faltantes:
            # Ordenar por el menor número de ingredientes faltantes
            candidatas_ordenadas = sorted(candidatas_faltantes.items(), key=lambda item: len(item[1]))
            
            for plato, faltantes in candidatas_ordenadas:
                nombre_plato = plato.split('(')[1].replace(')', '')
                faltantes_str = ", ".join([f.split('(')[1].replace(')', '') for f in faltantes])
                salida += f"\n- {nombre_plato}: ¡COMPRAR {len(faltantes)}! (Faltan: {faltantes_str})"
        else:
            salida += "\n- Ninguna receta viable con el margen de error."
            
        salida += "\n" + "=" * 60
        return salida

# =============================================================================
# Funciones de Soporte y Flujo Principal (Orquestación)
# =============================================================================

def menu_seleccion_ingredientes(maestros):
    """1. Interfaz: Permite al usuario seleccionar ingredientes de la lista maestra."""
    print("\n\n--- 📋 1. SELECCIÓN DE INGREDIENTES DISPONIBLES ---")
    
    ingredientes_seleccionados = []
    
    while True:
        print("\nLista de ingredientes disponibles (ingrese el número para seleccionar):")
        for i, ing in enumerate(maestros, 1):
            print(f"[{i}] {ing}")
        print("[0] FINALIZAR SELECCIÓN")
        
        try:
            eleccion = input(">>> Ingrese el número del ingrediente (o 0 para terminar): ")
            indice = int(eleccion)
            
            if indice == 0:
                break
            elif 1 <= indice <= len(maestros):
                ingrediente = maestros[indice - 1]
                if ingrediente not in ingredientes_seleccionados:
                    ingredientes_seleccionados.append(ingrediente)
                    print(f"  Añadido: {ingrediente}")
            else:
                print("Opción inválida. Intente de nuevo.")
        except ValueError:
            print("Entrada inválida. Debe ser un número.")
            
    # Convertir a formato de Hecho: Ingrediente(Nombre)
    return [f"Ingrediente({i})" for i in ingredientes_seleccionados]


def ejecutar_flujo_completo(ruta_pdf):
    """Orquesta las 3 etapas del agente."""
    
    # 1. Inicialización y Carga de Conocimiento (Paso 2)
    se_arc = SistemaExpertoARC(ruta_pdf)
    if not se_arc.cargar_base_conocimiento():
        return
    
    # 2. Ingreso de Ingredientes (Paso 1)
    ingredientes_iniciales = menu_seleccion_ingredientes(se_arc.ingredientes_maestros)
    se_arc.hechos.update(ingredientes_iniciales)
    se_arc.hechos_historial.update(ingredientes_iniciales)
    
    print("\n--- BASE DE HECHOS INICIAL (Usuario) ---")
    print(se_arc.hechos_historial)
    
    # 3. Inferencia y Resultados (Paso 3)
    if se_arc.reglas:
        resultado_final = se_arc.inferencia_hacia_adelante()
        print(resultado_final)
    
    
if __name__ == '__main__':
    
    # Asegúrate de que este archivo existe y tiene las 50 reglas estructuradas
    PDF_FILE = "recetas.pdf" 
    
    ejecutar_flujo_completo(PDF_FILE)