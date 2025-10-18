from core import hash_bloque, Bloque, Blockchain, create_rgd_address, RGDBlockchainConfig
from wallet_manager import WalletManager
from network_manager import NetworkManager
from time import time
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import asyncio

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
    # Primero iniciar servicios de red
    network_manager.start_network_services()
    
    # Esperar un poco para que el servidor esté listo
    print("⏳ Esperando que el servidor esté listo...")
    await asyncio.sleep(3)
    
    # DESCUBRIMIENTO SIMPLIFICADO DE PEERS
    print("🔍 Descubriendo peers (método simplificado)...")
    try:
        success = blockchain.discover_peers_simplified("https://rudagserver.canariannode.uk")
        if success:
            print("✅ Descubrimiento de peers completado")
        else:
            print("⚠️  Usando configuración local de peers")
    except Exception as e:
        print(f"❌ Error en descubrimiento de peers: {e}")
    
    # Sincronización automática al inicio (esperar un poco más)
    await asyncio.sleep(2)
    print("🔄 Sincronizando blockchain al inicio...")
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
