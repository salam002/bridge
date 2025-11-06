from web3 import Web3
from eth_account import Account

# create new random account
acct = Account.create()

print("Your new address:", acct.address)
print("Your private key:", acct.key.hex())

# save the private key for later
with open("secret_key.txt", "w") as f:
    f.write(acct.key.hex())

print("Private key saved to secret_key.txt")
