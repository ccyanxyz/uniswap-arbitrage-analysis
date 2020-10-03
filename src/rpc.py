from web3 import HTTPProvider
from web3._utils.request import make_post_request
from common import *

def generate_json_rpc(method, params, request_id=1):
    return {
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
        'id': request_id,
    }

def generate_get_block_by_number_json_rpc(block_numbers, include_transactions):
    for idx, block_number in enumerate(block_numbers):
        yield generate_json_rpc(
            method='eth_getBlockByNumber',
            params=[hex(block_number), include_transactions],
            request_id=idx
        )

def generate_get_reserves_json_rpc(pairs, blockNumber='latest'):
    c = w3.eth.contract(abi=pairABI) 
    for pair in pairs:
        yield generate_json_rpc(
                method='eth_call',
                params=[{
                    'to': pair['address'],
                    'data': c.encodeABI(fn_name='getReserves', args=[]),
                    },
                    hex(blockNumber) if blockNumber != 'latest' else 'latest',
                    ]
                )

def generate_get_receipt_json_rpc(transaction_hashes):
    for idx, transaction_hash in enumerate(transaction_hashes):
        yield generate_json_rpc(
            method='eth_getTransactionReceipt',
            params=[transaction_hash],
            request_id=idx
        )

def rpc_response_batch_to_results(response):
    for response_item in response:
        yield rpc_response_to_result(response_item)


def rpc_response_to_result(response):
    result = response.get('result')
    if result is None:
        error_message = 'result is None in response {}.'.format(response)
        if response.get('error') is None:
            error_message = error_message + ' Make sure Ethereum node is synced.'
            # When nodes are behind a load balancer it makes sense to retry the request in hopes it will go to other,
            # synced node
            raise RetriableValueError(error_message)
        elif response.get('error') is not None and is_retriable_error(response.get('error').get('code')):
            raise RetriableValueError(error_message)
        raise ValueError(error_message)
    return result

class BatchHTTPProvider(HTTPProvider):

    def make_batch_request(self, text):
        self.logger.debug("Making request HTTP. URI: %s, Request: %s",
                          self.endpoint_uri, text)
        request_data = text.encode('utf-8')
        raw_response = make_post_request(
            self.endpoint_uri,
            request_data,
            **self.get_request_kwargs()
        )
        response = self.decode_rpc_response(raw_response)
        self.logger.debug("Getting response HTTP. URI: %s, "
                          "Request: %s, Response: %s",
                          self.endpoint_uri, text, response)
        return response
