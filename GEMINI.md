# Contexto del Proyecto GEMINI: Proyecto_ISC_AI

## Descripción general del proyecto

Este es un proyecto de Python centrado en la construcción de agentes de IA. El entorno de desarrollo está configurado para Visual Studio Code con una cadena de herramientas de Python estándar.

* **Tecnologías principales:** Python
* **Entorno de desarrollo:** Visual Studio Code y Spyder (para pruebas)
* **Dependencias clave (de las recomendaciones de VS Code):**
  * `ms-python.python`: Extensión principal de Python para VS Code.
  * `ms-python.vscode-pylance`: Proporciona soporte de lenguaje enriquecido para Python.
  * `ms-python.python-extension-pack`: Una colección de extensiones populares para el desarrollo de Python.
  * `google.gemini-cli-companion`: Compañero de la CLI de Gemini para interactuar con Gemini AI.
  * `usernamehw.errorlens`: Resalta errores y advertencias en el código.
  * `kisstkondoros.vscode-gutter-preview`: Muestra vistas previas de imágenes en el margen del editor.

## Construcción y ejecución

Todavía no hay comandos de construcción o ejecución definidos, ya que no hay código de aplicación.

<!--
TODO: Agregue instrucciones para construir, ejecutar y probar el proyecto una vez que se agregue el código de la aplicación. Por ejemplo:

**Para instalar dependencias:**
```bash
pip install -r requirements.txt
```

**Para ejecutar la aplicación principal:**
```bash
python src/main.py
```
-->

## Convenciones de desarrollo

El proyecto tiene las siguientes convenciones de desarrollo configuradas en `.vscode/settings.json`:

* **Linting:** `pylint` está habilitado para el análisis de código.
* **Formato:** Se utiliza el formateador de código `black` para mantener un estilo de código consistente.
* **Formato al guardar:** El código se formatea automáticamente con `black` cada vez que se guarda un archivo.
* **Intérprete de Python:** Se utiliza el `python` predeterminado en la ruta del entorno.

Estas convenciones son aplicadas por las extensiones y configuraciones recomendadas de VS Code. Se espera que todas las contribuciones se adhieran a estos estándares.
