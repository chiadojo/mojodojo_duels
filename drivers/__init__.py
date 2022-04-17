import json

from blspy import G1Element
from chia.cmds.units import units
from chia.util.bech32m import decode_puzzle_hash
from time import sleep
from drivers.mojo_dojo_drivers import player1_create, player1_check_for_accept, player2_spend, \
    player1_submit_preimage, player1_cancel, player2_forfeit
import hashlib

# Creates a MojoDojo Duel
# Used to create a new smart coin, confirming to the MojoDojo duel architecture.
# payout_address    : The string value of the TXCH payout address to be used. e.g "txch1d31.."
# random            : The random entropy to be used, e.g "hello123"
# wager             : The integer wager in XCH to be committed to the smart coin, e.g 0.1
# fee               : The transactional network fee to be used, default for testnet = 1000000000
from drivers.security import Security


def create_duel(pk: G1Element, payout_address: str, random: str, wager: int, fee=1000000000) -> str:
    wager = int(units['chia'] * wager)
    address = decode_puzzle_hash(payout_address).hex()
    preimage = hashlib.sha256(random.encode())
    print(f"Generated preimage: {preimage.hexdigest()}")
    hashed_preimage = hashlib.sha256(preimage.digest()).hexdigest()
    print("Creating spend transaction...")
    if fee < 10000000:
        print("Fee too low :(")
    ret = player1_create(pk, address, hashed_preimage, wager, fee)
    print("Successfully created coin, printing JSON:")
    print(ret)
    return ret


def cancel_duel(json_dict: dict, s: Security):
    player1_cancel(json_dict, s)


def accept_duel(json_dict: dict, s: Security, payout_address: str, random: str):
    address = decode_puzzle_hash(payout_address).hex()
    preimage = hashlib.sha256(random.encode()).hexdigest()
    print(f"Generated preimage: {preimage}")
    player2_spend(json_dict, s, address, preimage)


def finalise_duel(random: str, json_data: dict):
    preimage = hashlib.sha256(random.encode()).hexdigest()
    ret = player1_submit_preimage(preimage, json_data)
    while ret is None:
        sleep(5)
        ret = player1_submit_preimage(preimage, json_data)
    return ret


def forfeit_duel(json_data: dict):
    ret = player2_forfeit(json_data)
    while ret is None:
        sleep(5)
        ret = player2_forfeit(json_data)
    return ret


