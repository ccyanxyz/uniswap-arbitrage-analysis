import time
import json
import os

import unittest

from web3 import Web3

from uniswap.uniswap import UniswapV2Client, UniswapV2Utils


class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = Web3.toChecksumAddress("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
        cls.link_token = Web3.toChecksumAddress("0x20fe562d797a42dcb3399062ae9546cd06f63280")
        cls.weth_token = Web3.toChecksumAddress("0xc778417E063141139Fce010982780140Aa0cD5Ab")
        cls.link_weth_pair = Web3.toChecksumAddress("0x98A608D3f29EebB496815901fcFe8eCcC32bE54a")

        with open(os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/config.json")) as f:
            raw_json = json.load(f)

        cls.address = Web3.toChecksumAddress(raw_json["account"]["address"])
        cls.private_key = raw_json["account"]["private-key"]
        cls.provider = raw_json["provider"]

        cls.token_0 = raw_json["tokens"][0]  # Token A for the ERC20-ERC20 pair
        cls.token_1 = raw_json["tokens"][1]  # Token B for the ERC20-ERC20 pair
        cls.token_2 = raw_json["tokens"][2]  # Token for the ERC20-WETH pair

        uniswap = UniswapV2Client(cls.address, cls.private_key, provider=cls.provider)

        # create a pair for token_0/token_1 if not already created
        cls.token_pair = uniswap.get_pair(cls.token_0["address"], cls.token_1["address"])
        if cls.token_pair == "0x0000000000000000000000000000000000000000":
            print("Creating ERC20-ERC20 pair...")
            token_tx = uniswap.add_liquidity(
                token_a=cls.token_0["address"],
                token_b=cls.token_1["address"],
                amount_a=int(cls.token_0["supply"] * 10 ** -1),                   # 1/10 of the total supply of A
                amount_b=int(cls.token_1["supply"] * 10 ** -1),                   # 1/10 of the total supply of B
                min_a=int(cls.token_1["supply"] / cls.token_0["supply"] * 1.01),  # allow 1% slippage on B/A
                min_b=int(cls.token_0["supply"] / cls.token_1["supply"] * 1.01),  # allow 1% slippage on B/A
                to=cls.address,
                deadline=int(time.time() + 10 ** 3))
            uniswap.conn.eth.waitForTransactionReceipt(token_tx, timeout=2000)
            cls.token_pair = uniswap.get_pair(cls.token_0["address"], cls.token_1["address"])

        # create a pair for token_2/weth if not already created
        cls.weth_pair = uniswap.get_pair(cls.token_2["address"], uniswap.get_weth_address())
        if cls.weth_pair == "0x0000000000000000000000000000000000000000":
            print("Creating ERC20-WETH pair...")
            weth_tx = uniswap.add_liquidity_eth(
                token=cls.token_2["address"],
                amount_token=int(cls.token_2["supply"] * 10 ** -1),  # 1/10 of the total supply of the token
                amount_eth=100,                                      # 100 wei
                min_token=int(1000 / cls.token_2["supply"] * 1.01),  # allow 1% slippage on B/A
                min_eth=int(cls.token_2["supply"] / 1000 * 1.01),    # allow 1% slippage on B/A
                to=cls.address,
                deadline=int(time.time() + 10 ** 3))
            uniswap.conn.eth.waitForTransactionReceipt(weth_tx, timeout=2000)
            cls.weth_pair = uniswap.get_pair(cls.token_2["address"], uniswap.get_weth_address())


class UniswapV2ClientTest(BaseTest):
    def setUp(self):
        self.uniswap = UniswapV2Client(self.address, self.private_key, self.provider)

    def test_get_pair(self):
        pair = self.uniswap.get_pair(self.token_0["address"], self.token_1["address"])
        self.assertEqual(pair, self.token_pair)

    def test_get_pair_swapped_order(self):
        pair = self.uniswap.get_pair(self.token_1["address"], self.token_0["address"])
        self.assertEqual(pair, self.token_pair)

    def test_get_pair_not_found(self):
        rand_token = Web3.toChecksumAddress("0xAE14A3B9F6B333BfF64bEAe1C70a93c0781D6A3F")
        pair = self.uniswap.get_pair(self.token_0["address"], rand_token)
        self.assertEqual(pair, "0x0000000000000000000000000000000000000000")

    def test_get_num_pairs(self):
        num_pairs = self.uniswap.get_num_pairs()
        self.assertGreaterEqual(num_pairs, 50)

    def test_get_pair_by_index(self):
        pair = self.uniswap.get_pair_by_index(51)
        self.assertEqual(pair, self.token_pair)

    def test_get_pair_by_index_not_found(self):
        pair = self.uniswap.get_pair_by_index(9999)
        self.assertEqual(pair, "0x0000000000000000000000000000000000000000")

    def test_get_fee(self):
        fee = self.uniswap.get_fee()
        self.assertEqual(fee, "0x0000000000000000000000000000000000000000")

    def test_get_fee_setter(self):
        fee_setter = self.uniswap.get_fee()
        self.assertEqual(fee_setter, "0x0000000000000000000000000000000000000000")

    def test_get_weth_address(self):
        address = self.uniswap.get_weth_address()
        self.assertEqual(address, self.weth_token)

    def test_add_liquidity(self):
        amount_a = int(self.token_0["supply"] * 10 ** -3)  # 1/1000 of the total supply of A
        amount_b = int(self.token_1["supply"] * 10 ** -3)  # 1/1000 of the total supply of B
        min_a = 0  # int((amount_b / amount_a) * 1.01)  # allow 1% slippage on B/A
        min_b = 0  # int((amount_a / amount_b) * 1.01)  # allow 1% slippage on A/B
        deadline = int(time.time()) + 1000

        tx = self.uniswap.add_liquidity(
            self.token_0["address"], self.token_1["address"], amount_a, amount_b, min_a, min_b, self.address, deadline)
        receipt = self.uniswap.conn.eth.waitForTransactionReceipt(tx, timeout=2000)

        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["status"])

    def test_add_liquidity_eth(self):
        token = self.token_2["address"]
        amount_token = int(self.token_2["supply"] * 10 ** -3)  # 1/1000 of the total supply of the token
        amount_eth = 1  # 1 wei
        deadline = int(time.time()) + 1000

        tx = self.uniswap.add_liquidity_eth(
            token, amount_token, amount_eth, min_token=0, min_eth=0, to=self.address, deadline=deadline)
        receipt = self.uniswap.conn.eth.waitForTransactionReceipt(tx, timeout=2000)

        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["status"])

    # FIXME add way to retrieve current liquidity balance for a par
    """def test_remove_liquidity(self):
        tx = self.uniswap.remove_liquidity(
            token_a=self.token_0["address"],
            token_b=self.token_1["address"],
            liquidity=100,
            min_a=0,
            min_b=0,
            to=self.address,
            deadline=int(time.time()) + 1000
        )
        receipt = self.uniswap.conn.eth.waitForTransactionReceipt(tx, timeout=2000)

        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["status"])

    def test_remove_liquidity_eth(self):
        token = Web3.toChecksumAddress("0x20fe562d797a42dcb3399062ae9546cd06f63280")
        liquidity = 1 * 10 ** 15
        min_token = 1 * 10 ** 15
        min_eth = 2 * 10 ** 13
        deadline = int(time.time()) + 1000

        tx = self.uniswap.remove_liquidity_eth(
            token=self.token_2["address"],
            liquidity=1,
            min_token=0,
            min_eth=0,
            to=self.address,
            deadline=int(time.time()) + 1000
        )
        receipt = self.uniswap.conn.eth.waitForTransactionReceipt(tx, timeout=2000)

        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["status"])"""

    def test_remove_liquidity_with_permit(self):
        pass  # TODO

    def test_remove_liquidity_eth_with_permit(self):
        pass  # TODO

    def test_swap_exact_tokens_for_tokens(self):
        amount = int(self.token_0["supply"] * 10 ** -3)
        min_out = int(self.token_1["supply"] * 10 ** -5)
        path = [self.token_0["address"], self.token_1["address"]]
        deadline = int(time.time()) + 1000

        tx = self.uniswap.swap_exact_tokens_for_tokens(amount, min_out, path, to=self.address, deadline=deadline)
        receipt = self.uniswap.conn.eth.waitForTransactionReceipt(tx, timeout=2000)

        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["status"])

    def test_swap_tokens_for_exact_tokens(self):
        amount_out = int(self.token_1["supply"] * 10 ** -5)
        amount_in_max = int(self.token_0["supply"] * 10 ** -3)
        path = [self.token_0["address"], self.token_1["address"]]
        deadline = int(time.time()) + 1000

        tx = self.uniswap.swap_tokens_for_exact_tokens(amount_out, amount_in_max, path, self.address, deadline)
        receipt = self.uniswap.conn.eth.waitForTransactionReceipt(tx, timeout=2000)

        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["status"])

    def test_swap_exact_eth_for_tokens(self):
        amount = 10  # 10 wei
        min_out = int(self.token_2["supply"] * 10 ** -5)
        path = [self.uniswap.get_weth_address(), self.token_2["address"]]
        deadline = int(time.time()) + 1000

        tx = self.uniswap.swap_exact_eth_for_tokens(amount, min_out, path, self.address, deadline)
        receipt = self.uniswap.conn.eth.waitForTransactionReceipt(tx, timeout=2000)

        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["status"])

    def test_swap_tokens_for_exact_eth(self):
        amount_out = 1  # 1 wei
        amount_in_max = int(self.token_2["supply"] * 10 ** -3)
        path = [self.token_2["address"], self.uniswap.get_weth_address()]
        deadline = int(time.time()) + 1000

        tx = self.uniswap.swap_tokens_for_exact_eth(amount_out, amount_in_max, path, self.address, deadline)
        receipt = self.uniswap.conn.eth.waitForTransactionReceipt(tx, timeout=2000)

        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["status"])

    def test_swap_exact_tokens_for_eth(self):
        amount = int(self.token_2["supply"] * 10 ** -3)
        min_out = 1  # 1 wei
        path = [self.token_2["address"], self.uniswap.get_weth_address()]
        deadline = int(time.time()) + 1000
        tx = self.uniswap.swap_exact_tokens_for_eth(amount, min_out, path, self.address, deadline)
        receipt = self.uniswap.conn.eth.waitForTransactionReceipt(tx, timeout=2000)

        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["status"])

    def test_swap_eth_for_exact_tokens(self):
        amount_out = int(self.token_2["supply"] * 10 ** -5)
        amount = 100  # 100 wei
        path = [self.uniswap.get_weth_address(), self.token_2["address"]]
        deadline = int(time.time()) + 1000

        tx = self.uniswap.swap_eth_for_exact_tokens(amount_out, amount, path, self.address, deadline)
        receipt = self.uniswap.conn.eth.waitForTransactionReceipt(tx, timeout=2000)

        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["status"])


