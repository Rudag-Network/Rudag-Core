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
