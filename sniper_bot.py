from web3 import Web3
from eth_account import Account
import json
import time
import os
from dotenv import load_dotenv
import asyncio
import websockets
import aiohttp
from asyncio_pool import AioPool
from concurrent.futures import ThreadPoolExecutor
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Network configurations
NETWORKS = {
    'mainnet': {
        'name': 'BSC Mainnet',
        'rpc_endpoints': [
            "https://bsc-dataseed1.binance.org/",
            "https://bsc-dataseed2.binance.org/",
            "https://bsc-dataseed3.binance.org/",
            "https://bsc-dataseed4.binance.org/"
        ],
        'wss_endpoints': [
            "wss://bsc-ws-node.nariox.org:443",
            "wss://bsc.getblock.io/mainnet/",
            "wss://bsc.publicnode.com",
        ],
        'router': "0x10ED43C718714eb63d5aA57B78B54704E256024E",
        'wbnb': "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        'factory': "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
    },
    'testnet': {
        'name': 'BSC Testnet',
        'rpc_endpoints': [
            "https://data-seed-prebsc-1-s1.binance.org:8545/",
            "https://data-seed-prebsc-2-s1.binance.org:8545/",
            "https://data-seed-prebsc-1-s2.binance.org:8545/"
        ],
        'wss_endpoints': [
            "wss://bsc-testnet.publicnode.com",
        ],
        'router': "0xD99D1c33F9fC3444f8101754aBC46c52416550D1",  # PancakeSwap Testnet Router
        'wbnb': "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd",    # WBNB Testnet
        'factory': "0x6725F303b657a9451d8BA641348b6761A6CC7a17"   # PancakeSwap Testnet Factory
    }
}

# Default to testnet for safety
NETWORK = NETWORKS['testnet']

# Load your private key from environment variable
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
if not PRIVATE_KEY:
    raise ValueError("Please set your PRIVATE_KEY in the .env file")

# Your wallet address
account = Account.from_key(PRIVATE_KEY)
WALLET_ADDRESS = account.address

