# Whitepaper de Rudag Core

**Versión 1.0 - 16 de Octubre de 2025**

## Resumen (Abstract)

Rudag Core es un protocolo de blockchain y una criptomoneda descentralizada (RGD) construida con un enfoque en la simplicidad, la modularidad y la educación. Este documento técnico describe la arquitectura del sistema, incluyendo el modelo de la cadena de bloques, el algoritmo de consenso por Prueba de Trabajo (Proof of Work), el protocolo de red P2P y el sistema de gestión de carteras. El objetivo de Rudag Core es proporcionar una implementación de referencia clara y funcional de los principios fundamentales que sustentan a las criptomonedas como Bitcoin.

---

## 1. Introducción

Desde la aparición de Bitcoin, la tecnología blockchain ha demostrado un potencial transformador en diversas industrias. Sin embargo, la complejidad inherente de los protocolos más establecidos puede representar una barrera de entrada para desarrolladores, estudiantes e investigadores. 

Rudag Core nace con la motivación de desmitificar esta tecnología, ofreciendo un sistema de blockchain completo pero comprensible. Este proyecto sirve como una herramienta práctica para explorar los mecanismos de consenso, la criptografía de clave pública y las redes distribuidas que hacen posible la existencia de las criptomonedas.

## 2. Componentes Centrales

### 2.1. Blockchain y Bloques

La blockchain de Rudag es una cadena de bloques enlazados secuencialmente, donde cada bloque contiene una referencia criptográfica al bloque anterior (su *hash*). Esta estructura garantiza la inmutabilidad de la historia de las transacciones.

Un bloque en Rudag Core se compone de:
- **Índice:** La posición del bloque en la cadena.
- **Hash Anterior:** El hash del bloque precedente, asegurando la integridad de la cadena.
- **Transacciones:** Una lista de transacciones incluidas en el bloque.
- **Timestamp:** La marca de tiempo de la creación del bloque.
- **Nonce:** Un número arbitrario utilizado en el proceso de minería para satisfacer el requisito de la Prueba de Trabajo.

### 2.2. Transacciones

Una transacción es una transferencia de valor entre direcciones de la red. El modelo de Rudag Core es un sistema basado en cuentas (similar a Ethereum en su simplicidad, aunque sin la complejidad de los contratos inteligentes en esta fase).

Cada transacción contiene:
- **Remitente (`envia`):** La dirección que envía los fondos.
- **Destinatario (`recibe`):** La dirección que recibe los fondos.
- **Monto:** La cantidad de RGD transferida.
- **Comisión (`fee`):** Una pequeña cantidad pagada al minero por incluir la transacción en un bloque.
- **Timestamp:** La marca de tiempo de la transacción.

Además, existe un tipo especial de transacción llamada **coinbase**, que es creada por el minero de un bloque para reclamar la recompensa del bloque y las comisiones acumuladas.

### 2.3. Prueba de Trabajo (Proof of Work - PoW)

Rudag Core utiliza un algoritmo de consenso PoW para asegurar la red. Para añadir un nuevo bloque a la cadena, los nodos (mineros) deben encontrar un valor `nonce` tal que el hash SHA-256 del bloque completo comience con un número predefinido de ceros. Este número de ceros está determinado por el parámetro de `dificultad`.

Este proceso requiere una cantidad significativa de poder computacional, lo que previene que actores maliciosos puedan alterar la historia de la blockchain. El primer minero que encuentra un `nonce` válido transmite el bloque a la red, y si es validado, lo añade a su cadena y recibe la recompensa.

## 3. Red P2P

Rudag Core opera sobre una red de nodos peer-to-peer (P2P) donde todos los participantes son iguales.

### 3.1. Comunicación entre Nodos

Los nodos se comunican a través de una API RESTful. Cuando un nodo realiza una acción relevante (como minar un bloque o crear una transacción), la transmite (broadcast) al resto de los nodos conocidos en la red.

### 3.2. Descubrimiento de Nodos

Un nodo puede descubrir a otros de las siguientes maneras:
- **Añadiendo manualmente:** Un usuario puede añadir la dirección de un nodo conocido.
- **Descubrimiento automático:** Cuando un nodo se conecta a otro, puede solicitar su lista de peers conocidos. La red comparte activamente listas de nodos para asegurar una buena conectividad.

### 3.3. Sincronización de la Blockchain

El consenso en la red se mantiene a través de la regla de la "cadena más larga". Un nodo siempre considerará como válida la cadena de bloques más larga que conozca y que cumpla con todas las reglas de validación. Periódicamente, los nodos consultan a sus peers para verificar si existe una cadena más larga y, de ser así, la descargan y la adoptan como su versión de la verdad.

## 4. Carteras y Direcciones

### 4.1. Generación de Direcciones

Las direcciones en la red Rudag (RGD) están diseñadas para ser análogas a las direcciones de Bitcoin, utilizando criptografía de curva elíptica.

El proceso es el siguiente:
1.  Se genera un par de claves (privada y pública) usando el algoritmo **ECDSA** sobre la curva `SECP256k1`.
2.  La clave pública se hashea con **SHA-256**.
3.  El resultado anterior se hashea con **RIPEMD-160**.
4.  Se añade un byte de versión al principio del hash.
5.  Se calcula un *checksum* aplicando un doble hash **SHA-256** a los datos versionados y tomando los primeros 4 bytes.
6.  La dirección binaria final (datos versionados + checksum) se codifica en **Base58Check** para obtener la dirección RGD final.

### 4.2. Gestión de Carteras

El `wallet_manager` se encarga de crear, almacenar y gestionar las carteras. Cada cartera contiene el par de claves y un nombre asociado. En la implementación actual, las claves privadas se almacenan en texto plano, pero se planea su cifrado en futuras versiones.

## 5. Política Monetaria

La política monetaria de Rudag Core está definida en el archivo `config.json` y sigue principios deflacionarios.

- **Suministro Máximo (`max_supply`):** Fijado en **21,000,000 RGD**.
- **Recompensa por Bloque (`initial_reward`):** La recompensa inicial es de **50 RGD** por bloque.
- **Halving:** La recompensa por bloque se reduce a la mitad cada **210,000 bloques**. Este mecanismo asegura que la emisión de nuevas monedas disminuya con el tiempo, creando escasez.

## 6. Futuro del Proyecto

Rudag Core es una base sobre la cual se pueden construir funcionalidades más avanzadas. Los planes futuros incluyen la implementación de un ajuste dinámico de la dificultad, el cifrado de claves privadas, la creación de una GUI para la cartera y la investigación de mecanismos de consenso alternativos. Para más detalles, consulte nuestro `roadmap.md`.

## 7. Conclusión

Rudag Core logra su objetivo de ser una implementación funcional y educativa de una blockchain. A través de su código modular y su CLI interactiva, ofrece una plataforma accesible para aprender y experimentar con los componentes clave de la tecnología de registro distribuido. El proyecto sienta las bases para futuras exploraciones y desarrollos en el campo de las criptomonedas.
