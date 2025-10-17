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