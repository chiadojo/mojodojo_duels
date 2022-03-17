# config/config.yaml
import asyncio
import json
import time

from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_spend import CoinSpend
from chia.types.spend_bundle import SpendBundle
from chia.util.bech32m import encode_puzzle_hash, decode_puzzle_hash
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16, uint64, uint32
from chia.wallet.transaction_record import TransactionRecord

config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
self_hostname = config["self_hostname"]  # localhost
full_node_rpc_port = config["full_node"]["rpc_port"]  # 8555
wallet_rpc_port = config["wallet"]["rpc_port"]  # 9256


async def get_coin_async(coin_id: bytes32):
    try:
        full_node_client = await FullNodeRpcClient.create(
            self_hostname, uint16(full_node_rpc_port), DEFAULT_ROOT_PATH, config
        )
        coin_record = await full_node_client.get_coin_record_by_name(coin_id)
        return coin_record
    finally:
        full_node_client.close()
        await full_node_client.await_closed()


def get_coin(coin_id: str):
    return asyncio.run(get_coin_async(coin_id))

async def get_coin_solution_async(coin_id: bytes32, block_height: uint32) -> str:
    try:
        full_node_client = await FullNodeRpcClient.create(
            self_hostname, uint16(full_node_rpc_port), DEFAULT_ROOT_PATH, config
        )
        data = await full_node_client.get_puzzle_and_solution(coin_id, block_height)
        return data
    finally:
        full_node_client.close()
        await full_node_client.await_closed()

def get_coin_solution(coin_id: bytes32, block_height: uint32) -> CoinSpend:
    return asyncio.run(get_coin_solution_async(coin_id, block_height))

async def get_transaction_async(tx_id: bytes32):
    wallet_id = "1"
    try:
        wallet_client = await WalletRpcClient.create(
            self_hostname, uint16(wallet_rpc_port), DEFAULT_ROOT_PATH, config
        )
        tx = await wallet_client.get_transaction(wallet_id, tx_id)
        return tx
    finally:
        wallet_client.close()
        await wallet_client.await_closed()


def get_transaction(tx_id: bytes32):
    return asyncio.run(get_transaction_async(tx_id))

# async def get_coin_info_async(coin : Coin):
#     try:
#         full_node_client = await FullNodeRpcClient.create(
#             self_hostname, uint16(full_node_rpc_port), DEFAULT_ROOT_PATH, config
#         )
#         coin_record = await full_node_client.get_coin_record_by_name(bytes32.fromhex(coin.get_hash()))
#         return coin_record.
#
#     finally:
#         full_node_client.close()
#         await full_node_client.await_closed()
#
# def get_coin_info

async def send_money_async(amount, address, fee=0):
    wallet_id = "1"
    try:
        wallet_client = await WalletRpcClient.create(
            self_hostname, uint16(wallet_rpc_port), DEFAULT_ROOT_PATH, config
        )
        res = await wallet_client.send_transaction(wallet_id, amount, address, fee)
        tx_id = res.name
        # print(f"waiting until transaction {tx_id} is confirmed...")
        tx: TransactionRecord = await wallet_client.get_transaction(wallet_id, tx_id)
        while (not tx.confirmed):
            await asyncio.sleep(5)
            tx = await wallet_client.get_transaction(wallet_id, tx_id)
            # print(".", end='', flush=True)
        puzzle_hash = decode_puzzle_hash(address)
        coin = next((c for c in tx.additions if c.puzzle_hash == puzzle_hash), None)
        return coin

    finally:
        wallet_client.close()
        await wallet_client.await_closed()


def send_money(amount, address, fee=0):
    return asyncio.run(send_money_async(amount, address, fee))


def deploy_smart_coin(puzzlehash: bytes32, amount: uint64, fee=0):
    address = encode_puzzle_hash(puzzlehash, "txch")
    coin = send_money(amount, address, fee)
    return coin


async def push_tx_async(spend_bundle: SpendBundle):
    try:
        full_node_client = await FullNodeRpcClient.create(
            self_hostname, uint16(full_node_rpc_port), DEFAULT_ROOT_PATH, config
        )
        status = await full_node_client.push_tx(spend_bundle)
        return status
    finally:
        full_node_client.close()
        await full_node_client.await_closed()


def push_tx(spend_bundle: SpendBundle):
    return asyncio.run(push_tx_async(spend_bundle))


def print_json(dict):
    print(json.dumps(dict, sort_keys=True, indent=4))
