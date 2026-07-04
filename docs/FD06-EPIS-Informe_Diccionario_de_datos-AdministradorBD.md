UNIVERSIDAD PRIVADA DE TACNA

FACULTAD DE INGENIERIA

Escuela Profesional de Ingeniería de Sistemas

Informe Final 

Proyecto Administrador de BD en consola o terminal

Curso: Base de Datos II

Docente: Patrick Cuadros Quiroga

Integrantes:

Jahuira Pilco, Dayan Elvis		(2022075749)

Mamani Cori, Cristhian Carlos	(2023077282)

Tacna – Perú

2026

Sistema Administrador de BD en consola o terminal

Documento de Diccionario de Datos

Versión 1.0

Nota: El sistema no cuenta con un motor de base de datos propio; actúa como intermediario hacia motores externos. Por ello, este diccionario documenta las estructuras internas de datos de la aplicación (clases conectoras, excepciones y variables de sesión).

ÍNDICE GENERAL

Introducción

El presente documento describe el Diccionario de Datos del sistema “Administrador de BD en consola o terminal” (dbcli), una herramienta de línea de comandos que permite conectarse y administrar motores de bases de datos relacionales (SQLite, MySQL, PostgreSQL) y no relacionales (MongoDB, Redis, Cassandra).

A diferencia de un sistema tradicional, dbcli no incluye un motor de base de datos propio ni un esquema de almacenamiento persistente: actúa únicamente como una capa intermediaria entre el usuario y los distintos SGBD externos. Por esta razón, el presente diccionario de datos documenta las estructuras internas de la aplicación —clases conectoras, excepciones, formateador de resultados y variables de sesión— que constituyen el modelo de datos con el que trabaja el sistema durante su ejecución.

Este documento cumple la misma función que un diccionario de datos convencional: servir de referencia para desarrolladores que deseen extender el sistema (por ejemplo, agregando un nuevo conector) y para comprender cómo se organiza, transporta y descarta la información dentro de la aplicación.

Modelo de Clases

El modelo de clases se organiza en tres capas principales: la capa de presentación (REPL y TableFormatter), la capa de conectores (BaseConnector, BaseNoSQLConnector y sus implementaciones concretas) y la capa de manejo de errores (módulo exceptions). Los conectores relacionales (SQLiteConnector, MySQLConnector, PostgresConnector) y no relacionales (MongoDBConnector, RedisConnector, CassandraConnector) heredan de una clase base común, lo que permite que el REPL —y las integraciones externas de VS Code, MCP y Telegram— interactúen con cualquier motor mediante la misma interfaz, sin conocer los detalles particulares de cada SGBD. El detalle gráfico de este modelo se encuentra en el Diagrama de Clases del Documento de Arquitectura de Software (FD04, sección 3.2.5).

Diccionario de Datos (Estructuras Internas)

a. Clase BaseConnector

Clase abstracta que define el contrato común para todos los conectores relacionales. No se instancia directamente.

b. Clase SQLiteConnector

Hereda de BaseConnector. Gestiona la conexión a archivos de base de datos SQLite locales.

c. Clase MySQLConnector

Hereda de BaseConnector. Gestiona la conexión a servidores MySQL mediante la librería mysql-connector-python.

d. Clase PostgresConnector

Hereda de BaseConnector. Gestiona la conexión a servidores PostgreSQL mediante la librería psycopg2.

e. Clase BaseNoSQLConnector

Clase abstracta que hereda de BaseConnector y extiende el contrato para motores no relacionales.

f. Clase MongoDBConnector

Hereda de BaseNoSQLConnector. Gestiona la conexión a MongoDB mediante la librería pymongo.

g. Clase RedisConnector

Hereda de BaseNoSQLConnector. Gestiona la conexión a Redis mediante la librería redis-py.

h. Clase CassandraConnector

Hereda de BaseNoSQLConnector. Gestiona la conexión a Cassandra mediante la librería cassandra-driver.

i. Clase REPL

Clase principal del sistema. Implementa el bucle de lectura, interpretación y ejecución de comandos (Read-Eval-Print Loop).

j. Clase TableFormatter

Se encarga de dar formato tabular a los resultados de las consultas, utilizando la librería Rich.

k. Módulo exceptions

Contiene las excepciones personalizadas utilizadas para el manejo estructurado de errores en toda la aplicación.

l. Variables de Sesión y Configuración

Datos que existen únicamente en memoria durante la ejecución del programa y que no se persisten entre sesiones.

Relaciones entre Clases

