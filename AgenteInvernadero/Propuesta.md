# Propuesta de Proyecto: Sistema Inteligente para el Control de Temperatura en Invernaderos

## Resumen
Este proyecto propone el diseño y desarrollo de un sistema basado en inteligencia artificial para monitorear y regular de forma automática la temperatura dentro de un invernadero. El objetivo es optimizar las condiciones para el crecimiento de los cultivos, asegurar su salud y rendimiento, y reducir el consumo energético al evitar el funcionamiento innecesario de los sistemas de climatización.

## Problema a Resolver
La temperatura es un factor crítico en la agricultura de invernadero. Las fluctuaciones extremas o sostenidas fuera de un rango óptimo pueden causar estrés en las plantas, reducir la producción e incluso provocar la pérdida de cosechas. El control manual de la temperatura es ineficiente, requiere supervisión constante, es propenso a errores humanos y no puede reaccionar con la rapidez necesaria a los cambios súbitos de las condiciones ambientales.

## Solución Propuesta
Se desarrollará un agente inteligente basado en un sistema de reglas (motor de inferencia). Este sistema operará de la siguiente manera:
1.  **Entrada de Datos:** El sistema recibirá datos de un sensor de temperatura (simulado para este prototipo).
2.  **Procesamiento:** Un motor de inferencia evaluará la temperatura actual contra una base de conocimiento (conjunto de reglas predefinidas).
3.  **Toma de Decisiones:** Basado en las reglas, el agente decidirá si es necesario activar o desactivar los sistemas de climatización (calefacción, ventiladores, sistema de enfriamiento).
4.  **Salida:** El sistema enviará comandos a los actuadores (simulados) para ejecutar la acción decidida.

**Ejemplo de Regla:** `SI la temperatura > 25°C Y el ventilador está apagado, ENTONCES activar ventilador.`

## Objetivos del Proyecto

### Objetivo Principal:
*   Crear un prototipo funcional de software que simule el control inteligente de la temperatura de un invernadero.

### Objetivos Específicos:
*   Diseñar e implementar un motor de inferencia simple en Python.
*   Definir una base de conocimiento con reglas claras para el control de temperatura.
*   Crear una simulación que represente la temperatura del invernadero y el estado de los actuadores (calefactor, ventilador).
*   Generar un registro (log) de las decisiones tomadas por el agente.

## Alcance del Proyecto

*   El software del agente inteligente y el motor de inferencia.
*   La simulación completa del entorno (sensor de temperatura y actuadores).
*   Pruebas del sistema en diferentes escenarios simulados (un día caluroso, una noche fría).

### Fuera del Alcance:
*   La implementación en hardware físico (sensores o actuadores reales).
*   El control de otras variables ambientales como la humedad, el CO2 o la intensidad de la luz.
*   El desarrollo de una interfaz gráfica de usuario.

## Metodología y Fases

### Fase 1: Análisis y Diseño
*   Definir las reglas lógicas que gobernarán el sistema.
*   Diseñar la arquitectura del software (módulos para el simulador, motor de inferencia, etc.).

### Fase 2: Desarrollo
*   Codificar el simulador del invernadero.
*   Implementar el motor de inferencia y la base de conocimiento.
*   Integrar todos los componentes.

### Fase 3: Pruebas y Ajuste
*   Ejecutar simulaciones para validar el comportamiento del agente.
*   Ajustar las reglas para optimizar el rendimiento y la eficiencia.

## Criterios de Éxito
*   El sistema es capaz de mantener la temperatura simulada dentro del rango objetivo (ej. 20°C-25°C) durante el 95% del tiempo en una simulación de 24 horas.
*   El sistema reacciona correctamente a cambios bruscos de temperatura en la simulación en menos de 5 minutos (simulados).