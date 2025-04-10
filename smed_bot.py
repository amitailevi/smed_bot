from solders.keypair import Keypair
from solders.rpc import RpcClient
from solders.pubkey import Pubkey
import requests
import time
import random
import base58
import os

# Set the Solana RPC endpoint
RPC_URL = "https://api.mainnet-beta.solana.com"
client = RpcClient(RPC_URL)

# Get private key from environment variable
PRIVATE_KEY = os.getenv("SMED_PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("Please set SMED_PRIVATE_KEY environment variable")

# Convert base58 private key to bytes
private_key_bytes = base58.b58decode(PRIVATE_KEY)
wallet = Keypair.from_bytes(private_key_bytes)

# SMED token mint address
SMED_MINT = Pubkey.from_string("J9DuBB7AFtjwiX2nJbZ1DwHhpnoDBvFtzc8KLscB5Bq1")

def print_wallet_info():
    """Print wallet details"""
    print(f"[WALLET] Public key: {wallet.pubkey()}")

def get_smed_pool():
    """Find SMED liquidity pool"""
    try:
        pairs = requests.get("https://api.raydium.io/v2/main/pairs").json()
        for pair in pairs:
            if SMED_MINT.to_string() in str(pair):
                return pair
        return None
    except Exception as e:
        print(f"[ERROR] Pool search error: {str(e)}")
        return None

def buy_smed():
    """Buy random amount of SMED"""
    try:
        # Random amount between 0.5-3 USD
        amount_usd = random.uniform(0.5, 3.0)
        print(f"[BOT] Attempting to buy SMED worth {amount_usd:.2f}$")
        
        # Find liquidity pool
        pool = get_smed_pool()
        if not pool:
            print("[ERROR] Liquidity pool not found")
            return
        
        # Prepare transaction
        transaction_data = {
            "wallet": wallet.pubkey().to_string(),
            "amountIn": amount_usd,
            "poolId": pool["id"],
            "tokenMint": SMED_MINT.to_string()
        }
        
        # Send transaction to Raydium
        response = requests.post(
            "https://api.raydium.io/v2/main/swap",
            json=transaction_data
        )
        
        if response.status_code == 200:
            print(f"[SUCCESS] Transaction sent successfully!")
            print(f"[INFO] Transaction details: {response.json()}")
        else:
            print(f"[ERROR] Transaction failed: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] An error occurred: {str(e)}")

def run_bot():
    """Run the automated trading bot"""
    print("[BOT] Starting the bot...")
    print_wallet_info()
    
    while True:
        try:
            buy_smed()
            print("[BOT] Waiting 60 seconds until next purchase...")
            time.sleep(60)  # Wait for 1 minute
        except Exception as e:
            print(f"[ERROR] An error occurred: {str(e)}")
            time.sleep(5)  # Wait 5 seconds if error occurs

if __name__ == "__main__":
    run_bot()

