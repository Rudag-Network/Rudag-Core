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
