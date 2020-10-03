from common import *

'''
# path = [tokenIn]
def findBestTradeExactIn(pairs, tokenIn, tokenOut, amountIn, maxHops, currentPairs, path, origToken, origAmount, bestTrade):
    for i in range(len(pairs)):
        pair = pairs[i]
        if not pair['token0']['address'] == tokenIn['address'] and not pair['token1']['address'] == tokenIn['address']:
            continue
        if pair['reserve0'] == 0 or pair['reserve1'] == 0:
            continue
        if tokenIn['address'] == pair['token0']['address']:
            amountOut = getAmountOut(amountIn, pair['reserve0'], pair['reserve1'])
            tempOut = pair['token0']
        if tokenIn['address'] == pair['token1']['address']:
            amountOut = getAmountOut(amountIn, pair['reserve1'], pair['reserve0'])
            tempOut = pair['token1']
        path.append(tempOut)
        if tempOut == tokenOut:
            newTrade = { 'route': currentPairs + [pair], 'path': path, 'tokenIn': origToken, 'tokenOut': tokenOut, 'amountIn': origAmount, 'amountOut': amountOut }
            if not bestTrade:
                bestTrade = newTrade
            if bestTrade['amountOut'] < amountOut:
                bestTrade = newTrade
        elif maxHops > 1 and len(pairs) > 1:
            pairsExcludingThisPair = pairs[:i] + pairs[i+1:]
            findBestTradeExactIn(pairsExcludingThisPair, tempOut, tokenOut, amountOut, maxHops-1, currentPairs + [pair], path, origToken, origAmount, bestTrade)
        return bestTrade
'''

def sortTrades(trades, newTrade):
    trades.append(newTrade)
    return sorted(trades, key = lambda x: x['profit'])

# path = [tokenIn]
def findArb(pairs, tokenIn, tokenOut, maxHops, currentPairs, path, bestTrades, count=5):
    for i in range(len(pairs)):
        newPath = path.copy()
        pair = pairs[i]
        if not pair['token0']['address'] == tokenIn['address'] and not pair['token1']['address'] == tokenIn['address']:
            continue
        if pair['reserve0']/pow(10, pair['token0']['decimal']) < 1 or pair['reserve1']/pow(10, pair['token1']['decimal']) < 1:
            continue
        if tokenIn['address'] == pair['token0']['address']:
            tempOut = pair['token1']
        else:
            tempOut = pair['token0']
        newPath.append(tempOut)
        if tempOut['address'] == tokenOut['address'] and len(path) > 2:
            Ea, Eb = getEaEb(tokenOut, currentPairs + [pair])
            newTrade = { 'route': currentPairs + [pair], 'path': newPath, 'Ea': Ea, 'Eb': Eb }
            if Ea and Eb and Ea < Eb:
                newTrade['optimalAmount'] = getOptimalAmount(Ea, Eb)
                if newTrade['optimalAmount'] > 0:
                    newTrade['outputAmount'] = getAmountOut(newTrade['optimalAmount'], Ea, Eb)
                    newTrade['profit'] = newTrade['outputAmount']-newTrade['optimalAmount']
                    newTrade['p'] = int(newTrade['profit'])/pow(10, tokenOut['decimal'])
                else:
                    continue
                bestTrades = sortTrades(bestTrades, newTrade)
                bestTrades.reverse()
                bestTrades = bestTrades[:count]
        elif maxHops > 1 and len(pairs) > 1:
            pairsExcludingThisPair = pairs[:i] + pairs[i+1:]
            bestTrades = findArb(pairsExcludingThisPair, tempOut, tokenOut, maxHops-1, currentPairs + [pair], newPath, bestTrades, count)
    return bestTrades
