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

# Documento de Especificación de Requerimientos de Software (SRS)

**Versión 1.0**

---

## CONTROL DE VERSIONES

| Versión | Hecha por | Revisada por | Aprobada por | Fecha | Motivo |
|---------|-----------|--------------|--------------|-------|--------|
| 1.0 | Jahuira Pilco, Dayan Elvis | Mamani Cori, Cristhian Carlos | Jahuira Pilco, Dayan Elvis | 26/04/2026 | Versión Original |

---

## 1. Generalidades de la Empresa

**Nombre:** Aegis Filter

**Visión:** Ser un equipo capaz de desarrollar soluciones de software funcionales, aplicando buenas prácticas de ingeniería y contribuyendo al aprendizaje tecnológico.

**Misión:** Desarrollar aplicaciones de software que cumplan con los requerimientos establecidos, aplicando metodologías de desarrollo y garantizando calidad en los resultados.

**Organigrama:**

- Líder de Proyecto y Backend: encargado de conectores (SQLite, PostgreSQL, MySQL, MongoDB, Redis, Cassandra) y arquitectura base.
- Desarrollador REPL y Formateador: encargado del bucle principal, sistema de comandos, formateo de tablas, exportación CSV y manejo de errores.

---

## 2. Visionamiento de la Empresa

### 2.1. Descripción del Problema

La administración de bases de datos mediante herramientas gráficas limita la comprensión de los procesos internos y no siempre está disponible en entornos técnicos. Además, el uso de herramientas de consola existentes puede resultar complejo para usuarios en formación.

### 2.2. Objetivos de Negocio

- Desarrollar una herramienta funcional de administración de bases de datos
- Aplicar conocimientos de ingeniería de software
- Cumplir con los entregables académicos del curso

### 2.3. Objetivos de Diseño

- Crear una aplicación modular
- Implementar una interfaz basada en comandos
- Garantizar claridad en la interacción con el usuario

### 2.4. Alcance del proyecto

El sistema permite la gestión de bases de datos mediante consola, incluyendo operaciones CRUD y conexión a gestores relacionales (PostgreSQL, MySQL, SQLite) y no relacionales (MongoDB, Redis, Cassandra). Adicionalmente, el sistema se distribuye mediante una extensión de Visual Studio Code, un servidor MCP (Model Context Protocol) para integración con asistentes de IA, y un bot de Telegram en modo de solo lectura. No incluye desarrollo de motor de base de datos ni funcionalidades avanzadas de optimización. Las integraciones externas (servidor MCP y bot de Telegram) no incluyen operaciones de escritura, únicamente consultas de lectura.

### 2.5. Viabilidad del Sistema

El sistema es viable debido al uso de tecnologías accesibles, documentación disponible y alcance controlado (ver Informe de Factibilidad FD01).

### 2.6. Información obtenida del Levantamiento de Información

- Revisión de herramientas existentes (CLI de bases de datos)
- Análisis de necesidades académicas
- Revisión de documentación técnica

---

## 3. Análisis de Procesos

- Diagrama del Proceso Actual – Diagrama de actividades (ver documento .docx)
- Diagrama del Proceso Propuesto – Diagrama de actividades Inicial (ver documento .docx)

---

## 4. Especificación de Requerimientos de Software

### 4.1. Cuadro de Requerimientos Funcionales Inicial

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

### 4.2. Cuadro de Requerimientos No Funcionales

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

### 4.3. Cuadro de Requerimientos Funcionales Final

| ID | Descripción | Prioridad |
|----|-------------|-----------|
| RF-01 | Permitir la conexión multimotor a bases de datos relacionales y no SQL | Muy Alta |
| RF-02 | Crear, modificar y eliminar tablas | Muy Alta |
| RF-03 | Insertar registros mediante comandos en consola | Muy Alta |
| RF-04 | Consultar datos mediante comandos personalizados | Muy Alta |
| RF-05 | Actualizar registros con condiciones | Alta |
| RF-06 | Eliminar registros con condiciones | Alta |
| RF-07 | Listar estructuras de la base de datos | Media |
| RF-08 | Interpretar comandos ingresados por el usuario | Muy Alta |
| RF-09 | Validar comandos antes de su ejecución | Muy Alta |
| RF-10 | Mostrar resultados en formato legible en consola | Muy Alta |
| RF-11 | Mostrar mensajes de error ante comandos inválidos | Muy Alta |
| RF-12 | Incluir comando de ayuda (help) | Media |
| RF-13 | Permitir finalizar la sesión (exit) | Baja |
| RF-14 | Exponer un servidor MCP con herramientas de conexión y consulta de solo lectura para asistentes de IA | Alta |
| RF-15 | Permitir consultas de solo lectura mediante un bot de Telegram multi-motor | Media |
| RF-16 | Generar consultas SQL a partir de lenguaje natural mediante IA | Media |

