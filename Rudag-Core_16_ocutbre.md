# CÓDIGOS COMPLETOS DEL PROYECTO RGD CORREGIDOS

## 📁 **Estructura del Proyecto**
```
Rudag-Core/
├── config.json
├── core.py
├── network_manager.py
├── blockchain.py
├── wallet_manager.py
├── addnode.sh
├── blockchain.json
├── requirements.txt
├── wallets/
└── RudagCoreV2.py
```

## 1. **config.json**
```json
{
    "blockchain_name": "Rudag Network",
    "ticker": "RGD",
    "symbol": "⚡",
    "version": "1.0.0",
    "max_supply": 21000000,
    "initial_reward": 50,
    "genesis_reward": 500,
    "halving_interval": 210000,
    "block_time": 60,
    "initial_difficulty": "0000",
    "transaction_fee": 0.001,
    "max_transactions_per_block": 1000,
    "address_version_byte": "0x00",
    "blockchain_file": "blockchain.json",
    "wallet_dir": "wallets",
    "genesis_address": "RGD:1A77LFiAzzVnDdpMRjKqwB3ZjiVnuNqQjk",
    "automatic_peer_discovery": true,
    "share_peers_interval": 300
}
```

## 2. **core.py**
```python
import json
import os
import requests
import time
from hashlib import sha256
from urllib.parse import urlparse
import ecdsa
import base58
import hashlib

# Cargar configuración RGD
with open('config.json', 'r') as f:
    config = json.load(f)

class RGDBlockchainConfig:
    NAME = config['blockchain_name']
    TICKER = config['ticker']
    SYMBOL = config['symbol']
    VERSION = config['version']
    MAX_SUPPLY = config['max_supply']
    INITIAL_REWARD = config['initial_reward']
    GENESIS_REWARD = config['genesis_reward']
    HALVING_INTERVAL = config['halving_interval']
    BLOCK_TIME = config['block_time']
    TRANSACTION_FEE = config['transaction_fee']
    MAX_TX_PER_BLOCK = config['max_transactions_per_block']
    BLOCKCHAIN_FILE = config['blockchain_file']
    GENESIS_ADDRESS = config['genesis_address']
    AUTOMATIC_PEER_DISCOVERY = config['automatic_peer_discovery']

def hash_bloque(bloque):
    bloque_encode = json.dumps(bloque, sort_keys=True).encode()
    return sha256(bloque_encode).hexdigest()

def calculate_reward(block_height):
    """Calcula la recompensa según el halving schedule de RGD"""
    if block_height == 0:
        return RGDBlockchainConfig.GENESIS_REWARD
    
    halving_epoch = (block_height - 1) // RGDBlockchainConfig.HALVING_INTERVAL
    reward = RGDBlockchainConfig.INITIAL_REWARD / (2 ** halving_epoch)
    return reward

def create_rgd_address():
    """Genera una dirección RGD estilo Bitcoin"""
    # Generar clave privada
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    public_key = private_key.get_verifying_key().to_string()
    
    # SHA-256 + RIPEMD-160
    sha256_hash = sha256(public_key).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    
    # Añadir versión byte
    versioned_hash = b'\x00' + ripemd160_hash
    
    # Doble SHA-256 para checksum
    checksum = sha256(sha256(versioned_hash).digest()).digest()[:4]
    
    # Codificar en Base58
    binary_address = versioned_hash + checksum
    rgd_address = base58.b58encode(binary_address).decode('utf-8')
    
    return f"RGD:{rgd_address}"

class Bloque:
    def __init__(self, indice, hash_anterior, transacciones, tiempo, nonce):
        self.indice = indice 
        self.hash_anterior = hash_anterior 
        self.transacciones = transacciones 
        self.tiempo = tiempo 
        self.nonce = nonce

class Blockchain:
    dificultad = config['initial_difficulty']

    def __init__(self, node_id="unknown"):
        self.node_id = node_id
        self.nodes = set()
        self.chain = []
        self.transacciones_pendientes = []
        self.load_blockchain()
    
    def load_blockchain(self):
        """Cargar blockchain desde archivo si existe"""
        if os.path.exists(RGDBlockchainConfig.BLOCKCHAIN_FILE):
            try:
                with open(RGDBlockchainConfig.BLOCKCHAIN_FILE, 'r') as f:
                    data = json.load(f)
                    self.chain = data['chain']
                    self.nodes = set(data['nodes'])
                    self.transacciones_pendientes = data['transacciones_pendientes']
                print(f"✅ Blockchain cargada desde {RGDBlockchainConfig.BLOCKCHAIN_FILE}")
                print(f"📦 Bloques: {len(self.chain)} | Nodos: {len(self.nodes)}")
                return
            except Exception as e:
                print(f"❌ Error cargando blockchain: {e}")
        
        # Si no existe, crear bloque génesis
        self.create_genesis_block()

    def save_blockchain(self):
        """Guardar blockchain en archivo"""
        data = {
            'chain': self.chain,
            'nodes': list(self.nodes),
            'transacciones_pendientes': self.transacciones_pendientes
        }
        try:
            with open(RGDBlockchainConfig.BLOCKCHAIN_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error guardando blockchain: {e}")
            return False

    def create_genesis_block(self, genesis_wallet_address=None):
        """Crear bloque génesis FIJO"""
        # USAR SIEMPRE LA DIRECCIÓN GÉNESIS FIJA
        genesis_wallet_address = RGDBlockchainConfig.GENESIS_ADDRESS
        
        mensaje_genesis = f"""RUDAG_GENESIS_BLOCK: 
        {RGDBlockchainConfig.NAME} - {RGDBlockchainConfig.TICKER}
        Bloque Génesis - Recompensa: {RGDBlockchainConfig.GENESIS_REWARD} {RGDBlockchainConfig.SYMBOL}
        Timestamp: {time()}
        Dirección Génesis Fija: {genesis_wallet_address}"""
        
        hash_genesis = hash_bloque(mensaje_genesis)
        
        # Transacción coinbase del génesis
        genesis_transaction = {
            'tipo': 'coinbase',
            'recompensa': RGDBlockchainConfig.GENESIS_REWARD,
            'fees': 0,
            'destino': genesis_wallet_address,
            'timestamp': time()
        }
        
        genesis_block = self.proof_of_work(0, hash_genesis, [genesis_transaction], time())
        self.nuevo_bloque(genesis_block)
        self.save_blockchain()
        print(f"✅ Bloque génesis FIJO creado para: {genesis_wallet_address}")

    def proof_of_work(self, indice, hash_anterior, transacciones, tiempo):
        nonce = 0
        bloque = Bloque(indice, hash_anterior, transacciones, tiempo, nonce)
        while self.validar_pow(bloque.__dict__) is False:
            bloque.nonce += 1
        return bloque

    def validar_pow(self, bloque):
        hash_bloque_nuevo = hash_bloque(bloque)
        return hash_bloque_nuevo[:len(self.dificultad)] == self.dificultad

    def nuevo_bloque(self, bloque):
        # Verificar límite de transacciones
        if len(bloque.transacciones) > RGDBlockchainConfig.MAX_TX_PER_BLOCK:
            raise Exception(f"Límite de transacciones excedido: {RGDBlockchainConfig.MAX_TX_PER_BLOCK}")
        
        self.transacciones_pendientes = []
        self.chain.append(bloque.__dict__)
        self.save_blockchain()
        return bloque    

    def add_transaction(self, envia, recibe, monto, fee=RGDBlockchainConfig.TRANSACTION_FEE):
        # Verificar formato de dirección RGD
        if not recibe.startswith('RGD:'):
            raise Exception("Formato de dirección RGD inválido")
        
        # Verificar fee mínimo
        if fee < RGDBlockchainConfig.TRANSACTION_FEE:
            raise Exception(f"Fee mínimo requerido: {RGDBlockchainConfig.TRANSACTION_FEE} RGD")
        
        transaction_data = {
            'monto': monto,
            'recibe': recibe,
            'envia': envia,
            'fee': fee,
            'timestamp': time.time(),
            'hash': None
        }
        
        self.transacciones_pendientes.append(transaction_data)
        self.save_blockchain()
        return self.last_block['indice'] + 1

    @property
    def last_block(self):
        return self.chain[-1] if self.chain else None

    def add_node(self, address):
        parsed_url = urlparse(address)
        # Extraer solo el hostname para almacenamiento consistente
        node_address = parsed_url.netloc or parsed_url.path
        
        if node_address not in self.nodes:
            self.nodes.add(node_address)
            self.save_blockchain()
            print(f"✅ Nodo añadido: {node_address}")
            
            # Compartir automáticamente con otros nodos si está habilitado
            if RGDBlockchainConfig.AUTOMATIC_PEER_DISCOVERY:
                self._share_new_node_with_peers(node_address)
        else:
            print(f"⏭️  Nodo ya existe: {node_address}")

    def _share_new_node_with_peers(self, new_node):
        """Compartir nuevo nodo con otros peers de la red"""
        print(f"🔄 Compartiendo nuevo nodo {new_node} con la red...")
        for node in list(self.nodes):
            if node != new_node:  # No enviar a sí mismo
                try:
                    # Enviar mensaje de nuevo peer a nodos existentes
                    requests.post(
                        f"http://{node}/network/receive",
                        json={
                            'type': 'new_peer',
                            'data': {'node': new_node},
                            'timestamp': time.time(),
                            'node_id': self.node_id
                        },
                        timeout=5
                    )
                    print(f"✅ Nodo {new_node} compartido con {node}")
                except Exception as e:
                    print(f"❌ Error compartiendo nodo con {node}: {e}")

    def share_peers_list(self, target_node):
        """Compartir lista completa de peers con un nodo específico"""
        try:
            requests.post(
                f"http://{target_node}/network/receive",
                json={
                    'type': 'peers_list',
                    'data': {'peers': list(self.nodes)},
                    'timestamp': time.time(),
                    'node_id': self.node_id
                },
                timeout=5
            )
            print(f"✅ Lista de peers compartida con {target_node}")
        except Exception as e:
            print(f"❌ Error compartiendo peers con {target_node}: {e}")

    def update_blockchain(self):
        """Sincronizar con la cadena más larga válida"""
        neighbours = self.nodes
        new_chain = None 
        max_length = len(self.chain)
        
        print(f"🔍 Buscando cadenas más largas en {len(neighbours)} nodos...")
        
        for node in neighbours:
            try:
                print(f"🔄 Consultando nodo: {node}")
                
                # Intentar tanto HTTP como HTTPS
                protocols = ['https', 'http']
                success = False
                
                for protocol in protocols:
                    try:
                        url = f"{protocol}://{node}/chain"
                        response = requests.get(url, timeout=15)
                        if response.status_code == 200:
                            node_data = response.json()
                            length = node_data['largo']
                            chain = node_data['chain']
                            
                            print(f"📊 Nodo {node} ({protocol}): {length} bloques")
                            
                            if length > max_length and self.valid_chain(chain):
                                max_length = length
                                new_chain = chain
                                print(f"✅ Cadena más larga encontrada: {length} bloques")
                            
                            success = True
                            break
                    except Exception as e:
                        print(f"   ❌ {protocol}://{node} falló: {e}")
                        continue
                
                if not success:
                    print(f"❌ No se pudo conectar a {node} con ningún protocolo")
                        
            except Exception as e:
                print(f"❌ Error consultando nodo {node}: {e}")
        
        if new_chain:
            print(f"🔄 Actualizando cadena local a {max_length} bloques")
            self.chain = new_chain
            self.save_blockchain()
            
            # Limpiar transacciones pendientes que ya están en la nueva cadena
            self._cleanup_pending_transactions()
            
            return True
        
        print("✅ Nuestra cadena es la más actualizada")
        return False

    def _cleanup_pending_transactions(self):
        """Limpiar transacciones pendientes que ya están en bloques confirmados"""
        confirmed_transactions = []
        for block in self.chain:
            confirmed_transactions.extend(block.get('transacciones', []))
        
        new_pending = []
        for pending_tx in self.transacciones_pendientes:
            is_confirmed = False
            for confirmed_tx in confirmed_transactions:
                if (pending_tx.get('envia') == confirmed_tx.get('envia') and
                    pending_tx.get('recibe') == confirmed_tx.get('recibe') and
                    pending_tx.get('monto') == confirmed_tx.get('monto')):
                    is_confirmed = True
                    break
            
            if not is_confirmed:
                new_pending.append(pending_tx)
        
        removed_count = len(self.transacciones_pendientes) - len(new_pending)
        if removed_count > 0:
            print(f"🧹 {removed_count} transacciones limpiadas (ya confirmadas)")
        
        self.transacciones_pendientes = new_pending
        self.save_blockchain()

    def valid_chain(self, chain):
        """Validar una cadena completa"""
        if not chain:
            return False
            
        # Verificar bloque génesis - DEBE SER EL FIJADO
        if chain[0]['indice'] != 0:
            return False
            
        # Verificar dirección génesis correcta
        genesis_tx = chain[0]['transacciones'][0]
        if genesis_tx.get('destino') != RGDBlockchainConfig.GENESIS_ADDRESS:
            print(f"❌ Bloque génesis incorrecto. Esperado: {RGDBlockchainConfig.GENESIS_ADDRESS}")
            return False
            
        # Verificar cada bloque subsequente
        for i in range(1, len(chain)):
            block = chain[i]
            previous_block = chain[i-1]
            
            # Verificar hash anterior
            if block['hash_anterior'] != hash_bloque(previous_block):
                return False
                
            # Verificar proof of work
            if not self.validar_pow(block):
                return False
                
        return True

    def get_current_reward(self):
        """Obtiene la recompensa actual según la altura del bloque"""
        return calculate_reward(len(self.chain))

    def get_network_info(self):
        """Retorna información de la red RGD"""
        return {
            'name': RGDBlockchainConfig.NAME,
            'ticker': RGDBlockchainConfig.TICKER,
            'symbol': RGDBlockchainConfig.SYMBOL,
            'version': RGDBlockchainConfig.VERSION,
            'block_height': len(self.chain),
            'current_reward': self.get_current_reward(),
            'total_supply': self.get_total_supply(),
            'max_supply': RGDBlockchainConfig.MAX_SUPPLY,
            'difficulty': self.dificultad,
            'nodes': list(self.nodes),
            'pending_transactions': len(self.transacciones_pendientes),
            'genesis_address': RGDBlockchainConfig.GENESIS_ADDRESS
        }

    def reset_blockchain(self, genesis_wallet_address=None):
        """Reinicia la blockchain - SIEMPRE usa la dirección génesis fija"""
        # IGNORAR el parámetro y usar siempre la dirección fija
        genesis_wallet_address = RGDBlockchainConfig.GENESIS_ADDRESS
        
        self.chain = []
        self.nodes = set()
        self.transacciones_pendientes = []
        self.create_genesis_block(genesis_wallet_address)
        self.save_blockchain()
        
        print(f"✅ Blockchain reiniciada con dirección génesis fija: {genesis_wallet_address}")

    def get_total_supply(self):
        """Calcular el supply total recorriendo todos los bloques"""
        total = 0
        for block in self.chain:
            for tx in block.get('transacciones', []):
                if tx.get('tipo') == 'coinbase':
                    total += tx.get('recompensa', 0)
        return total
```

