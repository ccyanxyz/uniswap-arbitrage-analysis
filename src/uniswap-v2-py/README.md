# UniswapV2 Python

[![Build Status](https://travis-ci.com/asynctomatic/uniswap-v2-py.svg?branch=master)](https://travis-ci.com/asynctomatic/uniswap-v2-py)
[![License](http://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/asynctomatic/uniswap-v2-py/master/LICENSE)

An unofficial Python wrapper for [Uniswap V2](https://uniswap.exchange/).

I am not affiliated with Uniswap, **use at your own risk**.

## Features
- Simplistic library capable of interacting with most contract functions and variables.
- Factory - query for information regarding existing pairs.
- Router - add/remove liquidity and perform swaps using either ETH or ERC20 tokens.


## Getting Started
This module presents a simplistic interface to Uniswap V2, however I highly recommend you to familiarize yourself
with the [official documentation](https://uniswap.org/docs/v2) before using ``uniswap-v2-py`` in order to unlock
its full potential and have a better understanding regarding what is actually going on behind the scenes.

### Installation:
The module can be installed via pip:
```
pip install uniswap-v2-py
# or
pip install git+git://github.com/asynctomatic/uniswap-v2-py.git
```

Alternatively you can clone this repository and install it manually:
```
git clone https://github.com/asynctomatic/uniswap-v2-py.git
cd uniswap-v2-py
python setup.py install
```

### Configuration
The client expects a web3 provider to be passed to it as an argument.
Alternatively you can set the ``PROVIDER`` environment variable with your provider of choice.
```
export PROVIDER=https://mainnet.infura.io/v3/<PROJECT_SECRET>
```

## Documentation

```python
from uniswap.uniswap import UniswapV2Client
client = UniswapV2Client(address, private_key)
```

```python
from uniswap.uniswap import UniswapV2Client

my_provider = "https://mainnet.infura.io/v3/<PROJECT_SECRET>"
client = UniswapV2Client(address, private_key, provider=my_provider)
```

#### Factory Read-Only Methods

[get_pair](https://uniswap.org/docs/v2/smart-contracts/factory/#getpair)
```python
token_a = "0x20fe562d797a42dcb3399062ae9546cd06f63280"
token_b = "0xc778417E063141139Fce010982780140Aa0cD5Ab"
pair = client.get_pair(token_a, token_b)
```
Returns the address of the pair for ``token_a`` and ``token_b``, if it has been created, else ``0x0000000000000000000000000000000000000000``.

[get_pair_by_index](https://uniswap.org/docs/v2/smart-contracts/factory/#allpairs)
```python
pair = client.get_pair_by_index(42)
```
Returns the address of the ``n``th pair (``0``-indexed) created through the factory, or ``0x0000000000000000000000000000000000000000`` if not enough pairs have been created yet.

[get_num_pairs](https://uniswap.org/docs/v2/smart-contracts/factory/#allpairslength)
```python
num_pairs = client.get_num_pairs()
```
Returns the total number of pairs created through the factory so far.

[get_fee](https://uniswap.org/docs/v2/smart-contracts/factory/#feeto)
```python
fee = client.get_fee()
```
Returns the protocol wide fee. See [Protocol Charge Calculation](https://uniswap.org/docs/v2/smart-contracts/architecture/#protocol-charge-calculation) for details.

[get_fee_setter](https://uniswap.org/docs/v2/smart-contracts/factory/#feetosetter)
```python
num_pairs = client.get_fee_setter()
```
Returns the address allowed to change the protocol fee.

#### Router Read-Only Methods

[get_factory](https://uniswap.org/docs/v2/smart-contracts/router/#factory)
```python
factory = client.get_factory()
```
Returns the factory address.

[get_weth_address](https://uniswap.org/docs/v2/smart-contracts/router/#weth)
```python
factory = client.get_weth_address()
```
Returns the [canonical WETH address](https://blog.0xproject.com/canonical-weth-a9aa7d0279dd)
on the Ethereum mainnet, or the Ropsten, Rinkeby, Görli, or Kovan testnets.

#### State-Changing Methods

[add_liquidity](https://uniswap.org/docs/v2/smart-contracts/router/#addliquidity)
```python
import time

token_a = "0x20fe562d797a42dcb3399062ae9546cd06f63280"
token_b = "0xc778417E063141139Fce010982780140Aa0cD5Ab"
amount_a = 1 * 10**18
amount_b = 2 * 10**17
min_a = int((amount_b / amount_a) * 1.01)  # allow 1% slippage on B/A
min_b = int((amount_a / amount_b) * 1.01)  # allow 1% slippage on A/B
deadline = int(time.time()) + 1000

tx = client.add_liquidity(token_a, token_b, amount_a, amount_b, min_a, min_b, address, deadline)
```
Adds liquidity to an ERC20-ERC20 pool.
- Always adds assets at the ideal ratio, according to the price when the transaction is executed.
- If a pool for the passed tokens does not exists, one is created automatically, and exactly ``amount_a``/``amount_b`` tokens are added.

[add_liquidity_eth](https://uniswap.org/docs/v2/smart-contracts/router/#addliquidityeth)
```python
import time

token = "0x20fe562d797a42dcb3399062ae9546cd06f63280"
amount_token = 1 * 10**18
amount_eth = 2 * 10**17
min_token = int((amount_eth / amount_token) * 1.01)  # allow 1% slippage on B/A
min_eth = int((amount_token / amount_eth) * 1.01)  # allow 1% slippage on A/B
deadline = int(time.time()) + 1000

tx = client.add_liquidity_eth(token, amount_token, amount_eth, min_token, min_eth, address, deadline)
```
Adds liquidity to an ERC20-WETH pool with ETH.
- Always adds assets at the ideal ratio, according to the price when the transaction is executed.
- The ``amount_eth`` is sent as ``msg.value``.
- Leftover ETH, if any, is returned to ``msg.sender``.
- If a pool for the passed token and WETH does not exists, one is created automatically,
and exactly ``amount_token``/``amount_eth`` tokens are added.

[remove_liquidity](https://uniswap.org/docs/v2/smart-contracts/router/#removeliquidity)
```python
liquidity = 1 * 10**16  # amount of liquidity tokens.
tx = client.remove_liquidity(token_a, token_b, liquidity, min_a, min_b, to, deadline)
```
Removes liquidity from an ERC20-ERC20 pool.

[remove_liquidity_eth](https://uniswap.org/docs/v2/smart-contracts/router/#removeliquidityeth)
```python
liquidity = 1 * 10**16  # amount of liquidity tokens.
tx = client.remove_liquidity(token, liquidity, min_token, min_eth, to, deadline)
```
Removes liquidity from an ERC-20-WETH pool and returns ETH.

[swap_exact_tokens_for_tokens](https://uniswap.org/docs/v2/smart-contracts/router/#swapexacttokensfortokens)
```python
amount_in = 1 * 10**17
min_amount_out = 1 * 10**15
path = [
    "0x20fe562d797a42dcb3399062ae9546cd06f63280",
    "0xc778417e063141139fce010982780140aa0cd5ab"
]

tx = client.swap_exact_tokens_for_tokens(amount_in, min_amount_out, path, to_address, deadline)
```
Swaps an exact amount of input tokens for as many output tokens as possible,
along the route determined by the path. The first element of path is the input token,
the last is the output token, and any intermediate elements represent intermediate pairs
to trade through (if, for example, a direct pair does not exist).

## Donate
If you found this library useful and want to support my work feel free to donate.

- BTC: 36wpJNSZ4mKHh526D5Zo7qsTvWk8eCkzru
- ETH: 0x1209cEc8CBBa5C67e8A3a154258FEaaCd99D5F20

## Disclaimer
I am not affiliated with the Uniswap team nor am I responsible for possible losses of funds resulting from
bugs or incorrect usage of this module, **use at your own risk**.