class SniperBot:
    def __init__(self, network='testnet'):
        """
        Initialize bot with network selection
        network: 'mainnet' or 'testnet'
        """
        self.network = NETWORKS[network]
        logger.info(f"Initializing bot on {self.network['name']}")
        
        self.rpc_endpoints = self.network['rpc_endpoints']
        self.wss_endpoints = self.network['wss_endpoints']
        self.router_address = self.network['router']
        self.wbnb_address = self.network['wbnb']
        self.factory_address = self.network['factory']
        
        self.w3 = None
        self.ws = None
        self.session = None
        self.router_contract = None
        self.default_gas_limit = 300000
        self.gas_price_multiplier = 1.1
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.connection_pool = None

    async def initialize(self):
        """Initialize all connections in parallel"""
        self.session = aiohttp.ClientSession()
        self.connection_pool = AioPool(size=len(self.rpc_endpoints))
        
        # Initialize all connections in parallel
        await asyncio.gather(
            self._initialize_web3(),
            self._initialize_websocket(),
            self._setup_contracts()
        )

    async def _initialize_web3(self):
        """Initialize the fastest Web3 connection"""
        async def check_endpoint(endpoint):
            try:
                w3 = Web3(Web3.HTTPProvider(endpoint))
                start = time.time()
                block = await self.executor.submit(w3.eth.block_number)
                latency = time.time() - start
                return (latency, w3)
            except Exception as e:
                logger.error(f"Error connecting to {endpoint}: {str(e)}")
                return (float('inf'), None)

        # Check all endpoints in parallel
        results = await asyncio.gather(*[check_endpoint(ep) for ep in self.rpc_endpoints])
        fastest = min(results, key=lambda x: x[0])
        self.w3 = fastest[1] or Web3(Web3.HTTPProvider(self.rpc_endpoints[0]))

    async def _initialize_websocket(self):
        """Initialize WebSocket connection"""
        for endpoint in self.wss_endpoints:
            try:
                self.ws = await websockets.connect(endpoint)
                break
            except Exception as e:
                logger.error(f"WebSocket connection failed for {endpoint}: {str(e)}")
                continue

    async def _setup_contracts(self):
        """Setup contract instances"""
        self.router_contract = self.w3.eth.contract(
            address=self.router_address,
            abi=[
                {
                    "inputs": [
                        {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                        {"internalType": "address[]", "name": "path", "type": "address[]"},
                        {"internalType": "address", "name": "to", "type": "address"},
                        {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                    ],
                    "name": "swapExactETHForTokens",
                    "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                    "stateMutability": "payable",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                        {"internalType": "address[]", "name": "path", "type": "address[]"}
                    ],
                    "name": "getAmountsOut",
                    "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                        {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                        {"internalType": "address[]", "name": "path", "type": "address[]"},
                        {"internalType": "address", "name": "to", "type": "address"},
                        {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                    ],
                    "name": "swapExactTokensForETH",
                    "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
        )

    async def snipe_token(self, token_address, amount_bnb, slippage=49):
        """Ultra-fast token sniping with parallel processing"""
        try:
            # Prepare all transaction parameters in parallel
            amount_wei = self.w3.to_wei(amount_bnb, 'ether')
            path = [self.wbnb_address, token_address]
            deadline = int(time.time()) + 60

            # Get gas price and nonce in parallel
            gas_price, nonce = await asyncio.gather(
                self.executor.submit(self.w3.eth.gas_price),
                self.executor.submit(self.w3.eth.get_transaction_count, WALLET_ADDRESS)
            )

            # Optimize gas price
            optimized_gas_price = int(gas_price * self.gas_price_multiplier)

            # Prepare transaction
            transaction = self.router_contract.functions.swapExactETHForTokens(
                0,  # Accept any amount of tokens
                path,
                WALLET_ADDRESS,
                deadline
            ).build_transaction({
                'from': WALLET_ADDRESS,
                'value': amount_wei,
                'gas': self.default_gas_limit,
                'gasPrice': optimized_gas_price,
                'nonce': nonce,
            })

            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)

            # Send transaction to multiple nodes in parallel for fastest confirmation
            async def send_to_node(endpoint):
                try:
                    w3 = Web3(Web3.HTTPProvider(endpoint))
                    tx_hash = await self.executor.submit(
                        w3.eth.send_raw_transaction,
                        signed_txn.rawTransaction
                    )
                    return tx_hash
                except Exception:
                    return None

            # Try all nodes in parallel
            tx_hashes = await asyncio.gather(*[
                send_to_node(endpoint) for endpoint in self.rpc_endpoints
            ])
            
            # Use the first successful transaction hash
            tx_hash = next((h for h in tx_hashes if h is not None), None)
            if not tx_hash:
                raise Exception("Failed to send transaction to any node")

            logger.info(f"Transaction sent! Hash: {tx_hash.hex()}")

            # Wait for receipt with optimized polling
            receipt = await self._wait_for_transaction_fast(tx_hash)
            logger.info(f"Transaction confirmed! Status: {receipt['status']}")
            return receipt

        except Exception as e:
            logger.error(f"Error sniping token: {str(e)}")
            return None

    async def _wait_for_transaction_fast(self, tx_hash, timeout=60):
        """Enhanced transaction waiting with parallel receipt checking"""
        start_time = time.time()
        async def check_receipt(endpoint):
            try:
                w3 = Web3(Web3.HTTPProvider(endpoint))
                receipt = await self.executor.submit(
                    w3.eth.get_transaction_receipt,
                    tx_hash
                )
                return receipt
            except Exception:
                return None

        while time.time() - start_time < timeout:
            # Check all nodes in parallel
            receipts = await asyncio.gather(*[
                check_receipt(endpoint) for endpoint in self.rpc_endpoints
            ])
            
            # Use the first valid receipt
            receipt = next((r for r in receipts if r is not None), None)
            if receipt:
                return receipt
                
            await asyncio.sleep(0.1)

        raise TimeoutError("Transaction confirmation timeout")

    async def check_token_price(self, token_address):
        """Check the current price of the token in BNB"""
        try:
            # Get token contract
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=['function balanceOf(address) view returns (uint256)']
            )
            
            # Amount of tokens for 1 BNB (simplified)
            amount_in = self.w3.to_wei(1, 'ether')
            path = [self.wbnb_address, token_address]
            
            # Get amount out
            amounts = self.router_contract.functions.getAmountsOut(
                amount_in,
                path
            ).call()
            
            return amounts[1] / (10 ** 18)  # Convert to human readable
        except Exception as e:
            logger.error(f"Error checking price: {str(e)}")
            return None

    async def sell_token(self, token_address, amount_tokens=None, sell_all=False):
        """
        Sells tokens for BNB
        
        Args:
            token_address (str): Token address to sell
            amount_tokens (float): Amount of tokens to sell
            sell_all (bool): If True, sells entire balance
        """
        try:
            # Get token contract
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=[
                    'function balanceOf(address) view returns (uint256)',
                    'function approve(address spender, uint256 amount) returns (bool)'
                ]
            )
            
            # Get token balance
            if sell_all:
                amount_wei = token_contract.functions.balanceOf(WALLET_ADDRESS).call()
            else:
                amount_wei = self.w3.to_wei(amount_tokens, 'ether')
            
            if amount_wei == 0:
                logger.info("No tokens to sell!")
                return None
                
            # Approve tokens
            approve_txn = token_contract.functions.approve(
                self.router_address,
                amount_wei
            ).build_transaction({
                'from': WALLET_ADDRESS,
                'gas': 250000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(WALLET_ADDRESS),
            })
            
            # Sign and send approval
            signed_approve = self.w3.eth.account.sign_transaction(approve_txn, PRIVATE_KEY)
            tx_approve = self.w3.eth.send_raw_transaction(signed_approve.rawTransaction)
            self.w3.eth.wait_for_transaction_receipt(tx_approve)
            
            # Prepare sell transaction
            path = [token_address, self.wbnb_address]
            deadline = int(time.time()) + 60
            
            # Get minimum BNB out (with slippage)
            amounts = self.router_contract.functions.getAmountsOut(
                amount_wei,
                path
            ).call()
            min_bnb = int(amounts[1] * 0.95)  # 5% slippage
            
            # Create sell transaction
            sell_txn = self.router_contract.functions.swapExactTokensForETH(
                amount_wei,
                min_bnb,
                path,
                WALLET_ADDRESS,
                deadline
            ).build_transaction({
                'from': WALLET_ADDRESS,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(WALLET_ADDRESS),
            })
            
            # Sign and send sell transaction
            signed_txn = self.w3.eth.account.sign_transaction(sell_txn, PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"Sell transaction sent! Hash: {tx_hash.hex()}")
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(f"Sell transaction confirmed! Status: {receipt['status']}")
            return receipt
            
        except Exception as e:
            logger.error(f"Error selling token: {str(e)}")
            return None

    async def monitor_price_and_sell(self, token_address, buy_price, take_profit=2.0, stop_loss=0.8):
        """
        Monitors token price and sells based on take-profit or stop-loss
        
        Args:
            token_address (str): Token to monitor
            buy_price (float): Price at which you bought
            take_profit (float): Multiplier for take profit (2.0 = 100% profit)
            stop_loss (float): Multiplier for stop loss (0.8 = 20% loss)
        """
        while True:
            current_price = await self.check_token_price(token_address)
            if not current_price:
                continue
                
            logger.info(f"Current price: {current_price}")
            
            # Check take profit
            if current_price >= (buy_price * take_profit):
                logger.info(f"Take profit triggered! Selling tokens...")
                await self.sell_token(token_address, sell_all=True)
                break
                
            # Check stop loss
            if current_price <= (buy_price * stop_loss):
                logger.info(f"Stop loss triggered! Selling tokens...")
                await self.sell_token(token_address, sell_all=True)
                break
                
            await asyncio.sleep(1)  # Check every second

    async def monitor_new_tokens(self):
        """Monitor for new token pairs on PancakeSwap"""
        # PancakeSwap factory address
        factory_address = self.factory_address
        factory_abi = [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "type": "address", "name": "token0"},
                    {"indexed": True, "type": "address", "name": "token1"},
                    {"indexed": False, "type": "address", "name": "pair"},
                    {"indexed": False, "type": "uint256", "name": ""}
                ],
                "name": "PairCreated",
                "type": "event"
            }
        ]

        # Create factory contract instance
        factory_contract = self.w3.eth.contract(
            address=factory_address,
            abi=factory_abi
        )

        logger.info("\nMonitoring for new token pairs...")
        logger.info("When a new token is detected, you'll see its details here.")
        logger.info("Press Ctrl+C to stop monitoring\n")

        # Get the latest block number
        latest_block = self.w3.eth.block_number

        try:
            while True:
                try:
                    # Get PairCreated events
                    events = factory_contract.events.PairCreated.get_logs(
                        fromBlock=latest_block
                    )

                    for event in events:
                        token0 = event['args']['token0']
                        token1 = event['args']['token1']
                        pair = event['args']['pair']

                        # If one of the tokens is WBNB
                        if token0.lower() == self.wbnb_address.lower() or token1.lower() == self.wbnb_address.lower():
                            new_token = token1 if token0.lower() == self.wbnb_address.lower() else token0
                            
                            # Get initial liquidity
                            try:
                                initial_price = await self.check_token_price(new_token)
                                liquidity = "Price: {} BNB per token".format(initial_price) if initial_price else "Unable to get price"
                            except:
                                liquidity = "Unable to get price"

                            logger.info(f"\n=== New Token Detected! ===")
                            logger.info(f"Token Address: {new_token}")
                            logger.info(f"Pair Address: {pair}")
                            logger.info(f"Initial {liquidity}")
                            
                            # Ask if user wants to snipe this token
                            if input("\nWould you like to snipe this token? (y/n): ").lower() == 'y':
                                return new_token

                    latest_block = self.w3.eth.block_number
                    await asyncio.sleep(1)  # Poll every second

                except Exception as e:
                    logger.error(f"Error in monitoring: {str(e)}")
                    await asyncio.sleep(1)
                    continue

        except KeyboardInterrupt:
            logger.info("\nStopped monitoring for new tokens")
            return None