## 3. **network_manager.py**
```python
import requests
import time
import json
from threading import Thread
from queue import Queue
import hashlib

class NetworkManager:
    def __init__(self, blockchain, wallet_manager):
        self.blockchain = blockchain
        self.wallet_manager = wallet_manager
        self.message_queue = Queue()
        self.running = True
        self.broadcast_delay = 2  # segundos entre broadcasts
        self.peer_discovery_enabled = True
        
    def start_network_services(self):
        """Iniciar servicios de red en segundo plano"""
        self.broadcast_thread = Thread(target=self._broadcast_worker, daemon=True)
        self.sync_thread = Thread(target=self._sync_worker, daemon=True)
        self.peer_discovery_thread = Thread(target=self._peer_discovery_worker, daemon=True)
        
        self.broadcast_thread.start()
        self.sync_thread.start()
        self.peer_discovery_thread.start()
        
        print("🔄 Servicios de red iniciados (broadcast, sync, peer discovery)")
    
    def stop_network_services(self):
        """Detener servicios de red"""
        self.running = False
        print("🛑 Servicios de red detenidos")
    
    def _broadcast_worker(self):
        """Trabajador para broadcast de mensajes"""
        while self.running:
            try:
                if not self.message_queue.empty():
                    message = self.message_queue.get()
                    self._broadcast_message(message)
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ Error en broadcast worker: {e}")
    
    def _sync_worker(self):
        """Trabajador para sincronización periódica"""
        sync_interval = 30  # sincronizar cada 30 segundos
        last_sync = 0
        
        while self.running:
            try:
                current_time = time.time()
                if current_time - last_sync > sync_interval:
                    if self.blockchain.nodes:
                        self.sync_blockchain()
                    last_sync = current_time
                time.sleep(5)
            except Exception as e:
                print(f"❌ Error en sync worker: {e}")
    
    def _peer_discovery_worker(self):
        """Trabajador para descubrimiento automático de peers"""
        share_interval = 300  # Compartir peers cada 5 minutos
        last_share = 0
        
        while self.running:
            try:
                current_time = time.time()
                if current_time - last_share > share_interval and self.peer_discovery_enabled:
                    if self.blockchain.nodes:
                        self._share_peers_with_network()
                    last_share = current_time
                time.sleep(10)
            except Exception as e:
                print(f"❌ Error en peer discovery worker: {e}")
    
    def _share_peers_with_network(self):
        """Compartir lista de peers con toda la red"""
        print("🔄 Compartiendo lista de peers con la red...")
        for node in list(self.blockchain.nodes):
            try:
                self.blockchain.share_peers_list(node)
            except Exception as e:
                print(f"❌ Error compartiendo peers con {node}: {e}")
    
    def broadcast_new_block(self, block_data):
        """Transmitir nuevo bloque a la red"""
        message = {
            'type': 'new_block',
            'data': block_data,
            'timestamp': time.time(),
            'node_id': getattr(self.blockchain, 'node_id', 'unknown')
        }
        self.message_queue.put(message)
        print(f"📤 Transmitiendo bloque {block_data['indice']} a la red")
    
    def broadcast_new_transaction(self, transaction_data):
        """Transmitir nueva transacción a la red"""
        message = {
            'type': 'new_transaction',
            'data': transaction_data,
            'timestamp': time.time(),
            'node_id': getattr(self.blockchain, 'node_id', 'unknown')
        }
        self.message_queue.put(message)
        print(f"📤 Transmitiendo transacción a la red")
    
    def _broadcast_message(self, message):
        """Transmitir mensaje a todos los nodos"""
        for node in list(self.blockchain.nodes):
            try:
                # Intentar tanto HTTP como HTTPS
                protocols = ['https', 'http']
                success = False
                
                for protocol in protocols:
                    try:
                        url = f"{protocol}://{node}/network/receive"
                        response = requests.post(
                            url,
                            json=message,
                            timeout=5
                        )
                        if response.status_code == 200:
                            print(f"✅ Mensaje {message['type']} transmitido a {node} ({protocol})")
                            success = True
                            break
                    except Exception as e:
                        continue
                
                if not success:
                    print(f"❌ No se pudo transmitir a {node} con ningún protocolo")
                    
            except Exception as e:
                print(f"❌ Error en broadcast a {node}: {e}")
    
    def receive_message(self, message):
        """Procesar mensaje recibido de la red"""
        try:
            msg_type = message.get('type')
            data = message.get('data')
            sender = message.get('node_id')
            
            print(f"📥 Mensaje recibido de {sender}: {msg_type}")
            
            if msg_type == 'new_block':
                self._process_received_block(data, sender)
            elif msg_type == 'new_transaction':
                self._process_received_transaction(data, sender)
            elif msg_type == 'chain_request':
                self._handle_chain_request(sender)
            elif msg_type == 'chain_response':
                self._handle_chain_response(data, sender)
            elif msg_type == 'new_peer':
                self._process_new_peer(data, sender)
            elif msg_type == 'peers_list':
                self._process_peers_list(data, sender)
                
        except Exception as e:
            print(f"❌ Error procesando mensaje: {e}")
    
    def _process_new_peer(self, peer_data, sender):
        """Procesar nuevo peer recibido de otro nodo"""
        try:
            new_node = peer_data.get('node')
            if new_node and new_node not in self.blockchain.nodes:
                print(f"👥 Nuevo peer descubierto: {new_node}")
                self.blockchain.add_node(new_node)
                
                # Compartir nuestro conocimiento de peers con el nuevo nodo
                self.blockchain.share_peers_list(new_node)
                
        except Exception as e:
            print(f"❌ Error procesando nuevo peer: {e}")
    
    def _process_peers_list(self, peers_data, sender):
        """Procesar lista de peers recibida"""
        try:
            peers_list = peers_data.get('peers', [])
            new_peers_added = 0
            
            for peer in peers_list:
                if peer not in self.blockchain.nodes:
                    self.blockchain.add_node(peer)
                    new_peers_added += 1
            
            if new_peers_added > 0:
                print(f"👥 {new_peers_added} nuevos peers añadidos desde {sender}")
                
        except Exception as e:
            print(f"❌ Error procesando lista de peers: {e}")
    
    def _process_received_block(self, block_data, sender):
        """Procesar bloque recibido de otro nodo"""
        try:
            # Verificar si ya tenemos este bloque
            current_chain_length = len(self.blockchain.chain)
            if block_data['indice'] <= current_chain_length:
                print(f"⏭️  Bloque {block_data['indice']} ya existe, ignorando")
                return
            
            # Verificar si es el siguiente bloque esperado
            if block_data['indice'] == current_chain_length + 1:
                print(f"✅ Recibido siguiente bloque {block_data['indice']}")
                self._validate_and_add_block(block_data)
            else:
                # Necesitamos sincronizar la cadena completa
                print(f"🔄 Bloque {block_data['indice']} recibido, necesitamos sincronizar")
                self.request_full_chain(sender)
                
        except Exception as e:
            print(f"❌ Error procesando bloque recibido: {e}")
    
    def _validate_and_add_block(self, block_data):
        """Validar y agregar bloque a la cadena"""
        try:
            # Verificar Proof of Work
            if not self.blockchain.validar_pow(block_data):
                print("❌ Bloque con PoW inválido")
                return False
            
            # Verificar hash anterior
            last_block = self.blockchain.last_block
            if block_data['hash_anterior'] != self._calculate_block_hash(last_block):
                print("❌ Hash anterior no coincide")
                return False
            
            # Crear objeto bloque
            block = self.blockchain.Bloque(
                block_data['indice'],
                block_data['hash_anterior'],
                block_data['transacciones'],
                block_data['tiempo'],
                block_data['nonce']
            )
            
            # Agregar bloque
            self.blockchain.nuevo_bloque(block)
            print(f"✅ Bloque {block_data['indice']} agregado exitosamente")
            
            # Verificar si hay transacciones pendientes que ya están en este bloque
            self._cleanup_pending_transactions(block_data['transacciones'])
            
            return True
            
        except Exception as e:
            print(f"❌ Error validando bloque: {e}")
            return False
    
    def _cleanup_pending_transactions(self, block_transactions):
        """Limpiar transacciones pendientes que ya están en bloques confirmados"""
        pending_txs = self.blockchain.transacciones_pendientes.copy()
        
        for pending_tx in pending_txs:
            for block_tx in block_transactions:
                # Comparar transacciones por contenido similar
                if self._transactions_match(pending_tx, block_tx):
                    try:
                        self.blockchain.transacciones_pendientes.remove(pending_tx)
                        print(f"🧹 Transacción limpiada de pendientes")
                    except ValueError:
                        pass
    
    def _transactions_match(self, tx1, tx2):
        """Verificar si dos transacciones son iguales"""
        keys = ['envia', 'recibe', 'monto']
        for key in keys:
            if tx1.get(key) != tx2.get(key):
                return False
        return True
    
    def _process_received_transaction(self, transaction_data, sender):
        """Procesar transacción recibida de otro nodo"""
        try:
            # Verificar si ya tenemos esta transacción
            for pending_tx in self.blockchain.transacciones_pendientes:
                if self._transactions_match(pending_tx, transaction_data):
                    print("⏭️  Transacción ya existe, ignorando")
                    return
            
            # Agregar transacción pendiente
            self.blockchain.add_transaction(
                transaction_data['envia'],
                transaction_data['recibe'],
                transaction_data['monto'],
                transaction_data.get('fee', 0.001)
            )
            print(f"✅ Transacción recibida agregada a pendientes")
            
        except Exception as e:
            print(f"❌ Error procesando transacción recibida: {e}")
    
    def request_full_chain(self, target_node):
        """Solicitar cadena completa a un nodo específico"""
        try:
            message = {
                'type': 'chain_request',
                'timestamp': time.time(),
                'node_id': getattr(self.blockchain, 'node_id', 'unknown')
            }
            
            # Intentar tanto HTTP como HTTPS
            protocols = ['https', 'http']
            success = False
            
            for protocol in protocols:
                try:
                    url = f"{protocol}://{target_node}/network/receive"
                    response = requests.post(url, json=message, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✅ Solicitud de cadena enviada a {target_node} ({protocol})")
                        success = True
                        break
                except:
                    continue
            
            if not success:
                print(f"❌ Error solicitando cadena a {target_node}")
                
        except Exception as e:
            print(f"❌ No se pudo solicitar cadena a {target_node}: {e}")
    
    def _handle_chain_request(self, sender):
        """Manejar solicitud de cadena de otro nodo"""
        try:
            chain_data = {
                'chain': self.blockchain.chain,
                'length': len(self.blockchain.chain),
                'total_supply': self.blockchain.get_total_supply()
            }
            
            message = {
                'type': 'chain_response',
                'data': chain_data,
                'timestamp': time.time(),
                'node_id': getattr(self.blockchain, 'node_id', 'unknown')
            }
            
            # Intentar tanto HTTP como HTTPS
            protocols = ['https', 'http']
            success = False
            
            for protocol in protocols:
                try:
                    url = f"{protocol}://{sender}/network/receive"
                    response = requests.post(url, json=message, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✅ Cadena enviada a {sender} ({protocol})")
                        success = True
                        break
                except:
                    continue
            
            if not success:
                print(f"❌ Error enviando cadena a {sender}")
                
        except Exception as e:
            print(f"❌ Error manejando solicitud de cadena: {e}")
    
    def _handle_chain_response(self, chain_data, sender):
        """Manejar respuesta de cadena de otro nodo"""
        try:
            received_chain = chain_data['chain']
            received_length = chain_data['length']
            
            print(f"📥 Cadena recibida de {sender}: {received_length} bloques")
            
            # Validar cadena recibida
            if self.blockchain.valid_chain(received_chain):
                current_length = len(self.blockchain.chain)
                
                # Adoptar cadena más larga
                if received_length > current_length:
                    print(f"🔄 Adoptando cadena más larga de {sender}")
                    self.blockchain.chain = received_chain
                    self.blockchain.save_blockchain()
                    
                    # Limpiar transacciones pendientes que ya están en la nueva cadena
                    self._cleanup_pending_from_chain(received_chain)
                    
                    print(f"✅ Cadena actualizada a {received_length} bloques")
                else:
                    print(f"⏭️  Nuestra cadena es más larga o igual, manteniendo")
            else:
                print(f"❌ Cadena recibida de {sender} es inválida")
                
        except Exception as e:
            print(f"❌ Error manejando respuesta de cadena: {e}")
    
    def _cleanup_pending_from_chain(self, new_chain):
        """Limpiar transacciones pendientes basado en nueva cadena"""
        all_confirmed_txs = []
        for block in new_chain:
            all_confirmed_txs.extend(block.get('transacciones', []))
        
        pending_txs = self.blockchain.transacciones_pendientes.copy()
        
        for pending_tx in pending_txs:
            for confirmed_tx in all_confirmed_txs:
                if self._transactions_match(pending_tx, confirmed_tx):
                    try:
                        self.blockchain.transacciones_pendientes.remove(pending_tx)
                        print(f"🧹 Transacción confirmada limpiada de pendientes")
                    except ValueError:
                        pass
    
    def sync_blockchain(self):
        """Sincronizar blockchain con todos los nodos - VERSIÓN MEJORADA"""
        print("🔄 Iniciando sincronización de blockchain...")
        
        longest_chain = None
        max_length = len(self.blockchain.chain)
        
        for node in list(self.blockchain.nodes):
            try:
                print(f"🔍 Consultando nodo: {node}")
                
                # Intentar tanto HTTP como HTTPS
                protocols = ['https', 'http']
                success = False
                
                for protocol in protocols:
                    try:
                        url = f"{protocol}://{node}/chain"
                        response = requests.get(url, timeout=15)
                        
                        if response.status_code == 200:
                            node_chain = response.json()
                            node_length = node_chain['largo']
                            chain_data = node_chain['chain']
                            
                            print(f"📡 Nodo {node} ({protocol}): {node_length} bloques")
                            
                            if node_length > max_length and self.blockchain.valid_chain(chain_data):
                                max_length = node_length
                                longest_chain = chain_data
                                print(f"🎯 Cadena más larga encontrada en {node}")
                            
                            success = True
                            break
                    except Exception as e:
                        print(f"   ❌ {protocol}://{node} falló: {e}")
                        continue
                
                if not success:
                    print(f"❌ No se pudo conectar a {node} con ningún protocolo")
                        
            except Exception as e:
                print(f"❌ Error sincronizando con {node}: {e}")
        
        if longest_chain:
            print(f"✅ Sincronizando con cadena de {max_length} bloques")
            self.blockchain.chain = longest_chain
            self.blockchain.save_blockchain()
            return True
        else:
            print("✅ Nuestra cadena es la más actualizada")
            return False
    
    def _calculate_block_hash(self, block):
        """Calcular hash de un bloque (mismo método que en core.py)"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
```

