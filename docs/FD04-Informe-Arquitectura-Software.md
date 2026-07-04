# UNIVERSIDAD PRIVADA DE TACNA

# FACULTAD DE INGENIERÍA

# Escuela Profesional de Ingeniería de Sistemas

## Proyecto Administrador de BD en consola o terminal

**Curso:** Base de Datos II

**Docente:** Patrick Cuadros Quiroga

**Integrantes:**

Jahuira Pilco, Dayan Elvis (2022075749)
Mamani Cori, Cristhian Carlos (2023077282)

---

**Tacna – Perú**
**2026**

---

# Documento de Arquitectura de Software (SAD)

**Versión 1.0**

---

## CONTROL DE VERSIONES

| Versión | Hecha por | Revisada por | Aprobada por | Fecha | Motivo |
|---------|-----------|--------------|--------------|-------|--------|
| 1.0 | Jahuira Pilco, Dayan Elvis | Mamani Cori, Cristhian Carlos | Jahuira Pilco, Dayan Elvis | 26/04/2026 | Versión Original |

---

## 1. Introducción

### 1.1. Propósito (Diagrama 4+1)

Definir la arquitectura de software del sistema "Administrador de BD en consola o terminal" utilizando el modelo de vistas 4+1 (Lógica, Implementación, Procesos, Despliegue y Casos de Uso). Presenta una visión global del diseño, justificando cómo las decisiones arquitectónicas satisfacen los requerimientos funcionales de administración de bases de datos y las prioridades de modularidad, extensibilidad y facilidad de uso en entornos de consola.

### 1.2. Alcance

Este documento se centra en el desarrollo de la arquitectura del sistema CLI en Python, su estructura modular de conectores (relacionales y NoSQL) y el formateo de resultados. Incluye la vista lógica (conectores y REPL), la vista de implementación (paquetes y componentes) y la vista de procesos (flujo de ejecución de comandos). Adicionalmente, cubre la arquitectura de las tres integraciones de distribución del sistema: la extensión de Visual Studio Code, el servidor MCP (Model Context Protocol) y el bot de Telegram, todos reutilizando la misma capa de conectores del CLI. Se omiten procesos de interfaz gráfica ya que el sistema opera completamente en consola.

### 1.3. Definición, siglas y abreviaturas

| Término | Definición |
|---------|-----------|
| CLI | Interfaz de Línea de Comandos |
| REPL | Bucle de Lectura-Evaluación-Impresión |
| CRUD | Crear, Leer, Actualizar y Eliminar |
| SGBD | Sistema Gestor de Bases de Datos |
| SQL | Lenguaje de Consulta Estructurado |
| NoSQL | Bases de datos no relacionales |
| CSV | Valores Separados por Comas |
| DDL | Lenguaje de Definición de Datos |
| DML | Lenguaje de Manipulación de Datos |
| MCP | Model Context Protocol |

### 1.4. Organización del documento

El documento está organizado en cuatro secciones principales: Objetivos y restricciones (define qué se debe cumplir), Representación de la arquitectura (donde se exponen los diagramas 4+1), y finalmente los atributos de calidad del software.

---

## 2. Objetivos y Restricciones Arquitectónicas

### 2.1. Priorización de requerimientos

#### 2.1.1. Requerimientos Funcionales

| ID | Descripción | Prioridad |
|----|-------------|-----------|
| RF-01 | Permitir la conexión multimotor a bases de datos relacionales y no SQL | Muy Alta |
| RF-02 | Crear tablas en la base de datos | Alta |
| RF-03 | Insertar registros en las tablas | Muy Alta |
| RF-04 | Consultar datos almacenados | Muy Alta |
| RF-05 | Actualizar registros existentes | Alta |
| RF-06 | Eliminar registros | Alta |
| RF-07 | Listar tablas existentes | Media |
| RF-08 | Mostrar resultados en consola | Muy Alta |
| RF-09 | Salir del sistema | Baja |

#### 2.1.2. No Funcionales – Atributos de Calidad