async def handle_buy(network):
    """Handle the buy token process"""
    while True:
        print("\n=== Buy Token ===")
        token_address = input("Enter token address to snipe (or 'back' to return): ")
        if token_address.lower() == 'back':
            return
            
        try:
            amount_bnb = float(input("Enter amount of BNB to spend (or 0 to go back): "))
            if amount_bnb <= 0:
                return
                
            print(f"\nStarting to snipe token: {token_address}")
            bot = SniperBot(network)
            await bot.initialize()
            receipt = await bot.snipe_token(token_address, amount_bnb)
            
            if receipt and receipt['status'] == 1:
                print("\nBuy successful! Starting price monitoring...")
                initial_price = await bot.check_token_price(token_address)
                if initial_price:
                    while True:
                        try:
                            take_profit = float(input("\nEnter take profit multiplier (e.g., 2.0 for 100% profit, 0 to go back): "))
                            if take_profit <= 0:
                                return
                            stop_loss = float(input("Enter stop loss multiplier (e.g., 0.8 for 20% loss, 0 to go back): "))
                            if stop_loss <= 0:
                                return
                            if stop_loss >= take_profit:
                                print("\nError: Stop loss must be less than take profit!")
                                continue
                            break
                        except ValueError:
                            print("\nPlease enter valid numbers!")
                            
                    print("\nMonitoring price...")
                    await bot.monitor_price_and_sell(token_address, initial_price, take_profit, stop_loss)
            return
            
        except ValueError:
            print("\nPlease enter a valid BNB amount!")
        except Exception as e:
            print(f"\nError: {str(e)}")
            time.sleep(2)
            return

