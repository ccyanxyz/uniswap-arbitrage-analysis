import json
import requests
from decimal import Decimal
from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3 import WebsocketProvider
from uniswap.uniswap import UniswapV2Client
from uniswap.uniswap import UniswapV2Utils as utils
import threading
import random

config = json.load(open('config.json'))
network = config['network']
address = config['address']
privkey = config['privkey']
http_addr = config[network]['http']
wss_addr = config[network]['wss']
printer_addr = config['printer'][network]
printer_sushi_addr = config['printer_sushi']
printer_abi = json.load(open('abi/printer.json'))

uni = UniswapV2Client(address, privkey, http_addr)

w3 = Web3(HTTPProvider(http_addr, request_kwargs={'timeout': 6000}))
ws = Web3(WebsocketProvider(wss_addr))

pairABI = json.load(open('abi/IUniswapV2Pair.json'))['abi']
erc20abi = json.load(open('./abi/erc20.abi'))
printer = w3.eth.contract(address=printer_addr, abi=printer_abi)
printer_sushi = w3.eth.contract(address=printer_sushi_addr, abi=printer_abi)

usdc = config['usdc'][network]
ycrv = config['ycrv'][network]
weth = config['weth'][network]
usdt = config['usdt'][network]
dai = config['dai'][network]
yycrv = w3.toChecksumAddress("0x199ddb4bdf09f699d2cf9ca10212bd5e3b570ac2")

basicTokens = {
        'weth': {
            'address': weth,
            'symbol': 'WETH',
            'decimal': 18,
            },
        'usdt': {
                'address': usdt,
                'symbol': 'USDT',
                'decimal': 6,
                },
        'usdc': {
                'address': usdc,
                'symbol': 'USDC',
                'decimal': 6,
                },
        'dai': {
                'address': dai,
                'symbol': 'DAI',
                'decimal': 18,
                },
        }

# dfs params
maxHops = config['maxHops']
startToken = basicTokens[config['start']]
minProfit = config['minProfit']
def randSelect(allp, num=200):
    maxNum = len(allp)
    start = random.randint(0, maxNum-num)
    return allp[start:start+num]

def randSelect1(allp, num=200):
    p = []
    maxNum = len(allp)
    # start = random.randint(0, maxNum-num)
    # end = random.randint(start, maxNum)
    jump = int(len(allp)/10)
    t = int(num/10)
    start = 0
    while start < maxNum:
        rand = random.randint(start, start+jump)
        if rand >= maxNum:
            break
        p += allp[rand:rand+t]
        start += jump
    return p
def removeBlackList(pairs):
    blacklist = json.load(open('files/blacklist.json'))
    r = []
    for i in range(len(pairs)):
        if pairs[i]['token0']['address'].lower() in blacklist or pairs[i]['token1']['address'].lower() in blacklist:
            r.append(i)
    r.reverse()
    for t in r:
        del pairs[t]
    return pairs
def toDict(pairs):
    p = {}
    i = 0
    for pair in pairs:
        p[pair['address']] = pair
        p[pair['address']]['arrIndex'] = i
        i += 1
    return p
def selectPairs(all_pairs):
    if config['pairs'] == 'random':
        pairs = randSelect(all_pairs, config['pair_num'])
    elif config['pairs'] == 'main_pairs':
        pairs = json.load(open('files/main_pairs.json'))
    pairs = removeBlackList(pairs)
    # pairs = removeLowLiq(pairs)
    pairsDict = toDict(pairs)
    return pairs, pairsDict

# gas
def gasnow():
    ret = requests.get(config['gasnow'])
    return ret.json()['data']

def getBalance(tokenAddress, address):
    c = w3.eth.contract(address=tokenAddress, abi=erc20abi)
    return c.functions.balanceOf(address).call()