| ID | Descripción | Prioridad |
|----|-------------|-----------|
| RNF-01 | El sistema debe ejecutarse en entorno de consola (CLI) | Muy Alta |
| RNF-02 | El sistema debe ser compatible con sistemas operativos comunes | Alta |
| RNF-03 | El tiempo de respuesta debe ser menor a 2 segundos | Alta |
| RNF-04 | El sistema debe manejar errores de entrada del usuario | Muy Alta |
| RNF-05 | El código debe estar estructurado y modular | Alta |
| RNF-06 | El sistema debe ser fácil de usar mediante comandos claros | Media |
| RNF-07 | El sistema debe construirse como ejecutable independiente para Windows | Alta |
| RNF-08 | El sistema debe validar la sintaxis básica de los comandos | Muy Alta |

### 2.2. Restricciones

El desarrollo debe utilizar estrictamente Python 3.8 o superior. Las librerías externas permitidas son únicamente aquellas necesarias para la conexión a cada motor de base de datos (relacional y NoSQL), la librería Rich para el formateo de tablas en consola, y las librerías oficiales de las integraciones externas (mcp, python-telegram-bot). La interfaz principal debe ser exclusivamente mediante línea de comandos, sin componentes gráficos. El sistema no debe incluir un motor de base de datos propio, actuando únicamente como intermediario entre el usuario y el SGBD. Las herramientas expuestas al servidor MCP y al bot de Telegram deben restringirse a operaciones de solo lectura.

---

## 3. Representación de la Arquitectura del Sistema

### 3.1. Vista de Caso de Uso

Diagramas de Casos de Uso (ver documento .docx).

### 3.2. Vista Lógica

Incluye Diagrama de Subsistemas (paquetes), Diagrama de Secuencia, Diagrama de Colaboración, Diagrama de Objetos y Diagrama de Clases (ver documento .docx).

**Diagrama de Base de Datos:** El sistema no cuenta con una base de datos propia, ya que su función es actuar como interfaz entre el usuario y los motores de base de datos externos. El único dato que el sistema mantiene en memoria durante la sesión es el resultado de la última consulta SELECT ejecutada (variable `last_results`), utilizada para exportación a CSV. Esta información es volátil y se descarta al cerrar el programa o al ejecutar una nueva consulta.

### 3.3. Vista de Implementación (vista de desarrollo)

Diagrama de arquitectura software (paquetes) y Diagrama de arquitectura del sistema (Diagrama de componentes) — ver documento .docx.

### 3.4. Vista de Procesos

Diagrama de Procesos del sistema (diagrama de actividad) — ver documento .docx.

### 3.5. Vista de Despliegue (vista física)

Además del despliegue local del CLI, el sistema se distribuye en tres entornos adicionales: la extensión de Visual Studio Code (empaquetada con el ejecutable de NexusDB e instalada desde el Marketplace), el servidor MCP (publicado como paquete Python en PyPI e invocado bajo demanda por el cliente de IA) y el bot de Telegram (desplegado de forma permanente como servicio systemd en un VPS Debian, con reinicio automático ante fallos). Los tres canales reutilizan la misma capa de conectores, evitando duplicar la lógica de acceso a datos.

---

## 4. Atributos de Calidad del Software

**Escenario de Funcionalidad:** El sistema demuestra su funcionalidad al interpretar correctamente los comandos ingresados por el usuario, ejecutar las operaciones CRUD correspondientes sobre la base de datos conectada y mostrar los resultados en formato tabular. Ante comandos inválidos, el sistema muestra mensajes de error descriptivos sin finalizar la ejecución.

**Escenario de Usabilidad:** La usabilidad se enfoca en la claridad de los comandos y la legibilidad de los resultados, garantizada mediante un comando help que muestra todos los comandos disponibles organizados por categoría.

**Escenario de Confiabilidad:** El sistema previene fallos catastróficos mediante el manejo estructurado de excepciones. Las credenciales no se almacenan en archivos ni logs, y las conexiones se cierran explícitamente al desconectar o salir.

**Escenario de Rendimiento:** El bucle REPL y los conectores están diseñados para ejecutar consultas simples en tiempos inferiores a un segundo.

**Escenario de Mantenibilidad:** La arquitectura separada en capas (REPL, Conectores, Formateador) y el uso de una clase base abstracta (BaseConnector / BaseNoSQLConnector) facilitan la extensibilidad. Nuevos motores de base de datos pueden añadirse implementando un nuevo conector, sin modificar la lógica del bucle principal ni del formateador.