### 4.4. Reglas de Negocio

- Para utilizar el sistema, el usuario debe tener instalado previamente al menos un motor de base de datos compatible; la herramienta no incluye ningún gestor propio.
- El usuario debe conocer las credenciales de acceso a la base de datos que desea administrar, ya que el sistema no las almacena ni las recuerda entre sesiones.
- Los comandos SQL y NoSQL ingresados deben respetar la sintaxis propia del motor de base de datos al que se está conectado.
- La funcionalidad de exportación a CSV solo está disponible después de haber ejecutado una consulta SELECT.
- El sistema está diseñado para trabajar con una sola conexión a la vez.
- Al finalizar la sesión con el comando exit, cualquier conexión activa se cierra automáticamente.
- El comando help muestra únicamente los comandos disponibles según el modo de operación seleccionado (relacional o NoSQL).
- Las contraseñas se ingresan en texto plano durante el comando connect.
- El sistema está pensado para fines educativos; no se recomienda su uso en producción sin medidas adicionales de seguridad.
- Las integraciones externas (servidor MCP y bot de Telegram) únicamente permiten operaciones de lectura; cualquier intento de comando de escritura será rechazado automáticamente, independientemente del cliente que lo origine.

---

## 5. Fase de Desarrollo

### 5.1. Perfiles de Usuario

- **Usuario Básico (Estudiante):** conocimientos de conexión y comandos SELECT/INSERT/UPDATE/DELETE básicos. Uso: 1-2 veces por semana.
- **Usuario Intermedio (Desarrollador):** SQL avanzado (joins, subconsultas), DDL. Uso: varias veces por semana.
- **Usuario Técnico (Administrador):** administración de SGBD, motores relacionales y NoSQL. Uso: diario.

### 5.2. Modelo Conceptual

Incluye Diagrama de Paquetes, Diagrama de Casos de Uso, y los escenarios narrativos de los 10 casos de uso principales (CU001 a CU010): Seleccionar Modo, Conectar a Base de Datos, Gestionar Estructuras, Consultar Datos, Modificar Datos, Exportar Resultados a CSV, Ver Estado de Conexión, Mostrar Ayuda/Comandos, Desconectar BD y Salir del Sistema. Ver detalle completo en el documento .docx.

### 5.3. Modelo Lógico

Incluye Diagrama de Secuencia y Diagrama de Clases (ver documento .docx).

---

## 6. Conclusiones

El proyecto permitió desarrollar un sistema funcional de administración de bases de datos en consola, capaz de ejecutar operaciones sobre gestores relacionales (MySQL, PostgreSQL, SQLite) y no relacionales (MongoDB, Redis, Cassandra), además de integrarse con asistentes de IA y canales de distribución externos bajo un estricto modelo de solo lectura para dichas integraciones.

## 7. Recomendaciones

- Realizar pruebas con cada uno de los motores de base de datos soportados antes de la presentación.
- Preparar un script de demostración con conexión exitosa, consulta SELECT y manejo de errores.
- Verificar que la terminal soporte caracteres Unicode para las tablas.
- Incluir instrucciones claras de instalación y uso en un README.
- Para versiones futuras, implementar enmascaramiento de contraseñas con el módulo getpass.

## 8. Bibliografía

- Ramakrishnan, R., & Gehrke, J. (2003). Sistemas de Gestión de Bases de Datos (3ª ed.). McGraw-Hill.
- Silberschatz, A., Korth, H. F., & Sudarshan, S. (2019). Database System Concepts (7ª ed.). McGraw-Hill Education.
- Beaulieu, A. (2020). Learning SQL (3ª ed.). O'Reilly Media.
- Python Software Foundation. (2026). The Python Standard Library.

## 9. Webgrafía

- https://docs.python.org/3/
- https://www.postgresql.org/docs/
- https://dev.mysql.com/doc/
- https://www.sqlite.org/docs.html
