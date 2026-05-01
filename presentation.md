---
marp: true
theme: default
paginate: true
header: "DBAdmin – Administrador de Bases de Datos"
footer: "UPT – FAING – EPIS | 2026-I"
---

# 🛡️ DBAdmin
### Administrador de Bases de Datos por Consola

**Curso:** Base de Datos Avanzadas  
**Universidad:** UPT – FAING – EPIS  
**Semestre:** 2026-I

---

## 📐 Arquitectura del Proyecto

```
v2Administrador de BD por consola o terminal/
├── main.py                     ← Punto de entrada principal
├── requirements.txt            ← Dependencias del proyecto
├── cli/                        ← Implementación de la interfaz de línea de comandos
│   ├── __init__.py
│   └── repl.py                 ← Bucle REPL para comandos interactivos
├── connectors/                 ← Conectores para bases de datos específicas
│   ├── __init__.py
│   ├── base.py                 ← Clase base para conectores
│   ├── cassandra_connector.py  ← Conector para Cassandra
│   ├── mongodb_connector.py    ← Conector para MongoDB
│   ├── mysql_connector.py      ← Conector para MySQL
│   ├── nosql_base.py           ← Clase base para NoSQL
│   ├── postgres_connector.py   ← Conector para PostgreSQL
│   ├── redis_connector.py      ← Conector para Redis
│   └── sqlite_connector.py     ← Conector para SQLite
├── core/                       ← Lógica principal del sistema
│   ├── __init__.py
│   ├── executor.py             ← Ejecutor de comandos
│   └── parser.py               ← Analizador de comandos
├── formatters/                 ← Formateadores de salida
│   ├── __init__.py
│   └── table_formatter.py      ← Formateador de tablas
├── utils/                      ← Utilidades y excepciones
│   ├── __init__.py
│   └── exceptions.py           ← Manejo de excepciones
├── assets/                     ← Recursos adicionales
├── build/                      ← Archivos generados durante la construcción
└── diagrams/                   ← Diagramas UML
    ├── activity_diagram.puml
    ├── class_diagram.puml
    └── sequence_diagram.puml
```

---

## 🚀 Inicio Rápido

1. **Clonar el repositorio:**
   ```bash
git clone https://github.com/TU_ORG/dbadmin.git
cd dbadmin
   ```

2. **Crear un entorno virtual e instalar dependencias:**
   ```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
python main.py
   ```

---

## 🧪 Pruebas

- **Pruebas unitarias con pytest:**
  ```bash
pytest --tb=short
  ```

- **Generar reporte de cobertura:**
  ```bash
pytest --cov=.
  ```

---

## 📦 Diagramas UML

- **Diagrama de Clases:** Representa la estructura del sistema.
- **Diagrama de Actividades:** Describe el flujo de procesos.
- **Diagrama de Secuencia:** Muestra la interacción entre componentes.

---

## 🔍 Conectores Soportados

| Base de Datos   | Tipo       | Archivo Conector         |
|-----------------|------------|--------------------------|
| MySQL           | Relacional | `mysql_connector.py`     |
| PostgreSQL      | Relacional | `postgres_connector.py`  |
| SQLite          | Relacional | `sqlite_connector.py`    |
| MongoDB         | NoSQL      | `mongodb_connector.py`   |
| Cassandra       | NoSQL      | `cassandra_connector.py` |
| Redis           | NoSQL      | `redis_connector.py`     |

---

## 👥 Equipo

- **Curso:** Base de Datos Avanzadas  
- **Universidad:** UPT – FAING – EPIS  
- **Semestre:** 2026-I
