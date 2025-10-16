# Roadmap de Rudag Core

Este documento describe la hoja de ruta de desarrollo para el proyecto Rudag Core. La visión es evolucionar desde una blockchain educativa y funcional hacia un ecosistema más robusto, seguro y con mayores capacidades.

---

### ✔️ **Q4 2025: Lanzamiento y Fundación (Versión 1.0)**

- [x] **Implementación del Núcleo:** Desarrollo de la estructura de bloques y la cadena principal.
- [x] **Consenso PoW:** Implementación del algoritmo de Prueba de Trabajo (Proof of Work).
- [x] **Red P2P Básica:** Creación de la red de nodos con capacidad de broadcast y sincronización.
- [x] **Gestión de Wallets:** Funcionalidades para crear, importar y exportar carteras.
- [x] **CLI Interactiva:** Lanzamiento de la primera versión de la interfaz de línea de comandos.
- [x] **Publicación en GitHub:** Liberación del código fuente a la comunidad.

---

### ⏳ **Q1 2026: Mejoras en la Red y Seguridad**

- [ ] **Ajuste Dinámico de Dificultad:** Implementar un algoritmo que ajuste la dificultad de minado automáticamente para mantener un tiempo de bloque constante (aprox. 60 segundos).
- [ ] **Cifrado de Wallets:** Añadir cifrado con contraseña para las claves privadas en el archivo `wallets.json` para mejorar la seguridad.
- [ ] **Sistema de Reputación de Nodos:** Desarrollar un sistema de puntuación para priorizar la conexión con nodos fiables y penalizar a los maliciosos.
- [ ] **Validación de Transacciones Mejorada:** Introducir comprobaciones más estrictas para las transacciones, incluyendo la verificación de firmas digitales.

---

### ⏳ **Q2 2026: Experiencia de Usuario y Herramientas**

- [ ] **GUI Wallet de Escritorio:** Desarrollar una cartera con interfaz gráfica de usuario para una gestión más intuitiva de los fondos y las transacciones.
- [ ] **Explorador de Bloques Web:** Crear una aplicación web para visualizar la blockchain, buscar transacciones, bloques y direcciones.
- [ ] **Documentación Avanzada:** Publicar guías detalladas, tutoriales y una documentación completa de la API.
- [ ] **Tests Unitarios y de Integración:** Aumentar la cobertura de tests para garantizar la estabilidad y fiabilidad del código base.

---

### ⏳ **Q3 2026: Funcionalidades Avanzadas**

- [ ] **Investigación de Consenso Alternativo:** Estudiar la viabilidad de implementar un mecanismo de consenso híbrido o migrar a Pruebade Participación (Proof of Stake - PoS).
- [ ] **Capacidades de Scripting en Transacciones:** Introducir un lenguaje de script simple (similar a Bitcoin Script) para permitir transacciones más complejas como multifirma.
- [ ] **Implementación de Cliente Ligero (SPV):** Desarrollar un modo de cliente que no necesite descargar toda la blockchain para operar.

---

### ⏳ **Q4 2026 y Más Allá: Crecimiento del Ecosistema**

- [ ] **Fomentar la Comunidad:** Crear canales de comunicación (Discord, Telegram) para desarrolladores y usuarios.
- [ ] **Programa de Recompensas (Bounties):** Establecer un programa para recompensar a quienes encuentren bugs o desarrollen nuevas características.
- [ ] **Integraciones y APIs para Desarrolladores:** Facilitar la creación de aplicaciones y servicios sobre la blockchain de Rudag Core.
- [ ] **Gobernanza Descentralizada:** Investigar un modelo de gobernanza que permita a la comunidad participar en las decisiones futuras del protocolo.