class UniswapV2UtilsTest(BaseTest):
    def setup(self):
        self.w3 = Web3(Web3.HTTPProvider(self.provider, request_kwargs={"timeout": 60}))

    def test_sort_tokens_1(self):
        token_0, token_1 = UniswapV2Utils.sort_tokens(self.link_token, self.weth_token)
        self.assertEqual(token_0, self.link_token)
        self.assertEqual(token_1, self.weth_token)

    def test_sort_tokens_2(self):
        token_0, token_1 = UniswapV2Utils.sort_tokens(self.weth_token, self.link_token)
        self.assertEqual(token_0, self.link_token)
        self.assertEqual(token_1, self.weth_token)

    def test_sort_tokens_equal(self):
        with self.assertRaises(AssertionError):
            UniswapV2Utils.sort_tokens(self.link_token, self.link_token)

    def test_sort_tokens_zero(self):
        with self.assertRaises(AssertionError):
            UniswapV2Utils.sort_tokens(Web3.toHex(0x0), self.link_token)

    def test_pair_for_1(self):
        pair = UniswapV2Utils.pair_for(self.factory, self.link_token, self.weth_token)
        self.assertEqual(pair, self.link_weth_pair)

    def test_pair_for_2(self):
        pair = UniswapV2Utils.pair_for(self.factory, self.weth_token, self.link_token)
        self.assertEqual(pair, self.link_weth_pair)

    def test_get_reserves(self):
        pass  # TODO

    def calculate_quote(self):
        pass  # TODO

    def test_get_amount_out(self):
        pass  # TODO

    def test_get_amount_in(self):
        pass  # TODO

    def test_get_amounts_out(self):
        pass  # TODO

    def test_get_amounts_in(self):
        pass  # TODO
