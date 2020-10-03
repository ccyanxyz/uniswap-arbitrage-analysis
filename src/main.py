import json
import requests
import time
import random
from thread import *
from common import *
from dfs import *
from events import *

all_pairs = json.load(open('files/pairs.json'))

pairs, pairsDict = selectPairs(all_pairs)
tokenIn = startToken
tokenOut = tokenIn
startToken = tokenIn
currentPairs = []
path = [tokenIn]
bestTrades = []

def printMoney(amountIn, p, gasPrice, profit):
    deadline = int(time.time()) + 600
    tx = printer.functions.printMoney(startToken['address'], amountIn, amountIn, p, deadline).buildTransaction({
        'from': address,
        'value': 0,
        'gasPrice': gasPrice,
        'gas': 1500000,
        "nonce": w3.eth.getTransactionCount(address),
        })
    try:
        gasEstimate = w3.eth.estimateGas(tx)
        print('estimate gas cost:', gasEstimate*gasPrice/1e18)
    except Exception as e:
        print('gas estimate err:', e)
        return None
    if config['start'] == 'usdt' or config['start'] == 'usdc' or config['start'] == 'dai':
        if gasEstimate * gasPrice / 1e18 * 360 >= profit/pow(10, startToken['decimal']):
            print('gas too much, give up...')
            return None
    if config['start'] == 'weth' and gasEstimate * gasPrice >= profit:
        print('gas too much, give up...')
        return None
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=privkey)
    try:
        txhash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return txhash.hex()
    except:
        return None

def flashPrintMoney(amountIn, p, gasPrice, profit):
    tx = printer.functions.flashPrintMoney(startToken['address'], amountIn, p).buildTransaction({
        'from': address,
        'value': 0,
        'gasPrice': gasPrice,
        'gas': 1500000,
        "nonce": w3.eth.getTransactionCount(address),
        })
    try:
        gasEstimate = w3.eth.estimateGas(tx)
        print('estimate gas cost:', gasEstimate*gasPrice/1e18)
    except Exception as e:
        print('gas estimate err:', e)
        return None
    if config['start'] == 'usdt' or config['start'] == 'usdc' or config['start'] == 'dai':
        if gasEstimate * gasPrice / 1e18 * 360 >= profit/pow(10, startToken['decimal']):
            print('gas too much, give up...')
            return None
    if config['start'] == 'weth' and gasEstimate * gasPrice >= profit:
        print('gas too much, give up...')
        return None
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=privkey)
    try:
        txhash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return txhash.hex()
    except:
        return None

def doTrade(balance, trade):
    p = [t['address'] for t in trade['path']]
    amountIn = int(trade['optimalAmount'])
    useFlash = False
    if amountIn > balance:
        useFlash = True
    minOut = int(amountIn)
    to = config['address']
    deadline = int(time.time()) + 600
    print(amountIn, minOut, p, to, deadline)
    try:
        # amountsOut = uni.get_amounts_out(amountIn, p)
        amountsOut = [int(trade['outputAmount'])]
        print('amountsOut', amountsOut)
    except Exception as e:
        print('there is a fucking exception!')
        print(e)
        return
    if amountsOut[-1] > amountIn:
        gasPrice = int(gasnow()['rapid']*1.2)
        # uni.set_gas(int(gasnow()['rapid']*1.1))
        # txhash = uni.swap_exact_tokens_for_tokens(amountIn, minOut, p, to, deadline)
        # approve(startToken['address'], printer_addr, address, amountIn, gasPrice)
        # txhash = doTradeSwap(amountIn, p, deadline, gasPrice)
        if useFlash:
            txhash = flashPrintMoney(amountIn, p, gasPrice, amountsOut[-1]-amountIn)
        else:
            txhash = printMoney(amountIn, p, gasPrice, amountsOut[-1]-amountIn)
        return txhash
    return None

needChangeKey = False
def get_reserves_batch_mt(pairs):
    global needChangeKey
    if len(pairs) <= 200:
        new_pairs = get_reserves(pairs)
    else:
        s = 0
        threads = []
        while s < len(pairs):
            e = s + 200
            if e > len(pairs):
                e = len(pairs)
            t = MyThread(func=get_reserves, args=(pairs[s:e],))
            t.start()
            threads.append(t)
            s = e
        new_pairs = []
        for t in threads:
            t.join()
            ret = t.get_result()
            if not ret:
                needChangeKey = True
            new_pairs.extend(ret)
    return new_pairs

last_key = 0
def main():
    global pairs, pairsDict, uni, w3, printer, last_key, needChangeKey
    if config['pairs'] == 'random':
        pairs, pairsDict = selectPairs(all_pairs)
    start = time.time()
    print('pairs:', len(pairs))
    try:
        # pairs = get_reserves(pairs)
        pairs = get_reserves_batch_mt(pairs)
        if needChangeKey:
            needChangeKey = False
            l = len(config['https'])
            http_addr = config['https'][(last_key+1)%l]
            last_key += 1
            last_key %= l
            uni = UniswapV2Client(address, privkey, http_addr)
            w3 = Web3(HTTPProvider(http_addr, request_kwargs={'timeout': 6000}))
            printer = w3.eth.contract(address=printer_addr, abi=printer_abi)
            print('key changed:', http_addr)
            return
    except Exception as e:
        print('get_reserves err:', e)
        # raise
        return
    end = time.time()
    print('update cost:', end - start, 's')
    trades = findArb(pairs, tokenIn, tokenOut, maxHops, currentPairs, path, bestTrades)
    if len(trades) == 0:
        return
    print('max_profit:', trades[0]['p'])
    end1 = time.time()
    print('dfs cost:', end1 - end, 's, update+dfs cost:', end1 - start, 's')
    balance = getBalance(startToken['address'], config['address'])
    print('balance:', balance)
    trade = trades[0]
    if trade and int(trade['profit'])/pow(10, startToken['decimal']) >= minProfit:
        print(trade)
        tx = doTrade(balance, trade)
        print('tx:', tx)

if __name__ == "__main__":
    while 1:
        try:
            main()
        except Exception as e:
            print('exception:', e)
            raise