async def handle_sell(network):
    """Handle the sell token process"""
    while True:
        print("\n=== Sell Token ===")
        token_address = input("Enter token address to sell (or 'back' to return): ")
        if token_address.lower() == 'back':
            return
            
        sell_all = input("Sell all tokens? (y/n/back): ").lower()
        if sell_all == 'back':
            return
            
        bot = SniperBot(network)
        await bot.initialize()
        if sell_all == 'y':
            await bot.sell_token(token_address, sell_all=True)
        else:
            try:
                amount = float(input("Enter amount of tokens to sell (0 to go back): "))
                if amount <= 0:
                    return
                await bot.sell_token(token_address, amount_tokens=amount)
            except ValueError:
                print("\nPlease enter a valid amount!")
                continue
        return

async def handle_monitor(network):
    """Handle the price monitoring process"""
    while True:
        print("\n=== Monitor Token ===")
        token_address = input("Enter token address to monitor (or 'back' to return): ")
        if token_address.lower() == 'back':
            return
            
        bot = SniperBot(network)
        await bot.initialize()
        current_price = await bot.check_token_price(token_address)
        
        if current_price:
            while True:
                try:
                    take_profit = float(input("\nEnter take profit multiplier (e.g., 2.0 for 100% profit, 0 to go back): "))
                    if take_profit <= 0:
                        return
                    stop_loss = float(input("Enter stop loss multiplier (e.g., 0.8 for 20% loss, 0 to go back): "))
                    if stop_loss <= 0:
                        return
                    if stop_loss >= take_profit:
                        print("\nError: Stop loss must be less than take profit!")
                        continue
                    break
                except ValueError:
                    print("\nPlease enter valid numbers!")
                    
            print("\nStarting price monitoring...")
            await bot.monitor_price_and_sell(token_address, current_price, take_profit, stop_loss)
        return