def approve(tokenAddr, contractAddr, myAddr, amount, gasPrice):
    erc20Token = w3.eth.contract(address=tokenAddr, abi=erc20abi)
    approved_amount = erc20Token.functions.allowance(myAddr, contractAddr).call()
    if approved_amount >= amount:
        return True
    try:
        tx = erc20Token.functions.approve(contractAddr, 2**256-1).buildTransaction({
            'from': myAddr,
            'value': 0,
            'gasPrice': gasPrice,
            'gas': 1500000,
            "nonce": w3.eth.getTransactionCount(myAddr),
            })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=privkey)
        txhash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print('approving... ', txhash.hex())
        w3.eth.waitForTransactionReceipt(txhash.hex(), timeout=6000)
    except Exception as e:
        print('exception:', e)
        return False
    return True

# update reserves
def updateResJob(pairs, start, end):
    while start < end:
        reserves = uni.get_reserves(pairs[start]['address'])
        pairs[start]['reserve0'] = reserves[0]
        pairs[start]['reserve1'] = reserves[1]
        start += 1
def updateReservesMT(pairs):
    if len(pairs) < 10:
        updateResJob(pairs, 0, len(pairs))
    else:
        start = 0
        threads = []
        while start < len(pairs):
            end = start + 50
            if end > len(pairs):
                end = len(pairs)
            t = threading.Thread(target=updateResJob, args=(pairs, start, end))
            t.start()
            threads.append(t)
            start = end
        for t in threads:
            t.join()

d997 = Decimal(997)
d1000 = Decimal(1000)
def getOptimalAmount(Ea, Eb):
    if Ea > Eb:
        return None
    if not isinstance(Ea, Decimal):
        Ea = Decimal(Ea)
    if not isinstance(Eb, Decimal):
        Eb = Decimal(Eb)
    return Decimal(int((Decimal.sqrt(Ea*Eb*d997*d1000)-Ea*d1000)/d997))

def adjustReserve(token, amount):
    # res = Decimal(amount)*Decimal(pow(10, 18-token['decimal']))
    # return Decimal(int(res))
    return amount

def toInt(n):
    return Decimal(int(n))

def getEaEb(tokenIn, pairs):
    Ea = None
    Eb = None
    idx = 0
    tokenOut = tokenIn.copy()
    for pair in pairs:
        if idx == 0:
            if tokenIn['address'] == pair['token0']['address']:
                tokenOut = pair['token1']
            else:
                tokenOut = pair['token0']
        if idx == 1:
            Ra = adjustReserve(pairs[0]['token0'], pairs[0]['reserve0'])
            Rb = adjustReserve(pairs[0]['token1'], pairs[0]['reserve1'])
            if tokenIn['address'] == pairs[0]['token1']['address']:
                temp = Ra
                Ra = Rb
                Rb = temp
            Rb1 = adjustReserve(pair['token0'], pair['reserve0'])
            Rc = adjustReserve(pair['token1'], pair['reserve1'])
            if tokenOut['address'] == pair['token1']['address']:
                temp = Rb1
                Rb1 = Rc
                Rc = temp
                tokenOut = pair['token0']
            else:
                tokenOut = pair['token1']
            Ea = toInt(d1000*Ra*Rb1/(d1000*Rb1+d997*Rb))
            Eb = toInt(d997*Rb*Rc/(d1000*Rb1+d997*Rb))
        if idx > 1:
            Ra = Ea
            Rb = Eb
            Rb1 = adjustReserve(pair['token0'], pair['reserve0'])
            Rc = adjustReserve(pair['token1'], pair['reserve1'])
            if tokenOut['address'] == pair['token1']['address']:
                temp = Rb1
                Rb1 = Rc
                Rc = temp
                tokenOut = pair['token0']
            else:
                tokenOut = pair['token1']
            Ea = toInt(d1000*Ra*Rb1/(d1000*Rb1+d997*Rb))
            Eb = toInt(d997*Rb*Rc/(d1000*Rb1+d997*Rb))
        idx += 1
    return Ea, Eb

