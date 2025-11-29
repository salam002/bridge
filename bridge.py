import time
from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware
from datetime import datetime
import json
import pandas as pd


def connect_to(chain):
    if chain == 'source':  
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" 

    if chain == 'destination':  
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" 

    if chain in ['source','destination']:
        w3 = Web3(Web3.HTTPProvider(api_url))
       
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info):
    """
        Load the contract_info file into a dictionary
        This function is used by the autograder and will likely be useful to you
    """
    try:
        with open(contract_info, 'r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( f"Failed to read contract info\nPlease contact your instructor\n{e}" )
        return 0
    return contracts[chain]



def scan_blocks(chain, contract_info="contract_info.json"):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return 0
  
    w3 = connect_to(chain)
    contracts = get_contract_info(chain, contract_info)
    contract_address = contracts["address"]
    abi = contracts["abi"]
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    lb = w3.eth.block_number 
    fb = max(lb - 20, 0) 
    tb = lb 

    if chain == "source":
        
        try:
            event_filter = contract.events.Deposit().create_filter(from_block=fb, to_block=tb)
            deposit_events = event_filter.get_all_entries()

            dst_contract_info = get_contract_info("destination", contract_info)
            dst_w3 = connect_to("destination")
            dst_warden_key = dst_contract_info["warden"]
            dst_warden = dst_w3.eth.account.from_key(dst_warden_key)
            
           
            nonce = dst_w3.eth.get_transaction_count(dst_warden.address, 'pending')
            
            
            dst_contract = dst_w3.eth.contract(address=dst_contract_info["address"], abi=dst_contract_info["abi"])

            for idx, evt in enumerate(deposit_events):
                print(f"Deposit event detected: {evt}")
                
               
                txn = dst_contract.functions.wrap(
                    evt.args['token'],
                    evt.args['recipient'],
                    evt.args['amount']
                ).build_transaction({
                    'from': dst_warden.address,
                    'chainId': 97,
                    'gas': 500000,
                    'gasPrice': dst_w3.to_wei('10', 'gwei'),
                    'nonce': nonce 
                })
                
                signed_txn = dst_w3.eth.account.sign_transaction(txn, private_key=dst_warden_key)
                tx_hash = dst_w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                print(f"Bridged to destination: {tx_hash.hex()}")
                
              
                nonce += 1 
                time.sleep(1) 
        except Exception as e:
            print(f"Error scanning Deposit events: {e}")

    elif chain == "destination":
      
        try:
            event_filter = contract.events.Unwrap().create_filter(from_block=fb, to_block=tb)
            unwrap_events = event_filter.get_all_entries()
            
    
            src_contract_info = get_contract_info("source", contract_info)
            src_w3 = connect_to("source")
            src_warden_key = src_contract_info["warden"]
            src_warden = src_w3.eth.account.from_key(src_warden_key)
            
           
            nonce = src_w3.eth.get_transaction_count(src_warden.address, 'pending')
      
            src_contract = src_w3.eth.contract(address=src_contract_info["address"], abi=src_contract_info["abi"])

            for idx, evt in enumerate(unwrap_events):
                print(f"Unwrap event detected: {evt}")
                
          
                txn = src_contract.functions.withdraw(
                    evt.args['underlying_token'],
                    evt.args['to'],
                    evt.args['amount']
                ).build_transaction({
                    'from': src_warden.address,
                    'chainId': 43113,
                    'gas': 500000,
                    'gasPrice': src_w3.to_wei('25', 'gwei'),
                    'nonce': nonce 
                })
                
                signed_txn = src_w3.eth.account.sign_transaction(txn, private_key=src_warden_key)
                tx_hash = src_w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                print(f"Bridged to source: {tx_hash.hex()}")
                
              
                nonce += 1
                time.sleep(1)
        except Exception as e:
            print(f"Error scanning Unwrap events: {e}")

if __name__ == "__main__":
    print("Scanning Source chain (Avalanche)...")
    scan_blocks("source")
    print("Finished scanning Source chain.\n")

    print("Scanning Destination chain (BSC)...")
    scan_blocks("destination")
    print("Finished scanning Destination chain.\n")