import json
from web3 import HTTPProvider, Web3

config = json.load(open('config.json'))
rpcs = config['https']

for rpc in rpcs:
    w3 = Web3(HTTPProvider(rpc))
    try:
        bn = w3.eth.blockNumber
        print(rpc, bn)
    except:
        print('bad:', rpc)
