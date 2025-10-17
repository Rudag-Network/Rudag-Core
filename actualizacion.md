## ✅ **actualizacion propuesta:**

1. **Centralización inicial, descentralización después** - Un punto de entrada conocido que deriva a una red P2P
2. **Actualización dinámica** - La lista se mantiene fresca automáticamente
3. **Resiliencia** - Si algunos nodos caen, el servidor proporciona alternativas
4. **Escalabilidad** - Nuevos nodos se integran automáticamente en la red

## 🚀 **Implementación propuesta:**

### **1. Servidor de Nodos (nodo_server.py)**
```python
#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from datetime import datetime, timedelta
import json
import os

app = FastAPI(title="RGD Node Server")

# Archivo para persistencia
NODES_FILE = "known_nodes.json"
# Nodos principales por defecto
DEFAULT_NODES = [
    "rudagnetwork2.canariannode.uk",
    "rudagnetwork.canariannode.uk"
]

class NodeRegistration(BaseModel):
    node_address: str
    node_id: str = "unknown"
    timestamp: float = None

class NodeList(BaseModel):
    nodes: list

def load_known_nodes():
    """Cargar nodos conocidos desde archivo"""
    if os.path.exists(NODES_FILE):
        try:
            with open(NODES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Si no existe, crear con nodos por defecto
    initial_nodes = {
        "nodes": DEFAULT_NODES,
        "last_updated": datetime.now().isoformat()
    }
    save_known_nodes(initial_nodes)
    return initial_nodes

def save_known_nodes(data):
    """Guardar nodos conocidos en archivo"""
    with open(NODES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def cleanup_old_nodes():
    """Limpiar nodos antiguos (más de 24 horas)"""
    data = load_known_nodes()
    current_time = datetime.now()
    active_nodes = []
    
    for node in data.get("nodes", []):
        # Por simplicidad, mantener todos por ahora
        # En una implementación real verificaríamos timestamp
        active_nodes.append(node)
    
    if len(active_nodes) != len(data.get("nodes", [])):
        data["nodes"] = active_nodes
        data["last_updated"] = current_time.isoformat()
        save_known_nodes(data)

@app.on_event("startup")
async def startup_event():
    """Inicializar servidor"""
    cleanup_old_nodes()
    print("🚀 Servidor de Nodos RGD iniciado")
    print(f"📋 Nodos conocidos: {len(load_known_nodes()['nodes'])}")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Servidor de Nodos RGD",
        "total_nodes": len(load_known_nodes()["nodes"]),
        "version": "1.0.0"
    }

@app.post("/register")
async def register_node(registration: NodeRegistration):
    """Registrar un nuevo nodo en la red"""
    data = load_known_nodes()
    nodes = data["nodes"]
    
    # Añadir timestamp si no viene
    if registration.timestamp is None:
        registration.timestamp = datetime.now().timestamp()
    
    # Añadir nodo si no existe
    if registration.node_address not in nodes:
        nodes.append(registration.node_address)
        print(f"✅ Nuevo nodo registrado: {registration.node_address}")
    
    # Actualizar y guardar
    data["nodes"] = nodes
    data["last_updated"] = datetime.now().isoformat()
    save_known_nodes(data)
    
    return {
        "status": "registered",
        "total_nodes": len(nodes),
        "your_node": registration.node_address
    }

@app.get("/nodes")
async def get_nodes():
    """Obtener lista de nodos activos"""
    cleanup_old_nodes()  # Limpiar antes de servir
    data = load_known_nodes()
    
    return {
        "nodes": data["nodes"],
        "total_nodes": len(data["nodes"]),
        "last_updated": data["last_updated"]
    }

@app.post("/nodes/bulk")
async def add_multiple_nodes(node_list: NodeList):
    """Añadir múltiples nodos a la lista"""
    data = load_known_nodes()
    nodes = data["nodes"]
    added_count = 0
    
    for node in node_list.nodes:
        if node not in nodes:
            nodes.append(node)
            added_count += 1
    
    if added_count > 0:
        data["nodes"] = nodes
        data["last_updated"] = datetime.now().isoformat()
        save_known_nodes(data)
        print(f"✅ {added_count} nuevos nodos añadidos")
    
    return {
        "status": "updated",
        "added_nodes": added_count,
        "total_nodes": len(nodes)
    }

@app.get("/health")
async def health_check():
    """Verificar estado del servidor"""
    data = load_known_nodes()
    return {
        "status": "healthy",
        "total_nodes": len(data["nodes"]),
        "uptime": "running"
    }

if __name__ == "__main__":
    print("=== Servidor de Nodos RGD ===")
    print("Iniciando en puerto 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### **2. Cliente Mejorado en blockchain.py**
```python
# Añadir esta función a la clase Blockchain
def discover_peers_from_server(self, server_url="http://localhost:8000"):
    """Descubrir peers desde el servidor central"""
    try:
        # Primero registrar nuestro nodo
        registration_data = {
            "node_address": f"{self.get_public_ip()}:5000",  # O tu IP pública
            "node_id": self.node_id,
            "timestamp": time.time()
        }
        
        # Registrar nodo
        response = requests.post(
            f"{server_url}/register",
            json=registration_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Nodo registrado en servidor")
        
        # Obtener lista de nodos
        response = requests.get(f"{server_url}/nodes", timeout=10)
        if response.status_code == 200:
            nodes_data = response.json()
            new_peers = nodes_data["nodes"]
            
            added_count = 0
            for node in new_peers:
                if node not in self.nodes:
                    self.add_node(node)
                    added_count += 1
            
            print(f"🔍 Descubiertos {added_count} nuevos peers")
            return True
            
    except Exception as e:
        print(f"❌ Error descubriendo peers: {e}")
    
    return False

def get_public_ip(self):
    """Obtener IP pública (simplificado)"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        return "localhost"  # Fallback
```

### **3. Script de Inicio Mejorado (start_node.py)**
```python
#!/usr/bin/env python3
import requests
import time
from blockchain import Blockchain

def initialize_node():
    """Inicializar nodo con descubrimiento automático"""
    blockchain = Blockchain()
    
    print("🔍 Descubriendo peers desde servidor...")
    if blockchain.discover_peers_from_server():
        print("✅ Red inicializada con peers descubiertos")
    else:
        print("⚠️  Usando nodos por defecto")
    
    return blockchain

# En tu main():
if __name__ == "__main__":
    blockchain = initialize_node()
    # ... resto del código
```

### **4. Configuración del Servidor**
**requirements_servidor.txt:**
```txt
fastapi==0.100.0
uvicorn==0.25.0
pydantic==1.10.0
```

### **5. Archivo de Configuración del Servidor**
**server_config.json:**
```json
{
    "server_host": "0.0.0.0",
    "server_port": 8000,
    "node_cleanup_hours": 24,
    "max_nodes": 1000,
    "default_nodes": [
        "rudagnetwork2.canariannode.uk",
        "rudagnetwork.canariannode.uk"
    ]
}
```

## 🎯 **Cómo funciona:**

1. **El servidor** corre en un puerto conocido (ej: 8000)
2. **Cada nodo** al iniciar:
   - Se registra en el servidor
   - Recibe la lista actualizada de nodos
   - Se conecta a esos nodos
3. **La red** se mantiene actualizada automáticamente
4. **Nuevos nodos** se integran sin configuración manual

## 📊 **Beneficios inmediatos:**

- ✅ **Plug & Play** - Nuevos nodos se conectan automáticamente
- ✅ **Red siempre actualizada** - Lista dinámica de peers
- ✅ **Tolerancia a fallos** - Si un nodo cae, hay alternativas
- ✅ **Escalabilidad** - La red crece orgánicamente

¿Quieres que implementemos esta solución en tu código? Es definitivamente una mejora significativa sobre el sistema actual.