def getAmountOutByPath(tokenIn, amountIn, pairs):
    amountOut = amountIn
    tokenOut = tokenIn
    for pair in pairs:
        if pair['token0']['address'] == tokenOut['address']:
            tokenOut = pair['token1']
            amountOut = getAmountOut(amountOut, pair['reserve0'], pair['reserve1'])
        elif pair['token1']['address'] == tokenOut['address']:
            tokenOut = pair['token0']
            amountOut = getAmountOut(amountOut, pair['reserve1'], pair['reserve0'])
    return amountOut

def getAmountOut(amountIn, reserveIn, reserveOut):
    assert amountIn > 0
    assert reserveIn > 0 and reserveOut > 0
    if not isinstance(amountIn, Decimal):
        amountIn = Decimal(amountIn)
    if not isinstance(reserveIn, Decimal):
        reserveIn = Decimal(reserveIn)
    if not isinstance(reserveOut, Decimal):
        reserveOut = Decimal(reserveOut)
    return d997*amountIn*reserveOut/(d1000*reserveIn+d997*amountIn)

def updateReserves(pairs):
    for pair in pairs:
        reserves = uni.get_reserves(pair['address'])
        pair['reserve0'] = reserves[0]
        pair['reserve1'] = reserves[1]
    return pairs

def getAllPairs(pair_file, problem_file, token_file):
    num = uni.get_num_pairs()
    print(num)
    problems = json.load(open(problem_file))
    pairs = json.load(open(pair_file))
    tokens = json.load(open(token_file))
    start = 0
    if len(pairs) > 0:
        start = pairs[-1]['index'] + 1
    for i in range(start, num):
        addr = uni.get_pair_by_index(i)
        try:
            token0 = uni.get_token_0(addr)
            token1 = uni.get_token_1(addr)
            print(token0, token1)
            if token0 in tokens.keys():
                symbol0 = tokens[token0]['symbol']
                decimal0 = tokens[token0]['decimal']
            else:
                erc20 = w3.eth.contract(address=token0, abi=erc20abi)
                symbol0 = erc20.functions.symbol().call()
                decimal0 = erc20.functions.decimals().call()
            if token1 in tokens.keys():
                symbol1 = tokens[token1]['symbol']
                decimal1 = tokens[token1]['decimal']
            else:
                erc20 = w3.eth.contract(address=token1, abi=erc20abi)
                symbol1 = erc20.functions.symbol().call() 
                decimal1 = erc20.functions.decimals().call()
            reserves = uni.get_reserves(addr)
        except Exception as e:
            print(e)
            problems.append(addr)
            json.dump(problems, open(problem_file, 'w'))
            continue
        pair = {
                'index': i,
                'address': addr,
                'token0': {
                    'address': token0,
                    'symbol': symbol0,
                    'decimal': decimal0,
                    },
                'token1': {
                    'address': token1,
                    'symbol': symbol1,
                    'decimal': decimal1,
                    },
                'reserve0': reserves[0],
                'reserve1': reserves[1],
                }
        print(i, '/', num, pair)
        pairs.append(pair)
        if i % 5 == 0:
            json.dump(pairs, open(pair_file, 'w'))
    json.dump(pairs, open(pair_file, 'w'))

def getPairs(symbol='USDC', thresh = 500):
    pairs = json.load(open('files/pairs.json'))
    ret = []
    for pair in pairs:
        if pair['token0']['symbol'] == symbol:
            if pair['reserve0'] / pow(10, pair['token0']['decimal']) >= thresh:
                ret.append(pair)
        if pair['token1']['symbol'] == symbol:
            if pair['reserve1'] / pow(10, pair['token1'][decimal]) >= thresh:
                ret.append(pair)
    print('count:', len(ret))
    json.dump(ret, open('files/'+symbol+'_pairs.json', 'w'))
