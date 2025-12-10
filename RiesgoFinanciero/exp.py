# -*- coding: utf-8 -*-
"""
Sistema Experto Completo con
- Lectura PDF
- Word2Vec
- Inferencia hacia adelante
- Inferencia hacia atrás
- Tkinter GUI
@author: Canul
"""

import os
import tkinter as tk
from tkinter import messagebox, PhotoImage
import PyPDF2
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence


# ====================================================================
# 1) LECTURA DE PDF Y ENTRENAMIENTO DEL MODELO
# ====================================================================

ruta_pdf = "/Users/Canul/Downloads/experto/riesgos.pdf"
ruta_txt = "/Users/Canul/Downloads/experto/cont.txt"
ruta_modelo = "/Users/Canul/Downloads/experto/modelo_entrenado.model"

def extraer_texto_pdf(ruta):
    texto = ""
    with open(ruta, "rb") as f:
        lector = PyPDF2.PdfReader(f)
        for pagina in lector.pages:
            texto += pagina.extract_text() + "\n"
    return texto

# Extraer texto y guardarlo
texto_pdf = extraer_texto_pdf(ruta_pdf)
with open(ruta_txt, "w", encoding="utf-8") as f:
    f.write(texto_pdf)
    
print("📄 Texto extraído del PDF y guardado en:", ruta_txt)

# ← AÑADIR
print("\n📄 --- INICIO DEL TEXTO DEL PDF ---")
print(texto_pdf[:1500])
print("📄 --- FIN DEL TEXTO DEL PDF ---\n")

# Cargar o entrenar modelo
if os.path.exists(ruta_modelo):
    modelo = Word2Vec.load(ruta_modelo)
else:
    sentences = LineSentence(ruta_txt)
    modelo = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)
    modelo.save(ruta_modelo)



# ====================================================================
# 2) MOTOR DE REGLAS – INFERENCIA HACIA ADELANTE Y ATRÁS
# ====================================================================

class SistemaExperto:
    def __init__(self):
        self.reglas = []
        self.hechos = {}

    def agregar_regla(self, condicion, conclusion):
        self.reglas.append((condicion, conclusion))

    def agregar_hecho(self, clave, valor):
        self.hechos[clave] = valor

    # ----------------------- INFERENCIA HACIA ADELANTE ----------------------
    def inferencia_adelante(self):
        nuevos = True
        while nuevos:
            nuevos = False
            for condicion, conclusion in self.reglas:
                if conclusion not in self.hechos:
                    if condicion(self.hechos):
                        self.hechos[conclusion] = True
                        nuevos = True
        return self.hechos

    # ------------------------- INFERENCIA HACIA ATRÁS ------------------------
    def inferencia_atras(self, meta):
        # Si ya está, se cumple
        if meta in self.hechos:
            return True

        # Buscar regla que concluya "meta"
        for condicion, conclusion in self.reglas:
            if conclusion == meta:
                # Evaluar condición
                if condicion(self.hechos):
                    self.hechos[meta] = True
                    return True
                else:
                    return False
        return False



# ====================================================================
# 3) DEFINICIÓN DEL SISTEMA EXPERTO DE RIESGO
# ====================================================================

se = SistemaExperto()

# REGLAS
se.agregar_regla(lambda h: h.get("ingreso", 0) < 8000, "riesgo_ingreso_bajo")
se.agregar_regla(lambda h: h.get("deuda", 0) > 50000, "riesgo_deuda_alta")
se.agregar_regla(lambda h: h.get("historial") == "malo", "riesgo_historial")
se.agregar_regla(lambda h: h.get("empleo") == "inestable", "riesgo_empleo")

# CONCLUSIÓN FINAL (meta)
se.agregar_regla(
    lambda h: h.get("riesgo_ingreso_bajo")
              or h.get("riesgo_deuda_alta")
              or h.get("riesgo_historial")
              or h.get("riesgo_empleo"),
    "riesgo_alto"
)



# ====================================================================
# 4) INTERFAZ TKINTER CON IMÁGENES Y MOTOR DE INFERENCIA
# ====================================================================

caracteristicas_bajo = [
    "Ingresos estables",
    "Deuda baja",
    "Historial positivo"
]

caracteristicas_medio = [
    "Ingresos irregulares",
    "Deuda moderada",
    "Algunos retrasos"
]

caracteristicas_alto = [
    "Deudas altas",
    "Ingresos inestables",
    "Mal historial crediticio"
]

def analizar():
    nombre = entrada.get().strip()

    if nombre == "":
        messagebox.showwarning("Error", "⚠ Escribe un nombre.")
        return

    # Pedir datos por popups (hechos del usuario)
    try:
        ing = float(input("➡ Ingreso mensual: "))
        deu = float(input("➡ Deuda total: "))
        hist = input("➡ Historial (bueno/regular/malo): ").lower()
        emp = input("➡ Empleo (estable/inestable): ").lower()
    except:
        messagebox.showerror("Error", "Valores no válidos.")
        return

    # Cargar hechos
    se.hechos = {}  # limpiar
    se.agregar_hecho("ingreso", ing)
    se.agregar_hecho("deuda", deu)
    se.agregar_hecho("historial", hist)
    se.agregar_hecho("empleo", emp)

    # Inferencia hacia adelante
    se.inferencia_adelante()

    # Inferencia hacia atrás para confirmar meta
    riesgo = se.inferencia_atras("riesgo_alto")

    # DEPENDIENDO DEL RESULTADO, MOSTRAR
    if riesgo:
        mostrar_resultado("RIESGO ALTO 🔴", caracteristicas_alto, "alto.png")
    else:
        # Diferencia entre bajo y medio
        if ing > 20000 and deu < 10000:
            mostrar_resultado("RIESGO BAJO 💚", caracteristicas_bajo, "bajo.png")
        else:
            mostrar_resultado("RIESGO MEDIO 🟡", caracteristicas_medio, "medio.png")


def mostrar_resultado(texto, lista, imagen):
    texto_resultado.config(text=texto)
    texto_caracteristicas.config(text="\n".join(lista))

    try:
        img_or = PhotoImage(file=imagen)
        img = img_or.subsample(3, 3)
        etiqueta_imagen.config(image=img)
        etiqueta_imagen.image = img
    except:
        etiqueta_imagen.config(text="(Imagen no encontrada)")


# ====================================================================
# 5) GUI COMPLETA
# ====================================================================

ventana = tk.Tk()
ventana.title("Sistema Experto: Riesgo Financiero")
ventana.geometry("430x530")

tk.Label(ventana, text="💰 SISTEMA EXPERTO COMPLETO",
         font=("Arial", 12, "bold")).pack(pady=10)

tk.Label(ventana, text="✏ Escribe nombre del solicitante:",
         font=("Arial", 10)).pack()
entrada = tk.Entry(ventana, font=("Arial", 11))
entrada.pack(pady=5)

tk.Button(ventana, text="🔎 ANALIZAR", font=("Arial", 11, "bold"),
          command=analizar).pack(pady=10)

texto_resultado = tk.Label(ventana, text="", font=("Arial", 13, "bold"))
texto_resultado.pack(pady=10)

tk.Label(ventana, text="📌 Características detectadas:",
         font=("Arial", 10, "bold")).pack()
texto_caracteristicas = tk.Label(ventana, text="", font=("Arial", 10))
texto_caracteristicas.pack()

etiqueta_imagen = tk.Label(ventana)
etiqueta_imagen.pack(pady=20)

ventana.mainloop()