async def handle_token_detection(network):
    """Handle the new token detection process"""
    print("\n=== New Token Detection ===")
    print("This will monitor PancakeSwap for new token launches.")
    print("When a new token is detected, you'll have the option to snipe it.")
    print("Press Ctrl+C to stop monitoring\n")

    bot = SniperBot(network)
    await bot.initialize()
    token_address = await bot.monitor_new_tokens()

    if token_address:
        print(f"\nPreparing to snipe token: {token_address}")
        try:
            amount_bnb = float(input("Enter amount of BNB to spend (or 0 to go back): "))
            if amount_bnb <= 0:
                return

            receipt = await bot.snipe_token(token_address, amount_bnb)
            
            if receipt and receipt['status'] == 1:
                print("\nBuy successful! Starting price monitoring...")
                initial_price = await bot.check_token_price(token_address)
                if initial_price:
                    while True:
                        try:
                            take_profit = float(input("\nEnter take profit multiplier (e.g., 2.0 for 100% profit, 0 to go back): "))
                            if take_profit <= 0:
                                return
                            stop_loss = float(input("Enter stop loss multiplier (e.g., 0.8 for 20% loss, 0 to go back): "))
                            if stop_loss <= 0:
                                return
                            if stop_loss >= take_profit:
                                print("\nError: Stop loss must be less than take profit!")
                                continue
                            break
                        except ValueError:
                            print("\nPlease enter valid numbers!")
                    
                    print("\nMonitoring price...")
                    await bot.monitor_price_and_sell(token_address, initial_price, take_profit, stop_loss)

        except ValueError:
            print("\nPlease enter a valid BNB amount!")
        except Exception as e:
            print(f"\nError: {str(e)}")
            time.sleep(2)

async def display_menu():
    """Display the main menu and get user choice"""
    while True:
        print("\n=== Crypto Sniper Bot Menu ===")
        print("1. Buy new token (Snipe)")
        print("2. Sell existing token")
        print("3. Monitor token price")
        print("4. Detect New Tokens")
        print("5. Exit")
        choice = input("\nChoose an option (1-5): ")
        
        if choice in ['1', '2', '3', '4', '5']:
            return choice
        else:
            print("\nInvalid choice! Please try again.")
            time.sleep(1)

async def main():
    while True:
        # Network selection
        print("\n=== Network Selection ===")
        print("1. BSC Testnet (for testing)")
        print("2. BSC Mainnet (real trading)")
        network = input("\nChoose network (1-2): ")
        
        if network == "1":
            network = "testnet"
            print("\n⚠️ Using BSC Testnet - Get free test BNB from: https://testnet.binance.org/faucet-smart")
        elif network == "2":
            confirm = input("\n⚠️ WARNING: You are about to use real BNB. Continue? (yes/no): ")
            if confirm.lower() != 'yes':
                continue
            network = "mainnet"
        else:
            print("\nInvalid choice!")
            continue
            
        while True:
            choice = await display_menu()
            
            if choice == '1':
                await handle_buy(network)
            elif choice == '2':
                await handle_sell(network)
            elif choice == '3':
                await handle_monitor(network)
            elif choice == '4':
                await handle_token_detection(network)
            elif choice == '5':
                break
                
            time.sleep(1)
            
        another = input("\nSwitch network? (yes/no): ")
        if another.lower() != 'yes':
            print("\nThank you for using Crypto Sniper Bot!")
            break

if __name__ == "__main__":
    asyncio.run(main())
