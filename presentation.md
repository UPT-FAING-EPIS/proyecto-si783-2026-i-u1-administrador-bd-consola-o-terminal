---
marp: true
theme: default
paginate: true
header: "DB-CLI: Sistema Integral de Gestión de Bases de Datos"
footer: "Ingeniería de Sistemas - Universidad Privada de Tacna"
style: |
  section {
    background-color: #f5f5f5;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  h1 { color: #2c3e50; }
  h2 { color: #2980b9; }
  code { background-color: #e8e8e8; color: #c0392b; }
---

# DB-CLI: Sistema de Gestión Multi-Base de Datos
### Interfaz de Línea de Comandos para SQL y NoSQL

**Presentado por:** Dayan Jahuira Pilco
**Ciclo:** VII[cite: 1]

---

## ¿Qué es el Módulo REPL?

El **Read-Eval-Print Loop** es el corazón de la aplicación. Es un bucle infinito que permite la interacción en tiempo real con el usuario[cite: 1].

1. **Read (Leer):** Captura el comando del usuario.
2. **Eval (Evaluar):** Procesa la lógica y se comunica con el conector.
3. **Print (Imprimir):** Muestra los resultados formateados con la librería `Rich`.
4. **Loop (Bucle):** Regresa al inicio para un nuevo comando.

---

## Arquitectura del Sistema

El proyecto utiliza una estructura basada en **Herencia y Polimorfismo**:

*   **BaseConnector:** Clase abstracta que define el contrato (connect, execute, disconnect).
*   **Conectores Relacionales:** Implementaciones para SQLite, MySQL y PostgreSQL[cite: 3, 5, 7].
*   **Conectores NoSQL:** Implementaciones para MongoDB, Redis y Cassandra[cite: 2, 6, 9].



---

## Conectividad Relacional (SQL)

El sistema soporta las bases de datos más utilizadas en la industria:

*   **SQLite:** Conexión local rápida mediante archivos `.db`[cite: 7].
*   **PostgreSQL:** Soporta esquemas públicos y gestión de transacciones[cite: 5].
*   **MySQL:** Conexión robusta para entornos web[cite: 3].

> **Comando ejemplo:** `connect postgres mi_db postgres 123`[cite: 1]

---

## Conectividad NoSQL

La aplicación se adapta a paradigmas no relacionales:

*   **MongoDB:** Gestión de documentos BSON y filtrado dinámico.
*   **Redis:** Operaciones clave-valor de alta velocidad[cite: 6].
*   **Cassandra:** Consultas distribuidas mediante CQL[cite: 9].



---

## Formateo de Datos y UI

Para mejorar la experiencia del usuario, se implementó `TableFormatter`:

*   **Librería Rich:** Genera tablas elegantes en la consola[cite: 10].
*   **Dynamic Prompt:** El prompt cambia según la base de datos conectada (ej: `dbcli-rel | sqlite: test.db`)[cite: 1].
*   **Exportación:** Permite guardar cualquier resultado de consulta en archivos **CSV**[cite: 1].

---

## Manejo de Errores y Seguridad

El sistema está diseñado para no cerrarse ante fallos:

*   **Try-Except Global:** Captura errores de sintaxis SQL o problemas de red sin terminar la aplicación[cite: 1].
*   **Estado de Conexión:** Valida si hay una sesión activa antes de intentar ejecutar consultas[cite: 1].
*   **Cierre Seguro:** Asegura que las conexiones se cierren correctamente al usar el comando `exit`[cite: 1].

---

## ¡Gracias por su atención!

¿Preguntas sobre la implementación?

*   **Tecnologías:** Python, PyMongo, Psycopg2, Redis-py, Rich.
*   **Autor:** Dayan Jahuira Pilco[cite: 1]
