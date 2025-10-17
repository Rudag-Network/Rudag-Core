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
        self.mining_interval = 60  # 60 segundos entre bloques

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
            print(f"{self.CYAN}║  {self.GREEN}6{self.NC})  Descubrir nuevos peers             {self.CYAN}║{self.NC}")  # NUEVO
            print(f"{self.CYAN}║  {self.RED}7{self.NC})  Volver al menú principal         {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}╚══════════════════════════════════════════════╝{self.NC}")
            print()
            print(f"{self.YELLOW}Selecciona una opción [1-7]: {self.NC}", end="")
            
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
                
            elif choice == "6":  # NUEVA OPCIÓN
                print(f"{self.BLUE}🔍 Descubriendo nuevos peers desde el servidor...{self.NC}")
                result = self.make_request('/network/discover', 'POST')  # Necesitarás crear este endpoint
                if "error" not in str(result):
                    print(f"{self.GREEN}✅ Descubrimiento completado: {result}{self.NC}")
                else:
                    print(f"{self.RED}❌ Error: {result}{self.NC}")
                time.sleep(2)
            
            elif choice == "7":
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
                
                # Espera silenciosa de 60 segundos sin mostrar nada
                time.sleep(self.mining_interval)
            
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
            print(f"{self.CYAN}║  {self.GREEN}1{self.NC})  Ejecutar transaction.sh           {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.GREEN}2{self.NC})  Ejecutar addnodes.sh              {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}║  {self.RED}3{self.NC})  Volver al menú principal         {self.CYAN}║{self.NC}")
            print(f"{self.CYAN}╚══════════════════════════════════════════════╝{self.NC}")
            print()
            print(f"{self.YELLOW}Selecciona una opción [1-3]: {self.NC}", end="")
            
            choice = input().strip()
            
            if choice == "1":
                if os.path.exists("./transaction.sh"):
                    print(f"{self.BLUE}Ejecutando transaction.sh...{self.NC}")
                    try:
                        subprocess.run(["./transaction.sh"], check=True)
                        print(f"{self.GREEN}Script completado{self.NC}")
                    except subprocess.CalledProcessError as e:
                        print(f"{self.RED}Error al ejecutar script: {e}{self.NC}")
                else:
                    print(f"{self.RED}Error: transaction.sh no encontrado{self.NC}")
                time.sleep(2)
                
            elif choice == "2":
                if os.path.exists("./addnodes.sh"):
                    print(f"{self.BLUE}Ejecutando addnodes.sh...{self.NC}")
                    try:
                        subprocess.run(["./addnodes.sh"], check=True)
                        print(f"{self.GREEN}Script completado{self.NC}")
                    except subprocess.CalledProcessError as e:
                        print(f"{self.RED}Error al ejecutar script: {e}{self.NC}")
                else:
                    print(f"{self.RED}Error: addnodes.sh no encontrado{self.NC}")
                time.sleep(2)
                
            elif choice == "3":
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
