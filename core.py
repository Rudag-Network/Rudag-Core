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