## 4. **blockchain.py**
```python
from core import hash_bloque, Bloque, Blockchain, create_rgd_address, RGDBlockchainConfig
from wallet_manager import WalletManager
from network_manager import NetworkManager
from time import time
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

class Transaccion(BaseModel):
    envia: str
    recibe: str
    monto: float
    fee: float = RGDBlockchainConfig.TRANSACTION_FEE

class Nodo(BaseModel):
    nodes: str

class ResetBlockchain(BaseModel):
    genesis_wallet_address: str = None  # Opcional, siempre se usará la fija

app = FastAPI()

# Inicializar componentes
wallet_manager = WalletManager()
blockchain = Blockchain(node_id=create_rgd_address())
network_manager = NetworkManager(blockchain, wallet_manager)

# Variable para almacenar la wallet del nodo minero
mining_wallet = None

@app.on_event("startup")
async def startup_event():
    """Iniciar servicios cuando arranca la aplicación"""
    network_manager.start_network_services()
    
    # Sincronización automática al inicio
    print("🔄 Sincronizando al inicio...")
    try:
        success = network_manager.sync_blockchain()
        if success:
            print("✅ Sincronización inicial completada")
        else:
            print("⚠️  No se pudo sincronizar al inicio")
    except Exception as e:
        print(f"❌ Error en sincronización inicial: {e}")
    
    print("🚀 Servicios de red iniciados automáticamente")

@app.on_event("shutdown")
async def shutdown_event():
    """Detener servicios cuando se apaga la aplicación"""
    network_manager.stop_network_services()
    print("🛑 Servicios de red detenidos")

@app.get('/')
def root():
    """Endpoint raíz con información de la red RGD"""
    return {
        'message': f'Bienvenido a {RGDBlockchainConfig.NAME}',
        'ticker': RGDBlockchainConfig.TICKER,
        'symbol': RGDBlockchainConfig.SYMBOL,
        'version': RGDBlockchainConfig.VERSION,
        'block_height': len(blockchain.chain),
        'mining_wallet': mining_wallet,
        'node_id': blockchain.node_id,
        'connected_nodes': len(blockchain.nodes),
        'genesis_address': RGDBlockchainConfig.GENESIS_ADDRESS
    }

@app.get('/network')
def network_info():
    """Información completa de la red RGD"""
    return blockchain.get_network_info()

@app.get('/chain')
def full_chain():
    resp = {
        'chain': blockchain.chain,
        'largo': len(blockchain.chain),
        'total_supply': blockchain.get_total_supply(),
        'current_reward': blockchain.get_current_reward(),
        'pending_transactions': len(blockchain.transacciones_pendientes),
        'genesis_address': RGDBlockchainConfig.GENESIS_ADDRESS
    }
    return resp

@app.get('/mine')
def minar_bloque():
    if not mining_wallet:
        return {'error': 'No hay wallet configurada para minar. Use /set_mining_wallet primero.'}
    
    # Recompensa actual + fees de transacciones
    current_reward = blockchain.get_current_reward()
    total_fees = sum(tx.get('fee', 0) for tx in blockchain.transacciones_pendientes)
    
    # Crear transacción coinbase
    coinbase_tx = {
        'tipo': 'coinbase',
        'recompensa': current_reward,
        'fees': total_fees,
        'destino': mining_wallet,
        'timestamp': time()
    }
    
    # Transacciones del bloque: coinbase + pendientes
    block_transactions = [coinbase_tx] + blockchain.transacciones_pendientes
    
    hash_bloque_anterior = hash_bloque(blockchain.last_block) if blockchain.last_block else "0" * 64
    index = len(blockchain.chain)
    
    block = blockchain.proof_of_work(index, hash_bloque_anterior, block_transactions, time())
    blockchain.nuevo_bloque(block)
    
    # Transmitir nuevo bloque a la red
    network_manager.broadcast_new_block(block.__dict__)
    
    resp = {
        'mensaje': f"¡Nuevo Bloque RGD Minado! {RGDBlockchainConfig.SYMBOL}",
        'index': block.indice,
        'hash_anterior': block.hash_anterior,
        'nonce': block.nonce,
        'recompensa': current_reward,
        'fees': total_fees,
        'transacciones': len(block.transacciones),
        'total_supply': blockchain.get_total_supply(),
        'mining_wallet': mining_wallet,
        'transmitted': True
    }
    return resp

@app.post('/transaciones/new')
async def new_transaction(item: Transaccion):
    index = blockchain.add_transaction(
        monto=item.monto,
        recibe=item.recibe,
        envia=item.envia,
        fee=item.fee
    )
    
    # Transmitir transacción a la red
    transaction_data = {
        'envia': item.envia,
        'recibe': item.recibe,
        'monto': item.monto,
        'fee': item.fee,
        'timestamp': time()
    }
    network_manager.broadcast_new_transaction(transaction_data)
    
    resp = {
        'mensaje': f'Transacción {RGDBlockchainConfig.TICKER} añadida',
        'simbolo': RGDBlockchainConfig.SYMBOL,
        'fee': item.fee,
        'block_index': index,
        'transmitted': True,
        'Datos': item.__dict__
    }
    return resp 

@app.post('/addnode')
async def add_nodes(item: Nodo):
    blockchain.add_node(item.nodes)
    resp = {
        'mensaje': 'Nuevo nodo RGD añadido',
        'nodos_en_la_red': list(blockchain.nodes)
    }
    return resp

@app.get('/nodo/sync')
def sync():
    updated = network_manager.sync_blockchain()
    if updated:
        resp = {
            'mensaje': 'El blockchain RGD se ha actualizado a la cadena más larga',
            'nuevo_largo': len(blockchain.chain),
            'bloques_agregados': len(blockchain.chain)
        }
    else:
        resp = {
            'mensaje': 'Su blockchain RGD tiene la cadena más larga',
            'largo_actual': len(blockchain.chain)
        } 
    return resp

@app.get('/address/new')
def generate_address():
    """Genera una nueva dirección RGD"""
    new_address = create_rgd_address()
    return {
        'mensaje': 'Nueva dirección RGD generada',
        'direccion': new_address
    }

# Endpoints para gestión de wallets
@app.post('/wallet/create')
async def create_wallet(wallet_data: dict):
    """Crear nueva wallet"""
    name = wallet_data.get('name', f'wallet_{int(time())}')
    password = wallet_data.get('password', None)
    
    address = wallet_manager.create_wallet(name, password)
    if address:
        return {
            'mensaje': 'Wallet RGD creada exitosamente',
            'wallet': {
                'nombre': name,
                'direccion': address,
                'simbolo': '⚡'
            }
        }
    else:
        return {'error': 'No se pudo crear la wallet'}

@app.get('/wallet/list')
def list_wallets():
    """Listar todas las wallets"""
    wallets = wallet_manager.list_wallets()
    wallet_details = []
    
    for address in wallets:
        wallet = wallet_manager.get_wallet(address)
        if wallet:
            # Calcular balance actual
            balance = wallet_manager.get_wallet_balance(address, blockchain)
            wallet_details.append({
                'nombre': wallet['name'],
                'direccion': wallet['address'],
                'balance': balance,
                'creada_en': wallet['created_at']
            })
    
    return {
        'total_wallets': len(wallet_details),
        'wallets': wallet_details
    }

@app.post('/wallet/export')
async def export_wallet(export_data: dict):
    """Exportar wallet a archivo"""
    address = export_data.get('address')
    export_path = export_data.get('path', f'wallets/export_{address}_{int(time())}.json')
    
    if wallet_manager.export_wallet(address, export_path):
        return {
            'mensaje': 'Wallet exportada exitosamente',
            'archivo': export_path
        }
    else:
        return {'error': 'Error exportando wallet'}

@app.post('/wallet/import')
async def import_wallet(import_data: dict):
    """Importar wallet desde archivo"""
    import_path = import_data.get('path')
    
    address = wallet_manager.import_wallet(import_path)
    if address:
        return {
            'mensaje': 'Wallet importada exitosamente',
            'direccion': address
        }
    else:
        return {'error': 'Error importando wallet'}

@app.get('/wallet/backup')
def backup_wallets():
    """Crear backup de todas las wallets"""
    if wallet_manager.backup_all_wallets():
        return {'mensaje': 'Backup de wallets creado exitosamente'}
    else:
        return {'error': 'Error creando backup'}

@app.post('/set_mining_wallet')
async def set_mining_wallet(wallet_data: dict):
    """Establecer la wallet para minar"""
    global mining_wallet
    address = wallet_data.get('address')
    
    if address in wallet_manager.list_wallets():
        mining_wallet = address
        return {
            'mensaje': 'Wallet de minado configurada exitosamente',
            'mining_wallet': mining_wallet
        }
    else:
        return {'error': 'La wallet no existe. Cree la wallet primero.'}

@app.get('/get_mining_wallet')
def get_mining_wallet():
    """Obtener la wallet actual de minado"""
    return {
        'mining_wallet': mining_wallet,
        'mensaje': 'Wallet de minado actual' if mining_wallet else 'No hay wallet configurada para minar'
    }

@app.post('/reset_blockchain')
async def reset_blockchain(data: ResetBlockchain = None):
    """Reiniciar la blockchain - SIEMPRE usa la dirección génesis fija"""
    # IGNORAR el parámetro y usar siempre la dirección fija
    genesis_wallet_address = RGDBlockchainConfig.GENESIS_ADDRESS
    
    # Verificar que la wallet existe
    if genesis_wallet_address not in wallet_manager.list_wallets():
        return {'error': 'La wallet génesis no existe. Cree la wallet primero.'}
    
    blockchain.reset_blockchain(genesis_wallet_address)
    return {
        'mensaje': 'Blockchain reiniciada exitosamente con dirección génesis fija',
        'genesis_wallet': genesis_wallet_address,
        'genesis_reward': RGDBlockchainConfig.GENESIS_REWARD
    }

@app.post('/network/receive')
async def receive_network_message(request: Request):
    """Endpoint para recibir mensajes de la red"""
    try:
        message = await request.json()
        network_manager.receive_message(message)
        return {'status': 'message_received'}
    except Exception as e:
        return {'error': f'Error processing message: {e}'}

@app.get('/network/status')
def network_status():
    """Estado de la red"""
    return {
        'node_id': blockchain.node_id,
        'connected_nodes': list(blockchain.nodes),
        'block_height': len(blockchain.chain),
        'pending_transactions': len(blockchain.transacciones_pendientes),
        'network_services': 'active',
        'genesis_address': RGDBlockchainConfig.GENESIS_ADDRESS
    }

@app.get('/peers')
def get_peers():
    """Obtener lista de peers conectados"""
    return {
        'peers': list(blockchain.nodes),
        'total_peers': len(blockchain.nodes)
    }

@app.post('/peers/share')
async def share_peers():
    """Forzar compartir lista de peers con la red"""
    network_manager._share_peers_with_network()
    return {'mensaje': 'Lista de peers compartida con la red'}

if __name__ == "__main__":
    print(f"=== {RGDBlockchainConfig.NAME} ===")
    print(f"Ticker: {RGDBlockchainConfig.TICKER}")
    print(f"Símbolo: {RGDBlockchainConfig.SYMBOL}")
    print(f"Versión: {RGDBlockchainConfig.VERSION}")
    print(f"Node ID: {blockchain.node_id}")
    print(f"Dirección Génesis Fija: {RGDBlockchainConfig.GENESIS_ADDRESS}")
    print("Iniciando servidor RGD con retransmisión automática y peer discovery...")
    
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

## 5. **wallet_manager.py**
```python
import json
import os
import base58
import ecdsa
from hashlib import sha256
import hashlib
import time