El REPL mantiene una única instancia activa de un conector (BaseConnector) a la vez; para cambiar de motor, primero debe desconectarse.

SQLiteConnector, MySQLConnector y PostgresConnector heredan de BaseConnector e implementan sus métodos abstractos según el motor relacional correspondiente.

MongoDBConnector, RedisConnector y CassandraConnector heredan de BaseNoSQLConnector, que a su vez extiende BaseConnector.

El REPL utiliza una instancia de TableFormatter para dar formato a los resultados devueltos por cualquier conector antes de mostrarlos en consola.

Los errores generados por los conectores (ConnectionError, SyntaxError, QueryError) son capturados por el REPL, que muestra el mensaje correspondiente sin detener la ejecución.

La variable last_results se llena únicamente tras una consulta de lectura (select/find/get) y es consumida por el comando export.

El servidor MCP y el bot de Telegram reutilizan la misma capa de conectores que el REPL, pero restringen su uso a los métodos de solo lectura (execute_query de tipo SELECT, find, get, get_tables, list_collections).

Reglas de Negocio

a. Gestión de Conexiones

El sistema no incluye ningún motor de base de datos propio; el usuario debe tener instalado y accesible al menos un motor compatible.

Solo puede existir una instancia de conector activa a la vez; para conectarse a un nuevo motor, el usuario debe desconectarse primero (regla reflejada en el atributo 'conector' de la clase REPL).

Las credenciales de conexión no se almacenan ni se recuerdan entre sesiones; deben ingresarse manualmente en cada ejecución mediante el comando connect.

b. Gestión de Resultados

La variable last_results solo se actualiza tras ejecutar una consulta de lectura (select/find/get) y es volátil: se descarta al cerrar el programa o al ejecutar una nueva consulta.

El comando export solo tiene efecto si existe un valor previo en last_results; de lo contrario, no genera ningún archivo.

c. Restricciones de las Integraciones Externas

Las herramientas expuestas al servidor MCP y al bot de Telegram están restringidas a operaciones de solo lectura (execute_query SELECT, find, get, get_tables, list_collections).

Cualquier intento de ejecutar un comando de escritura desde el servidor MCP o el bot de Telegram es rechazado automáticamente, independientemente del cliente que lo origine.

d. Manejo de Errores

Todo error de sintaxis, conexión o ejecución de consulta es capturado mediante las excepciones ConnectionError, SyntaxError y QueryError, y mostrado al usuario sin finalizar el programa.

Módulos y Componentes del Sistema

Dado que el sistema no posee objetos de base de datos propios (triggers, procedimientos almacenados o eventos), esta sección documenta los módulos internos de la aplicación que cumplen un rol equivalente en la organización de la lógica y los datos.

Conclusiones

El diccionario de datos permitió documentar la estructura interna de una aplicación que, al no poseer una base de datos propia, organiza su información en clases conectoras, variables de sesión volátiles y un módulo de excepciones.

La herencia común entre los conectores (BaseConnector y BaseNoSQLConnector) garantiza que el REPL y las integraciones externas (VS Code, MCP, Telegram) trabajen con una interfaz uniforme, independientemente del motor de base de datos conectado.

La variable last_results concentra el único dato persistente durante la sesión, evidenciando el carácter de intermediario —y no de almacén— que tiene el sistema.

Las restricciones de solo lectura aplicadas al servidor MCP y al bot de Telegram quedan reflejadas directamente en las restricciones documentadas para los métodos de cada conector.

Recomendaciones

Mantener actualizado este diccionario cada vez que se agregue un nuevo conector, heredando obligatoriamente de BaseConnector o BaseNoSQLConnector.

Documentar explícitamente en el código los tipos de retorno de los métodos abstractos, para facilitar la extensión del sistema por nuevos desarrolladores.

Evaluar la incorporación de un esquema de configuración (archivo .env o similar) para credenciales, sin comprometer la regla de negocio de no almacenarlas en disco en texto plano.

Para versiones futuras, considerar el registro (logging) de las operaciones de solo lectura realizadas desde el servidor MCP y el bot de Telegram, sin almacenar credenciales.

Bibliografía

Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). Design Patterns: Elements of Reusable Object-Oriented Software. Addison-Wesley.

Silberschatz, A., Korth, H. F., & Sudarshan, S. (2019). Database System Concepts (7ª ed.). McGraw-Hill Education.

Python Software Foundation. (2026). The Python Standard Library. Recuperado de https://docs.python.org/3/

Pallets/Rich Project. (2026). Rich Documentation. Recuperado de https://rich.readthedocs.io/