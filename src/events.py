import threading
from eth_abi import decode_abi
from common import *
from rpc import *

batch_provider = BatchHTTPProvider(config[network]['http'])
def get_reserves(pairs, blockNumber='latest'):
    r = list(generate_get_reserves_json_rpc(pairs, blockNumber))
    resp = batch_provider.make_batch_request(json.dumps(r))
    results = list(rpc_response_batch_to_results(resp))
    for i in range(len(results)):
        res = decode_abi(['uint256', 'uint256', 'uint256'], bytes.fromhex(results[i][2:]))
        pairs[i]['reserve0'] = res[0]
        pairs[i]['reserve1'] = res[1]
    return pairs

def get_receipts(txhashes):
    receipts_rpc = list(generate_get_receipt_json_rpc(txhashes))
    resp = batch_provider.make_batch_request(json.dumps(receipts_rpc))
    results = rpc_response_batch_to_results(resp)
    return list(results)

def get_block_txhashes(blockNumber='latest'):
    block = w3.eth.getBlock(blockNumber)
    txhashes = [t.hex() for t in block['transactions']]
    return txhashes

sync_topic = "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"
swap_topic = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
mint_topic = "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f"
burn_topic = "0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496"
def process_receipts(receipts, pairsDict, pairs):
    c = w3.eth.contract(abi=pairABI)
    for r in receipts:
        if len(r['logs']) == 0:
            continue
        for log in r['logs']:
            if log['topics'][0] not in [sync_topic]:
                continue
            if log['address'] not in pairsDict.keys():
                continue
            # process event
            event = None
            if log['topics'][0] == sync_topic:
                event = c.events.Sync.parseLog(log)
                pairs[pairsDict[log['address']]['arrIndex']]['reserve0'] = event['reserve0']
                pairs[pairsDict[log['address']]['arrIndex']]['reserve1'] = event['reserve1']
    return pairs