# Cargar configuración RGD
with open('config.json', 'r') as f:
    config = json.load(f)

class WalletManager:
    def __init__(self, wallet_dir=config['wallet_dir']):
        self.wallet_dir = wallet_dir
        self.ensure_wallet_dir()
        self.load_wallets()
    
    def ensure_wallet_dir(self):
        """Crear directorio de wallets si no existe"""
        if not os.path.exists(self.wallet_dir):
            os.makedirs(self.wallet_dir)
            print(f"✅ Directorio de wallets creado: {self.wallet_dir}")
    
    def load_wallets(self):
        """Cargar wallets existentes"""
        self.wallets = {}
        if os.path.exists(f"{self.wallet_dir}/wallets.json"):
            try:
                with open(f"{self.wallet_dir}/wallets.json", 'r') as f:
                    self.wallets = json.load(f)
                print(f"✅ {len(self.wallets)} wallets cargadas")
            except Exception as e:
                print(f"❌ Error cargando wallets: {e}")
                self.wallets = {}
    
    def save_wallets(self):
        """Guardar wallets en archivo"""
        try:
            with open(f"{self.wallet_dir}/wallets.json", 'w') as f:
                json.dump(self.wallets, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error guardando wallets: {e}")
            return False
    
    def create_wallet(self, wallet_name, password=None):
        """Crear nueva wallet y guardarla"""
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key().to_string()
        
        # Generar dirección RGD
        sha256_hash = sha256(public_key).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        versioned_hash = b'\x00' + ripemd160_hash
        checksum = sha256(sha256(versioned_hash).digest()).digest()[:4]
        binary_address = versioned_hash + checksum
        rgd_address = base58.b58encode(binary_address).decode('utf-8')
        full_address = f"RGD:{rgd_address}"
        
        # Guardar wallet
        wallet_data = {
            'name': wallet_name,
            'address': full_address,
            'public_key': public_key.hex(),
            'private_key_encrypted': private_key.to_string().hex(),  # ⚠️ En producción cifrar con password
            'created_at': time.time(),
            'balance': 0
        }
        
        self.wallets[full_address] = wallet_data
        if self.save_wallets():
            print(f"✅ Wallet '{wallet_name}' creada: {full_address}")
            return full_address
        else:
            print("❌ Error guardando wallet")
            return None
    
    def get_wallet(self, address):
        """Obtener información de una wallet"""
        return self.wallets.get(address)
    
    def list_wallets(self):
        """Listar todas las wallets"""
        return list(self.wallets.keys())
    
    def export_wallet(self, address, export_path):
        """Exportar wallet a archivo JSON"""
        wallet = self.get_wallet(address)
        if wallet:
            try:
                with open(export_path, 'w') as f:
                    json.dump(wallet, f, indent=2)
                print(f"✅ Wallet exportada a: {export_path}")
                return True
            except Exception as e:
                print(f"❌ Error exportando wallet: {e}")
                return False
        return False
    
    def import_wallet(self, import_path):
        """Importar wallet desde archivo JSON"""
        try:
            with open(import_path, 'r') as f:
                wallet_data = json.load(f)
            
            address = wallet_data['address']
            self.wallets[address] = wallet_data
            self.save_wallets()
            print(f"✅ Wallet importada: {address}")
            return address
        except Exception as e:
            print(f"❌ Error importando wallet: {e}")
            return None
    
    def backup_all_wallets(self, backup_dir="wallets/backup"):
        """Crear backup de todas las wallets"""
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = f"{backup_dir}/wallets_backup_{timestamp}.json"
        
        try:
            with open(backup_file, 'w') as f:
                json.dump(self.wallets, f, indent=2)
            print(f"✅ Backup creado: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return False

    def get_wallet_balance(self, address, blockchain):
        """Calcular balance de una wallet revisando la blockchain"""
        balance = 0
        for block in blockchain.chain:
            for tx in block.get('transacciones', []):
                if tx.get('destino') == address or tx.get('recibe') == address:
                    balance += tx.get('monto', 0) + tx.get('recompensa', 0)
                if tx.get('envia') == address:
                    balance -= tx.get('monto', 0)
        return balance
```

## 6. **addnode.sh**
```bash
#!/bin/bash
# Conectar nodos RGD rápidamente - VERSIÓN MEJORADA
echo "🔗 Conectando a nodos RGD..."

# Conectar al nodo principal via HTTPS (Cloudflare Tunnel)
curl -X POST 'http://localhost:5000/addnode' \
  -H 'Content-Type: application/json' \
  -d '{"nodes": "rudagnetwork2.canariannode.uk"}'

echo ""

# También conectar al otro nodo
curl -X POST 'http://localhost:5000/addnode' \
  -H 'Content-Type: application/json' \
  -d '{"nodes": "rudagnetwork.canariannode.uk"}'

echo ""
echo "✅ Nodos RGD conectados ⚡"
echo "🔄 La red compartirá automáticamente estos peers con otros nodos"
```

## 7. **blockchain.json** (Estructura inicial)
```json
{
  "chain": [
    {
      "indice": 0,
      "hash_anterior": "0000000000000000000000000000000000000000000000000000000000000000",
      "transacciones": [
        {
          "tipo": "coinbase",
          "recompensa": 500,
          "fees": 0,
          "destino": "RGD:1A77LFiAzzVnDdpMRjKqwB3ZjiVnuNqQjk",
          "timestamp": 1760476400.2370994
        }
      ],
      "tiempo": 1760476400.2371097,
      "nonce": 57798
    }
  ],
  "nodes": [
    "rudagnetwork2.canariannode.uk",
    "rudagnetwork.canariannode.uk"
  ],
  "transacciones_pendientes": []
}
```

## 8. **requirements.txt**
```text
fastapi~=0.100.0
uvicorn~=0.25.0
ecdsa~=0.18.0
base58~=2.1.1
requests~=2.27.1
pydantic~=1.10.0
```

## 9. **RudagCoreV2.py** (CLI Interactivo)
```python
#!/usr/bin/env python3

import os
import sys
import subprocess
import requests
import json
import signal
import time
from typing import Dict, Any

class RudagCore:
    def __init__(self):
        # Colores para output
        self.RED = '\033[0;31m'
        self.GREEN = '\033[0;32m'
        self.YELLOW = '\033[1;33m'
        self.BLUE = '\033[0;34m'
        self.PURPLE = '\033[0;35m'
        self.CYAN = '\033[0;36m'
        self.NC = '\033[0m'  # No Color
        
        self.base_url = "http://localhost:5000"
        self.mining_active = False
        self.mining_interval = 9  # 9 segundos entre bloques

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def show_banner(self):
        self.clear_screen()
        print(f"{self.PURPLE}")
        print("╔══════════════════════════════════════════════╗")
        print("║             RUDAG CORE 1.0.0.1              ║")
        print("║           Blockchain Interactive CLI         ║")
        print("║                                              ║")
        print("║      ██████╗ ██╗   ██╗██████╗  █████╗       ║")
        print("║      ██╔══██╗██║   ██║██╔══██╗██╔══██╗      ║")
        print("║      ██████╔╝██║   ██║██║  ██║███████║      ║")
        print("║      ██╔══██╗██║   ██║██║  ██║██╔══██║      ║")
        print("║      ██║  ██║╚██████╔╝██████╔╝██║  ██║      ║")
        print("║      ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝      ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"{self.NC}")
        print(f"{self.CYAN}Script interactivo para la Blockchain Rudag{self.NC}")
        print(f"{self.YELLOW}============================================={self.NC}")
        print()

    def show_menu(self):
        print(f"{self.BLUE}╔══════════════════════════════════════════════╗{self.NC}")
        print(f"{self.BLUE}║               MENÚ PRINCIPAL                 ║{self.NC}")
        print(f"{self.BLUE}╠══════════════════════════════════════════════╣{self.NC}")
        print(f"{self.BLUE}║  {self.GREEN}1{self.NC})  Gestión del Nodo                   {self.BLUE}║{self.NC}")
        print(f"{self.BLUE}║  {self.GREEN}2{self.NC})  Operaciones con Wallets            {self.BLUE}║{self.NC}")
        print(f"{self.BLUE}║  {self.GREEN}3{self.NC})  Transacciones                      {self.BLUE}║{self.NC}")
        print(f"{self.BLUE}║  {self.GREEN}4{self.NC})  Minería                            {self.BLUE}║{self.NC}")
        print(f"{self.BLUE}║  {self.GREEN}5{self.NC})  Información de la Red              {self.BLUE}║{self.NC}")
        print(f"{self.BLUE}║  {self.GREEN}6{self.NC})  Gestión de la Blockchain           {self.BLUE}║{self.NC}")
        print(f"{self.BLUE}║  {self.GREEN}7{self.NC})  Scripts Utilitarios                {self.BLUE}║{self.NC}")
        print(f"{self.BLUE}║  {self.RED}8{self.NC})  Salir                            {self.BLUE}║{self.NC}")
        print(f"{self.BLUE}╚══════════════════════════════════════════════╝{self.NC}")
        print()
        print(f"{self.YELLOW}Selecciona una opción [1-8]: {self.NC}", end="")

    def make_request(self, endpoint, method='GET', data=None):
        """Función auxiliar para hacer requests HTTP"""
        try:
            url = f"{self.base_url}{endpoint}"
            if method.upper() == 'GET':
                response = requests.get(url)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except requests.exceptions.ConnectionError:
            return {"error": "No se puede conectar al nodo. ¿Está ejecutándose?"}
        except Exception as e:
            return {"error": f"Error: {str(e)}"}

    def node_management(self):
        while True:
            self.clear_screen()
            print(f"{self.CYAN}╔══════════════════════════════════════════════╗{self.NC}")
            print(f"{self.CYAN}║            GESTIÓN DEL NODO                  ║{self.NC}")
            print(f"{self.CYAN}╠══════════════════════════════════════════════╣{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}1{self.NC})  Iniciar Nodo                        {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}2{self.NC})  Detener Nodo                       {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}3{self.NC})  Ver información de red             {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}4{self.NC})  Añadir nodo a la red               {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}5{self.NC})  Sincronizar blockchain             {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.RED}6{self.NC})  Volver al menú principal         {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}╚══════════════════════════════════════════════╝{self.NC}")
            print()
            print(f"{self.YELLOW}Selecciona una opción [1-6]: {self.NC}", end="")
            
            choice = input().strip()
            
            if choice == "1":
                print(f"{self.GREEN}Iniciando nodo...{self.NC}")
                try:
                    # Activar venv y ejecutar blockchain.py en segundo plano
                    subprocess.Popen([
                        'bash', '-c', 
                        'source venv/bin/activate && python3 blockchain.py &'
                    ])
                    print(f"{self.GREEN}Nodo iniciado en segundo plano{self.NC}")
                    time.sleep(2)
                except Exception as e:
                    print(f"{self.RED}Error al iniciar nodo: {e}{self.NC}")
                    
            elif choice == "2":
                print(f"{self.YELLOW}Deteniendo nodo...{self.NC}")
                try:
                    subprocess.run(['pkill', '-f', 'python3 blockchain.py'])
                    print(f"{self.GREEN}Nodo detenido{self.NC}")
                    time.sleep(1)
                except Exception as e:
                    print(f"{self.RED}Error al detener nodo: {e}{self.NC}")
                    
            elif choice == "3":
                print(f"{self.BLUE}Obteniendo información de red...{self.NC}")
                result = self.make_request('/network')
                print(json.dumps(result, indent=2))
                print()
                print(f"{self.YELLOW}Presiona Enter para continuar...{self.NC}", end="")
                input()
                
            elif choice == "4":
                print(f"{self.YELLOW}Ingresa la dirección del nodo (ej: http://192.168.1.100:5000):{self.NC}")
                node_address = input().strip()
                result = self.make_request('/addnode', 'POST', {"nodes": node_address})
                print(f"\n{self.GREEN}Nodo añadido: {result}{self.NC}")
                time.sleep(1)
                
            elif choice == "5":
                print(f"{self.BLUE}Sincronizando blockchain...{self.NC}")
                result = self.make_request('/nodo/sync')
                print(f"\n{self.GREEN}Sincronización completada: {result}{self.NC}")
                time.sleep(1)
                
            elif choice == "6":
                return
            else:
                print(f"{self.RED}Opción inválida{self.NC}")
                time.sleep(1)

    def wallet_operations(self):
        while True:
            self.clear_screen()
            print(f"{self.CYAN}╔══════════════════════════════════════════════╗{self.NC}")
            print(f"{self.CYAN}║          OPERACIONES CON WALLETS             ║{self.NC}")
            print(f"{self.CYAN}╠══════════════════════════════════════════════╣{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}1{self.NC})  Listar wallets                     {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}2{self.NC})  Crear nueva wallet                {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}3{self.NC})  Generar nueva dirección RGD       {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}4{self.NC})  Configurar wallet de minado       {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}5{self.NC})  Exportar wallet                   {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}6{self.NC})  Importar wallet                   {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}7{self.NC})  Backup de todas las wallets       {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.RED}8{self.NC})  Volver al menú principal         {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}╚══════════════════════════════════════════════╝{self.NC}")
            print()
            print(f"{self.YELLOW}Selecciona una opción [1-8]: {self.NC}", end="")
            
            choice = input().strip()
            
            if choice == "1":
                print(f"{self.BLUE}Listando wallets...{self.NC}")
                result = self.make_request('/wallet/list')
                print(json.dumps(result, indent=2))
                print()
                print(f"{self.YELLOW}Presiona Enter para continuar...{self.NC}", end="")
                input()
                
            elif choice == "2":
                print(f"{self.YELLOW}Nombre de la wallet:{self.NC}")
                wallet_name = input().strip()
                print(f"{self.YELLOW}Contraseña (opcional):{self.NC}")
                wallet_password = input().strip()
                result = self.make_request('/wallet/create', 'POST', {
                    "name": wallet_name, 
                    "password": wallet_password
                })
                print(f"\n{self.GREEN}Wallet creada: {result}{self.NC}")
                time.sleep(1)
                
            elif choice == "3":
                print(f"{self.BLUE}Generando nueva dirección...{self.NC}")
                result = self.make_request('/address/new')
                print(f"{self.GREEN}Nueva dirección: {result}{self.NC}")
                time.sleep(1)
                
            elif choice == "4":
                print(f"{self.YELLOW}Dirección de la wallet para minado:{self.NC}")
                mining_address = input().strip()
                result = self.make_request('/set_mining_wallet', 'POST', {
                    "address": mining_address
                })
                print(f"\n{self.GREEN}Wallet de minado configurada: {result}{self.NC}")
                time.sleep(1)
                
            elif choice == "5":
                print(f"{self.YELLOW}Dirección de la wallet a exportar:{self.NC}")
                export_address = input().strip()
                print(f"{self.YELLOW}Ruta de exportación (ej: /ruta/wallet.json):{self.NC}")
                export_path = input().strip()
                result = self.make_request('/wallet/export', 'POST', {
                    "address": export_address,
                    "path": export_path
                })
                print(f"\n{self.GREEN}Wallet exportada: {result}{self.NC}")
                time.sleep(1)
                
            elif choice == "6":
                print(f"{self.YELLOW}Ruta del archivo a importar:{self.NC}")
                import_path = input().strip()
                result = self.make_request('/wallet/import', 'POST', {
                    "path": import_path
                })
                print(f"\n{self.GREEN}Wallet importada: {result}{self.NC}")
                time.sleep(1)
                
            elif choice == "7":
                print(f"{self.BLUE}Creando backup de todas las wallets...{self.NC}")
                result = self.make_request('/wallet/backup')
                print(f"\n{self.GREEN}Backup completado: {result}{self.NC}")
                time.sleep(1)
                
            elif choice == "8":
                return
            else:
                print(f"{self.RED}Opción inválida{self.NC}")
                time.sleep(1)

    def transaction_operations(self):
        while True:
            self.clear_screen()
            print(f"{self.CYAN}╔══════════════════════════════════════════════╗{self.NC}")
            print(f"{self.CYAN}║               TRANSACCIONES                  ║{self.NC}")
            print(f"{self.CYAN}╠══════════════════════════════════════════════╣{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}1{self.NC})  Crear nueva transacción           {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}2{self.NC})  Ver cadena completa              {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.RED}3{self.NC})  Volver al menú principal         {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}╚══════════════════════════════════════════════╝{self.NC}")
            print()
            print(f"{self.YELLOW}Selecciona una opción [1-3]: {self.NC}", end="")
            
            choice = input().strip()
            
            if choice == "1":
                print(f"{self.YELLOW}Dirección de origen:{self.NC}")
                from_address = input().strip()
                print(f"{self.YELLOW}Dirección de destino:{self.NC}")
                to_address = input().strip()
                print(f"{self.YELLOW}Monto:{self.NC}")
                amount = input().strip()
                print(f"{self.YELLOW}Fee:{self.NC}")
                fee = input().strip()
                
                result = self.make_request('/transaciones/new', 'POST', {
                    "envia": from_address,
                    "recibe": to_address,
                    "monto": float(amount),
                    "fee": float(fee)
                })
                print(f"\n{self.GREEN}Transacción creada: {result}{self.NC}")
                time.sleep(1)
                
            elif choice == "2":
                print(f"{self.BLUE}Obteniendo cadena completa...{self.NC}")
                result = self.make_request('/chain')
                print(json.dumps(result, indent=2))
                print()
                print(f"{self.YELLOW}Presiona Enter para continuar...{self.NC}", end="")
                input()
                
            elif choice == "3":
                return
            else:
                print(f"{self.RED}Opción inválida{self.NC}")
                time.sleep(1)

    def signal_handler(self, signum, frame):
        """Manejador de señal para Ctrl+C"""
        self.mining_active = False
        print(f"\n{self.YELLOW}Deteniendo minería...{self.NC}")

    def start_infinite_mining(self):
        self.clear_screen()
        print(f"{self.PURPLE}╔══════════════════════════════════════════════╗{self.NC}")
        print(f"{self.PURPLE}║          INICIANDO MINERÍA INFINITA          ║{self.NC}")
        print(f"{self.PURPLE}╠══════════════════════════════════════════════╣{self.NC}")
        print(f"{self.PURPLE}║                                              ║{self.NC}")
        print(f"{self.PURPLE}║  {self.GREEN}• Minando bloques continuamente...        {self.PURPLE}║{self.NC}")
        print(f"{self.PURPLE}║  {self.YELLOW}• Presiona {self.RED}Ctrl+C{self.YELLOW} para detener la minería  {self.PURPLE}║{self.NC}")
        print(f"{self.PURPLE}║  {self.CYAN}• Verificando nodo en: localhost:5000     {self.PURPLE}║{self.NC}")
        print(f"{self.PURPLE}║                                              ║{self.NC}")
        print(f"{self.PURPLE}╚══════════════════════════════════════════════╝{self.NC}")
        print()
        
        # Configurar manejador de señal para Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        block_count = 0
        self.mining_active = True
        
        # Verificar si el nodo está ejecutándose
        try:
            test_result = self.make_request('/network')
            if "error" in test_result:
                print(f"{self.RED}Error: El nodo no está ejecutándose en localhost:5000{self.NC}")
                print(f"{self.YELLOW}Inicia el nodo primero desde el menú de Gestión del Nodo{self.NC}")
                time.sleep(3)
                return
        except:
            print(f"{self.RED}Error: No se puede conectar al nodo{self.NC}")
            time.sleep(3)
            return
        
        print(f"{self.GREEN}Nodo detectado. Iniciando minería...{self.NC}")
        print(f"{self.YELLOW}Presiona Ctrl+C en cualquier momento para detener{self.NC}")
        print()
        
        # Bucle infinito de minería
        while self.mining_active:
            block_count += 1
            print(f"{self.BLUE}⛏️  Minando bloque #{block_count}...{self.NC}")
            
            # Minar bloque
            result = self.make_request('/mine')
            
            # Verificar si la minería fue exitosa
            if "error" in str(result).lower():
                print(f"{self.RED}Error en la minería: {result}{self.NC}")
                print(f"{self.YELLOW}Reintentando en 5 segundos...{self.NC}")
                time.sleep(5)
            else:
                print(f"{self.GREEN}✅ Bloque #{block_count} minado exitosamente{self.NC}")
                print(f"{self.CYAN}Respuesta: {result}{self.NC}")
                print()
                
                # Espera silenciosa de 9 segundos sin mostrar nada
                for i in range(9):
                    if not self.mining_active:
                        break
                    time.sleep(1)
            
            # Verificar si el nodo sigue respondiendo cada 10 bloques
            if block_count % 10 == 0 and self.mining_active:
                print(f"{self.BLUE}Verificando estado del nodo...{self.NC}")
                test_result = self.make_request('/network')
                if "error" in test_result:
                    print(f"{self.RED}Error: El nodo ha dejado de responder{self.NC}")
                    self.mining_active = False
        
        # Limpieza después de detener
        print(f"{self.YELLOW}══════════════════════════════════════════════{self.NC}")
        print(f"{self.GREEN}Minería detenida{self.NC}")
        print(f"{self.BLUE}Total de bloques minados: {block_count}{self.NC}")
        print(f"{self.YELLOW}Presiona Enter para continuar...{self.NC}", end="")
        input()
        
        # Restablecer manejador de señal
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def mining_operations(self):
        while True:
            self.clear_screen()
            print(f"{self.CYAN}╔══════════════════════════════════════════════╗{self.NC}")
            print(f"{self.CYAN}║                  MINERÍA                    ║{self.NC}")
            print(f"{self.CYAN}╠══════════════════════════════════════════════╣{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}1{self.NC})  Minar bloque (Bucle Infinito)     {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}2{self.NC})  Minar bloque único                {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.RED}3{self.NC})  Volver al menú principal         {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}╚══════════════════════════════════════════════╝{self.NC}")
            print()
            print(f"{self.YELLOW}Selecciona una opción [1-3]: {self.NC}", end="")
            
            choice = input().strip()
            
            if choice == "1":
                self.start_infinite_mining()
            elif choice == "2":
                print(f"{self.BLUE}Minando bloque único...{self.NC}")
                result = self.make_request('/mine')
                print(f"\n{self.GREEN}Minería completada: {result}{self.NC}")
                time.sleep(2)
            elif choice == "3":
                return
            else:
                print(f"{self.RED}Opción inválida{self.NC}")
                time.sleep(1)

    def blockchain_management(self):
        while True:
            self.clear_screen()
            print(f"{self.CYAN}╔══════════════════════════════════════════════╗{self.NC}")
            print(f"{self.CYAN}║         GESTIÓN DE LA BLOCKCHAIN            ║{self.NC}")
            print(f"{self.CYAN}╠══════════════════════════════════════════════╣{self.NC}")
            print(f"{self.CYAN}║  {self.RED}1{self.NC})  Reiniciar blockchain (PELIGRO)    {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}2{self.NC})  Ver información de red           {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}3{self.NC})  Ver cadena completa              {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.RED}4{self.NC})  Volver al menú principal         {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}╚══════════════════════════════════════════════╝{self.NC}")
            print()
            print(f"{self.YELLOW}Selecciona una opción [1-4]: {self.NC}", end="")
            
            choice = input().strip()
            
            if choice == "1":
                print(f"{self.RED}╔══════════════════════════════════════════════╗{self.NC}")
                print(f"{self.RED}║                ¡ADVERTENCIA!                 ║{self.NC}")
                print(f"{self.RED}║  Esta acción es irreversible y borrará      ║{self.NC}")
                print(f"{self.RED}║  toda la blockchain actual.                 ║{self.NC}")
                print(f"{self.RED}╚══════════════════════════════════════════════╝{self.NC}")
                print()
                print(f"{self.YELLOW}¿Estás seguro de que quieres continuar? (s/N): {self.NC}", end="")
                confirm = input().strip().lower()
                if confirm == "s":
                    print(f"{self.YELLOW}Dirección para el bloque génesis:{self.NC}")
                    genesis_address = input().strip()
                    result = self.make_request('/reset_blockchain', 'POST', {
                        "genesis_wallet_address": genesis_address
                    })
                    print(f"\n{self.GREEN}Blockchain reiniciada: {result}{self.NC}")
                else:
                    print(f"{self.GREEN}Operación cancelada{self.NC}")
                time.sleep(2)
                
            elif choice == "2":
                print(f"{self.BLUE}Obteniendo información de red...{self.NC}")
                result = self.make_request('/network')
                print(json.dumps(result, indent=2))
                print()
                print(f"{self.YELLOW}Presiona Enter para continuar...{self.NC}", end="")
                input()
                
            elif choice == "3":
                print(f"{self.BLUE}Obteniendo cadena completa...{self.NC}")
                result = self.make_request('/chain')
                print(json.dumps(result, indent=2))
                print()
                print(f"{self.YELLOW}Presiona Enter para continuar...{self.NC}", end="")
                input()
                
            elif choice == "4":
                return
            else:
                print(f"{self.RED}Opción inválida{self.NC}")
                time.sleep(1)

    def utility_scripts(self):
        while True:
            self.clear_screen()
            print(f"{self.CYAN}╔══════════════════════════════════════════════╗{self.NC}")
            print(f"{self.CYAN}║            SCRIPTS UTILITARIOS              ║{self.NC}")
            print(f"{self.CYAN}╠══════════════════════════════════════════════╣{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}1{self.NC})  Ejecutar addnodes.sh              {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}2{self.NC})  Ver peers conectados              {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}3{self.NC})  Compartir peers con la red        {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.RED}4{self.NC})  Volver al menú principal         {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}╚══════════════════════════════════════════════╝{self.NC}")
            print()
            print(f"{self.YELLOW}Selecciona una opción [1-4]: {self.NC}", end="")
            
            choice = input().strip()
            
            if choice == "1":
                if os.path.exists("./addnode.sh"):
                    print(f"{self.BLUE}Ejecutando addnodes.sh...{self.NC}")
                    try:
                        subprocess.run(["./addnode.sh"], check=True)
                        print(f"{self.GREEN}Script completado{self.NC}")
                    except subprocess.CalledProcessError as e:
                        print(f"{self.RED}Error al ejecutar script: {e}{self.NC}")
                else:
                    print(f"{self.RED}Error: addnodes.sh no encontrado{self.NC}")
                time.sleep(2)
                
            elif choice == "2":
                print(f"{self.BLUE}Obteniendo lista de peers...{self.NC}")
                result = self.make_request('/peers')
                print(json.dumps(result, indent=2))
                print()
                print(f"{self.YELLOW}Presiona Enter para continuar...{self.NC}", end="")
                input()
                
            elif choice == "3":
                print(f"{self.BLUE}Compartiendo peers con la red...{self.NC}")
                result = self.make_request('/peers/share', 'POST')
                print(f"{self.GREEN}Resultado: {result}{self.NC}")
                time.sleep(2)
                
            elif choice == "4":
                return
            else:
                print(f"{self.RED}Opción inválida{self.NC}")
                time.sleep(1)

    def check_dependencies(self):
        """Verificar dependencias necesarias"""
        try:
            import requests
        except ImportError:
            print(f"{self.RED}Error: requests no está instalado. Instálalo con:{self.NC}")
            print("pip install requests")
            return False
        
        # Verificar si curl está instalado (para algunos comandos del sistema)
        try:
            subprocess.run(['curl', '--version'], check=True, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"{self.YELLOW}Advertencia: curl no está instalado{self.NC}")
            print("Algunas funcionalidades pueden no trabajar correctamente")
            time.sleep(2)
        
        return True

    def main(self):
        """Función principal"""
        if not self.check_dependencies():
            sys.exit(1)
            
        while True:
            self.show_banner()
            self.show_menu()
            choice = input().strip()
            
            if choice == "1":
                self.node_management()
            elif choice == "2":
                self.wallet_operations()
            elif choice == "3":
                self.transaction_operations()
            elif choice == "4":
                self.mining_operations()
            elif choice == "5":
                print(f"{self.BLUE}Obteniendo información de red...{self.NC}")
                result = self.make_request('/network')
                print(json.dumps(result, indent=2))
                print()
                print(f"{self.YELLOW}Presiona Enter para continuar...{self.NC}", end="")
                input()
            elif choice == "6":
                self.blockchain_management()
            elif choice == "7":
                self.utility_scripts()
            elif choice == "8":
                print(f"{self.GREEN}¡Hasta pronto!{self.NC}")
                sys.exit(0)
            else:
                print(f"{self.RED}Opción inválida. Presiona Enter para continuar.{self.NC}", end="")
                input()

if __name__ == "__main__":
    try:
        rudag = RudagCore()
        rudag.main()
    except KeyboardInterrupt:
        print(f"\n{rudag.GREEN}¡Hasta pronto!{rudag.NC}")
        sys.exit(0)
```

## 🚀 **INSTRUCCIONES DE INSTALACIÓN Y USO**

### **1. Instalación:**
```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Hacer ejecutable el script addnode
chmod +x addnode.sh
```

### **2. Ejecución:**
```bash
# Opción 1: Ejecutar nodo directamente
python blockchain.py

# Opción 2: Usar la CLI interactiva
python RudagCoreV2.py
```

### **3. Conexión a la red:**
```bash
./addnode.sh
```

## ✅ **CARACTERÍSTICAS IMPLEMENTADAS**

1. **Bloque Génesis Fijo** - Todos los nodos usan la misma dirección
2. **Soporte HTTP/HTTPS** - Compatible con Cloudflare Tunnel
3. **Descubrimiento Automático de Peers** - Los nodos se comparten automáticamente
4. **Sincronización Mejorada** - Con reintentos y validación mejorada
5. **CLI Interactivo** - Interfaz amigable para gestión
6. **Minería Automática** - Con bucle infinito y controles
7. **Gestión de Wallets** - Creación, backup, importación/exportación

¡El proyecto RGD ahora está completamente funcional con todas las mejoras solicitadas!
