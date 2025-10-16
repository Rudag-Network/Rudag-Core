# Rudag Core - Blockchain Interactiva

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

```
╔══════════════════════════════════════════════╗
║             RUDAG CORE 1.0.0.1              ║
║           Blockchain Interactive CLI         ║
║                                              ║
║      ██████╗ ██╗   ██╗██████╗  █████╗       ║
║      ██╔══██╗██║   ██║██╔══██╗██╔══██╗      ║
║      ██████╔╝██║   ██║██║  ██║███████║      ║
║      ██╔══██╗██║   ██║██║  ██║██╔══██║      ║
║      ██║  ██║╚██████╔╝██████╔╝██║  ██║      ║
║      ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝      ║
╚══════════════════════════════════════════════╝
```

**Una implementación de blockchain desde cero con una CLI interactiva para una fácil gestión.**

**Repositorio Oficial:** [https://github.com/Rudag-Network/Rudag-Core](https://github.com/Rudag-Network/Rudag-Core)

</div>

## 📜 Descripción General

Rudag Core es un proyecto de blockchain funcional construido en Python. Implementa los conceptos fundamentales de una criptomoneda, incluyendo una cadena de bloques, transacciones, minería con Prueba de Trabajo (Proof of Work), una red P2P para la sincronización entre nodos y un sistema de gestión de carteras.

El proyecto está diseñado para ser educativo y demostrativo, proporcionando una API RESTful para la interacción programática y una completa Interfaz de Línea de Comandos (CLI) para facilitar la gestión y operación del nodo.

## ✨ Características Principales

- **Blockchain Funcional:** Cadena de bloques inmutable con bloques enlazados criptográficamente.
- **Prueba de Trabajo (PoW):** Algoritmo de consenso para la creación de nuevos bloques.
- **Transacciones:** Soporte para transacciones entre carteras con cálculo de comisiones (fees).
- **Red P2P:** Sincronización automática de la cadena de bloques y descubrimiento de nodos (peers) en la red.
- **Gestión de Wallets:** Creación, listado, exportación, importación y backups de carteras.
- **Recompensas de Minería:** Los mineros son recompensados con nuevas monedas y las comisiones de las transacciones.
- **API RESTful:** Endpoints para interactuar con el nodo y la blockchain a través de HTTP.
- **CLI Interactiva:** Una interfaz de usuario amigable en la terminal para gestionar todas las funcionalidades del nodo.

## 🚀 Cómo Empezar

Sigue estos pasos para poner en marcha tu propio nodo de Rudag Core.

### 1. Prerrequisitos

- Python 3.7+
- `pip` y `venv` (generalmente incluidos con Python)

### 2. Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/Rudag-Network/Rudag-Core.git
    cd Rudag-Core
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *En Windows, usa `venv\Scripts\activate`.*

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Haz los scripts ejecutables (en Linux/macOS):**
    ```bash
    chmod +x addnode.sh RudagCoreV2.py
    ```

### 3. Uso

Para operar el nodo, necesitarás dos terminales.

1.  **Terminal 1: Inicia el Nodo Blockchain**
    Este comando inicia el servidor web y los servicios de red. Mantenlo en ejecución.
    ```bash
    python3 blockchain.py
    ```

2.  **Terminal 2: Lanza la CLI Interactiva**
    Usa esta terminal para interactuar con tu nodo.
    ```bash
    python3 RudagCoreV2.py
    ```
    Aparecerá un menú desde el cual podrás gestionar el nodo, las wallets, minar bloques y mucho más.

### 4. Configuración del Firewall (Opcional pero Recomendado)

Para asegurar que tu nodo pueda comunicarse con otros nodos en la red, es importante configurar tu firewall para permitir el tráfico en el puerto `5000`.

Aquí tienes un ejemplo para `ufw` (Uncomplicated Firewall) en sistemas basados en Debian/Ubuntu:

1.  **Instala UFW:**
    ```bash
    sudo apt-get update
    sudo apt-get install ufw
    ```

2.  **Permite el tráfico en el puerto 5000:**
    ```bash
    sudo ufw allow 5000/tcp
    sudo ufw allow 5000/udp
    ```

3.  **Activa el firewall:**
    ```bash
    sudo ufw enable
    ```

4.  **Verifica el estado:**
    ```bash
    sudo ufw status
    ```
    Deberías ver que el puerto 5000 está permitido.

**Nota:** Si usas un sistema operativo diferente o un firewall distinto, consulta su documentación para abrir los puertos correspondientes.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si deseas mejorar Rudag Core, siéntete libre de abrir un *Pull Request* o reportar un *Issue*.

1.  Haz un *fork* del proyecto.
2.  Crea tu propia rama (`git checkout -b feature/NuevaCaracteristica`).
3.  Realiza tus cambios (`git commit -m 'Añadir nueva característica'`).
4.  Haz *push* a tu rama (`git push origin feature/NuevaCaracteristica`).
5.  Abre un *Pull Request*.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.