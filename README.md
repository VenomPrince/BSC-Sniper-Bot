# 🚀 BSC Sniper Bot

A high-speed cryptocurrency trading bot for Binance Smart Chain (BSC) that supports both mainnet and testnet operations.

## 🌟 Features

- **Dual Network Support**:
  - BSC Mainnet (real trading)
  - BSC Testnet (practice & testing)

- **Trading Features**:
  - Token sniping (buy tokens immediately when liquidity is added)
  - Take-profit and stop-loss mechanisms
  - Manual and automatic selling
  - Real-time price monitoring
  - New token detection

- **Performance Optimizations**:
  - Multi-node transaction broadcasting
  - Parallel processing
  - Multiple RPC/WSS endpoints
  - Optimized gas pricing
  - Concurrent transaction handling

## 🔧 Setup Instructions

### 1. Prerequisites
```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Wallet Setup
1. Install MetaMask:
   - Visit [https://metamask.io](https://metamask.io)
   - Download and add to your browser
   - Create a new wallet
   - SECURELY SAVE your seed phrase

2. Get Your Private Key:
   - Open MetaMask
   - Click three dots (⋮) menu
   - Select "Account details"
   - Click "Export Private Key"
   - Enter your password
   - Copy the private key

3. Configure Environment:
   - Copy `.env.example` to `.env`
   - Add your private key:
     ```
     PRIVATE_KEY=your_private_key_here
     ```

### 3. Network Setup

#### For Testnet (Recommended for beginners):
1. Add BSC Testnet to MetaMask:
   - Visit [https://chainlist.org](https://chainlist.org)
   - Search for "BSC Testnet"
   - Connect wallet and add network
2. Get Test BNB:
   - Visit [https://testnet.binance.org/faucet-smart](https://testnet.binance.org/faucet-smart)
   - Enter your wallet address
   - Receive free test BNB

#### For Mainnet:
- Ensure you have real BNB in your wallet
- Double-check all settings before trading

## ⚠️ Important Testnet Requirements

Before using the BSC Testnet, please note:

### Prerequisites for Testnet
1. **Mainnet BNB Requirement**:
   - Most BSC Testnet faucets require you to have a small amount of BNB (≥0.002 BNB) on BSC Mainnet
   - This is an anti-spam measure implemented by faucets
   - Without mainnet BNB, you may not be able to get test BNB

### Available Faucets
1. Official BSC Testnet Faucet:
   - URL: https://testnet.binance.org/faucet-smart
   - Requires: ≥0.002 BNB on mainnet
   
2. Alternative Faucets:
   - https://testnet.bnbchain.org/faucet-smart
   - https://faucet.quicknode.com/binance-smart-chain/bnb-testnet
   - https://faucets.chain.link (Select "BNB Chain Testnet")
   
Note: All major faucets currently implement anti-spam measures requiring mainnet balance.

### Solutions
1. **For Testing Without Mainnet BNB**:
   - Consider using local testnet (Ganache)
   - Use alternative test networks
   - Contact development communities for test tokens

2. **For Full Testing**:
   - Acquire small amount of BNB on mainnet first
   - Use verified faucets only
   - Keep minimum required balance for faucet access

## 🚀 Usage

1. Start the bot:
```bash
python sniper_bot.py
```

2. Choose Network:
```
=== Network Selection ===
1. BSC Testnet (for testing)
2. BSC Mainnet (real trading)
```

3. Available Features:
- Buy tokens
- Sell tokens
- Monitor prices
- Detect new tokens

## 📚 Example Usage Guide

Here's a detailed walkthrough of using the bot:

### 1. Initial Setup Example
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your private key
PRIVATE_KEY=abc123...  # Your actual private key here
```

### 2. Running the Bot

```bash
$ python sniper_bot.py

=== Network Selection ===
1. BSC Testnet (for testing)
2. BSC Mainnet (real trading)

Choose network (1-2): 1

⚠️ Using BSC Testnet - Get free test BNB from: https://testnet.binance.org/faucet-smart

=== Crypto Sniper Bot Menu ===
1. Buy Token
2. Sell Token
3. Monitor Price
4. Detect New Tokens
5. Exit

Choose an option (1-5):
```

### 3. Feature Examples

#### A. Buying Tokens
```bash
Choose an option (1-5): 1

=== Buy Token ===
Enter token address (or 'back' to return): 0x123...
Enter amount of BNB to spend: 0.1
🔍 Analyzing token...
✅ Token verified
💰 Current Price: 0.00234 BNB
🚀 Sending buy transaction...
✅ Transaction successful! Hash: 0xabc...
```

