import asyncio
import json

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
from chia.cmds.wallet_funcs import get_wallet


config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
self_hostname = config["self_hostname"]
full_node_rpc_port = config["full_node"]["rpc_port"]
wallet_rpc_port = config["wallet"]["rpc_port"]


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


def get_coin(coin_id: bytes32):
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


async def async_get_signed_tx(puzzlehash: bytes32, amount: uint64, fee: int):
    # wallet_id = "1"
    try:
        wallet_client = await WalletRpcClient.create(
            self_hostname, uint16(wallet_rpc_port), DEFAULT_ROOT_PATH, config
        )
        tx = await wallet_client.create_signed_transaction([{"puzzle_hash": puzzlehash, "amount": amount}], fee=fee)
        return tx
    finally:
        wallet_client.close()
        await wallet_client.await_closed()

def get_signed_tx(puzzlehash: bytes32, amount: uint64, fee: int):
    return asyncio.run(async_get_signed_tx(puzzlehash, amount, fee))

async def async_get_child(coin_id: bytes32) -> Coin:
    try:
        full_node_client = await FullNodeRpcClient.create(
            self_hostname, uint16(full_node_rpc_port), DEFAULT_ROOT_PATH, config
        )
        coin_record = await full_node_client.get_coin_records_by_parent_ids([coin_id])
        print(type(coin_record))
        print(coin_record)
        return coin_record
    finally:
        full_node_client.close()
        await full_node_client.await_closed()

def get_children(coin_id: bytes32) -> Coin:
    return asyncio.run(async_get_child(coin_id))

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


async def send_money_async(amount, address, fee=0):
    wallet_id = "1"
    try:
        wallet_client = await WalletRpcClient.create(
            self_hostname, uint16(wallet_rpc_port), DEFAULT_ROOT_PATH, config
        )
        res = await wallet_client.send_transaction(wallet_id, amount, address, fee)
        tx_id = res.name
        tx: TransactionRecord = await wallet_client.get_transaction(wallet_id, tx_id)
        print("Initial SpendBundle")
        print(tx.spend_bundle)
        while not tx.confirmed:
            await asyncio.sleep(5)
            tx = await wallet_client.get_transaction(wallet_id, tx_id)
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
        wallet_client = await WalletRpcClient.create(
            self_hostname, uint16(wallet_rpc_port), DEFAULT_ROOT_PATH, config
        )
        status = await wallet_client.push_tx(spend_bundle)
        return status
    finally:
        wallet_client.close()
        await wallet_client.await_closed()


def push_tx(spend_bundle: SpendBundle):
    return asyncio.run(push_tx_async(spend_bundle))