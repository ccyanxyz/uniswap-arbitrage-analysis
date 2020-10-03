from common import *
from dfs import *
import json

def getPair(tokenA, tokenB, symbolA, symbolB):
    addr = uni.get_pair(tokenA, tokenB)
    res = uni.get_reserves(addr)
    token0 = tokenA
    symbol0 = symbolA
    decimal0 = 18
    token1 = tokenB
    symbol1 = symbolB
    decimal1 = 18
    if token0.lower() > token1.lower():
        token0 = tokenB
        symbol0 = symbolB
        if symbol0 == "USDC":
            decimal0 = 6
        token1 = tokenA
        symbol1 = symbolA
        if symbol1 == "USDC":
            decimal1 = 6
    pair = { 
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
            'reserve0': res[0],
            'reserve1': res[1],
            }
    print(pair)
    return pair

yycrv = w3.toChecksumAddress("0x199ddb4bdf09f699d2cf9ca10212bd5e3b570ac2")
usdc = w3.toChecksumAddress("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
ycrv = w3.toChecksumAddress("0xdf5e0e81dff6faf3a7e52ba697820c5e32d806a8")
weth = w3.toChecksumAddress("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
usdt = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

def calcAmountOut(tokenIn, amountIn, pairs):
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

def calcEaEb(pairs):
    Ea = None
    Eb = None
    idx = 0
    for pair in pairs:
        if idx == 1:
            Ra = adjustReserve(pairs[0]['token0'], pairs[0]['reserve0'])
            Rb = adjustReserve(pairs[0]['token1'], pairs[0]['reserve1'])
            Rb1 = adjustReserve(pair['token0'], pair['reserve0'])
            Rc = adjustReserve(pair['token1'], pair['reserve1'])
            Ea = d1000*Ra*Rb1/(d1000*Rb1+d997*Rb)
            Eb = d997*Rb*Rc/(d1000*Rb1+d997*Rb)
        if idx > 1:
            Ra = Ea
            Rb = Eb
            Rb1 = adjustReserve(pair['token0'], pair['reserve0'])
            Rc = adjustReserve(pair['token1'], pair['reserve1'])
            Ea = d1000*Ra*Rb1/(d1000*Rb1+d997*Rb)
            Eb = d997*Rb*Rc/(d1000*Rb1+d997*Rb)
        idx += 1
    print(Ea, Eb)
    optimalAmount = getOptimalAmount(Ea, Eb)
    profit = getAmountOut(optimalAmount, Ea, Eb)-optimalAmount
    print('amount:', optimalAmount, 'out:', profit+optimalAmount, 'profit:', profit)
    amountOut = calcAmountOut(optimalAmount, pairs)
    print('amountOut:', amountOut)

pairs = json.load(open('files/pairs.json'))[:100]
# pairs = [
        # getPair(yycrv, usdc, 'YYCRV', 'USDC'),
        # getPair(ycrv, yycrv, 'YCRV', 'YYCRV'),
        # getPair(ycrv, weth, 'YCRV', 'WETH'),
        # getPair(usdc, weth, 'USDC', 'WETH'),
        # ]
# # pairs = [
        # {'address': '0x803BcEAD8cE5B5634204228D8f3419aC046426f1', 'token1': {'address': '0x199ddb4BDF09f699d2Cf9CA10212Bd5E3B570aC2', 'symbol': 'YYCRV', 'decimal': 18}, 'token0': {'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'symbol': 'USDC', 'decimal': 6}, 'reserve1': 1256181159389962060575, 'reserve0': 845273560},
# {'address': '0x4e29a332806AFa07DD2c593DdFbAb3AB2E11664b', 'token0': {'address': '0x199ddb4BDF09f699d2Cf9CA10212Bd5E3B570aC2', 'symbol': 'YYCRV', 'decimal': 18}, 'token1': {'address': '0xdF5e0e81Dff6FAF3A7e52BA697820c5e32D806A8', 'symbol': 'YCRV', 'decimal': 18}, 'reserve0': 345545396859430951414, 'reserve1': 237803864062936128103},
# {'address': '0x55dF969467EBdf954FE33470ED9c3C0F8Fab0816', 'token1': {'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'symbol': 'WETH', 'decimal': 18}, 'token0': {'address': '0xdF5e0e81Dff6FAF3A7e52BA697820c5e32D806A8', 'symbol': 'YCRV', 'decimal': 18}, 'reserve1': 458989204630578316845, 'reserve0': 146347861464099611444006},
# {'address': '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc', 'token1': {'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'symbol': 'USDC', 'decimal': 6}, 'token0': {'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'symbol': 'WETH', 'decimal': 18}, 'reserve1': 177215126419196, 'reserve0': 525272035272173884843548},
        # ]
tokenIn = {
        'address': usdt,
        'symbol': 'USDT',
        'decimal': 6,
        }
tokenOut = {
        'address': usdt,
        'symbol': 'USDT',
        'decimal': 6,
        }
amountIn = 100*1e6
maxHops = 5
currentPairs = []
path = [tokenIn]
origToken = tokenIn
origAmount = amountIn
bestTrade = None

def testBestTradeExactIn():
    trade = findBestTradeExactIn(pairs, tokenIn, tokenOut, amountIn, maxHops, currentPairs, path, origToken, origAmount, bestTrade)
    print(trade)

def testFindArb():
    Ea = None
    Eb = None
    trade = findArb(pairs, tokenIn, tokenOut, maxHops, currentPairs, path, Ea, Eb, bestTrade)
    print(trade)
    amountOut = calcAmountOut(tokenIn, trade['optimalAmount'], trade['route'])
    print('amountOutByRoute:', amountOut, 'profit:', amountOut-trade['optimalAmount'])

if __name__ == '__main__':
    # testBestTradeExactIn()
    testFindArb()
    # calcEaEb(pairs)