#### B. Price Monitoring
```bash
Choose an option (1-5): 3

=== Monitor Token ===
Enter token address: 0x123...
💰 Current Price: 0.00234 BNB

Set take-profit (% increase) [default=50]: 100
Set stop-loss (% decrease) [default=20]: 25

📊 Monitoring price...
Current: 0.00234 BNB
Target: 0.00468 BNB (take-profit)
Stop: 0.00175 BNB (stop-loss)

🔄 Price update: 0.00240 BNB (+2.5%)
🔄 Price update: 0.00255 BNB (+9.0%)
...
```

#### C. New Token Detection
```bash
Choose an option (1-5): 4

=== New Token Detection ===
Press Ctrl+C to stop monitoring

👀 Monitoring PancakeSwap for new tokens...

🆕 New token detected!
Address: 0x789...
Initial Liquidity: 50 BNB
Pair created with: WBNB
Time: 2024-01-20 14:30:45

Would you like to buy? (y/n): n
Continuing monitoring...
```

### 4. Advanced Examples

#### Auto-Buying with Take-Profit
```bash
# Scenario: Buy token and set up automatic take-profit
Choose an option (1-5): 1

Enter token address: 0x123...
Enter amount of BNB to spend: 0.1
Set take-profit (%): 50

🔄 Transaction flow:
1. Checking token contract... ✅
2. Verifying liquidity... ✅
3. Sending buy transaction... ✅
4. Setting up price monitoring... ✅

💫 Bot will automatically:
- Monitor price changes
- Sell when 50% profit is reached
- Handle gas optimization
- Manage slippage
```

#### Multi-Node Broadcasting Example
```bash
# When buying high-demand tokens
🔄 Broadcasting to multiple nodes:
Node 1 (Primary): Connected ✅
Node 2: Connected ✅
Node 3: Connected ✅

⚡ Speed Test Results:
- Node 1: 45ms
- Node 2: 38ms
- Node 3: 52ms

🚀 Using fastest node for transaction...
```

### 5. Error Handling Examples

```bash
# Example: Insufficient Balance
Error: Insufficient BNB balance
Required: 0.1 BNB
Available: 0.05 BNB
Solution: Add more BNB to wallet

# Example: High Slippage Warning
⚠️ Warning: High price impact detected!
Expected slippage: 25%
Recommended: Reduce trade size or increase slippage tolerance

# Example: Token Security Check
🔍 Token Security Scan:
✅ Contract verified
❌ Honeypot check failed
⚠️ High sell tax detected (25%)
Recommendation: Avoid this token
```

### 6. Performance Metrics Example

```bash
📊 Transaction Performance:
- Submission time: 0.03s
- Block confirmation: 2.5s
- Gas optimization: Saved 0.001 BNB
- Node latency: 45ms average

🔧 System Status:
- Connected nodes: 3/3
- WebSocket status: Active
- Memory usage: 124MB
- Active monitors: 2
```

These examples demonstrate:
- Real-world usage scenarios
- Expected outputs
- Error handling
- Performance metrics
- Security checks
- Multi-node operations

Tips for Best Results:
1. Always start with small test amounts
2. Monitor gas prices before large transactions
3. Use price monitoring for volatile tokens
4. Keep track of transaction hashes
5. Check token security before buying

## 🔐 Security Tips

1. **Wallet Safety**:
   - NEVER share your private key
   - Use a dedicated trading wallet
   - Keep minimal funds in trading wallet
   - Backup seed phrase securely

2. **Testing**:
   - Start with testnet
   - Test all features before real trading
   - Use small amounts initially

3. **Environment**:
   - Keep `.env` file secure
   - Never commit private keys
   - Don't share wallet details

## 🌐 Network Details

### BSC Testnet
- Router: `0xD99D1c33F9fC3444f8101754aBC46c52416550D1`
- WBNB: `0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd`
- Factory: `0x6725F303b657a9451d8BA641348b6761A6CC7a17`

### BSC Mainnet
- Router: `0x10ED43C718714eb63d5aA57B78B54704E256024E`
- WBNB: `0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c`
- Factory: `0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73`

## ⚠️ Disclaimer

This bot is for educational purposes. Crypto trading carries high risk:
- Only trade what you can afford to lose
- Test thoroughly on testnet first
- No guarantee of profits
- Market conditions can change rapidly
- DYOR (Do Your Own Research)

## 🔍 Troubleshooting

Common issues:
1. "Private key not found":
   - Check `.env` file exists
   - Verify private key format

2. "Insufficient funds":
   - Ensure wallet has BNB for gas
   - For testnet: use faucet
   - For mainnet: add BNB to wallet

3. "Transaction failed":
   - Check gas settings
   - Verify token contract
   - Ensure sufficient slippage

## 📞 Support

For issues and feature requests:
1. Check troubleshooting guide
2. Verify network settings
3. Test on testnet first
4. Document any errors

Remember: NEVER share your private keys or seed phrase when seeking support!

## Even the README.md file is 375 lines long! 🤓
