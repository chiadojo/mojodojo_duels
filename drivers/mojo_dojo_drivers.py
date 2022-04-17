import hashlib
import json

from blspy import G2Element, G1Element
from cdv.util.load_clvm import load_clvm
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32, bytes4
from chia.types.coin_record import CoinRecord
from chia.types.coin_spend import CoinSpend
from chia.types.spend_bundle import SpendBundle
from chia.util.ints import uint64, uint32

from . import security
from .chia_utils import deploy_smart_coin, push_tx, get_coin, get_coin_solution
from .clvm_drivers import acceptance_modhash, initial_puzzle, match_puzzle, acceptance_puzzle, match_puzzle
from .security import Security


def player1_create(pk: G1Element, puzzlehash: str, hashed_preimage: str, amount: int, fee: int) -> str:
    coin: Coin = create_initial_coin(acceptance_modhash(),
                                     pk,
                                     bytes32.fromhex(puzzlehash),
                                     bytes32.fromhex(hashed_preimage),
                                     amount,
                                     uint64(fee))
    json_data = json.dumps({'coinid': coin.name().hex(),
                            'pubkey': bytes(pk).hex(),
                            'coin_parent': coin.parent_coin_info.hex(),
                            'coin_puzzlehash': coin.puzzle_hash.hex(),
                            'coin_amount': coin.amount,
                            'puzzlehash': puzzlehash,
                            'hashed_preimage': hashed_preimage,
                            'amount': amount,
                            'tx_fee': fee
                            })
    return json_data


def create_initial_coin(acceptance_modhash: bytes32,
                        pk: G1Element,
                        player1_puzzlehash: bytes32,
                        player1_hashed_preimage: bytes32,
                        amount: int,
                        fee: uint64
                        ) -> Coin:
    pzl = initial_puzzle(acceptance_modhash,
                         pk,
                         player1_puzzlehash,
                         player1_hashed_preimage,
                         amount)
    print(pzl)
    return deploy_smart_coin(pzl.get_tree_hash(), uint64(amount + (fee * 2)), fee)

def player1_cancel(coin_data: dict, s: Security):
    puzzle = initial_puzzle(acceptance_modhash(),
                            G1Element.from_bytes(bytes.fromhex(coin_data['pubkey'])),
                            bytes32.fromhex(coin_data['puzzlehash']),
                            bytes32.fromhex(coin_data['hashed_preimage']),
                            int(coin_data['amount'])
                            )
    solution = Program.to([0, 0, s.get_pk()])
    print("Creating spend for duel...")
    spend:CoinSpend = CoinSpend(
        coin=Coin(bytes32.fromhex(coin_data['coin_parent']),
                  bytes32.fromhex(coin_data['coin_puzzlehash']),
                  uint64(coin_data['coin_amount'])),
        puzzle_reveal=puzzle.to_serialized_program(),
        solution=solution.to_serialized_program()
    )
    signature = s.sign_coin_and_puzzlehash(
        bytes32.fromhex(coin_data['puzzlehash']),
        bytes32.fromhex(coin_data['coinid'])
    )
    spend_bundle: SpendBundle = SpendBundle([spend], signature)

    print(spend_bundle.to_json_dict())
    print(spend_bundle)
    print("Broadcasting spend to network...")
    print(push_tx(spend_bundle))


# Add security
# The best solution here is to unlock one of the standard transactions,
# & not to provide a new solution
# but then also create an output back to the same address, with total_amount - duel_amount
# as well as spending the initial coin

def player2_match_coin(pubkey: bytes32, puzzlehash: bytes32, preimage: bytes32, amount: int, fee: int):
    mp: Program = match_puzzle(
       pubkey,
       puzzlehash,
       preimage,
       amount
    )
    return mp, deploy_smart_coin(mp.get_tree_hash(), uint64(amount), uint64(fee))



def player2_spend(coin_data: dict, s: Security, puzzlehash, preimage):
    puzzle = initial_puzzle(acceptance_modhash(),
                            G1Element.from_bytes(bytes.fromhex(coin_data['pubkey'])),
                            bytes32.fromhex(coin_data['puzzlehash']),
                            bytes32.fromhex(coin_data['hashed_preimage']),
                            int(coin_data['amount'])
                            )
    solution = Program.to([bytes32.fromhex(puzzlehash), bytes32.fromhex(preimage), 0])
    print("Creating spend for duel...")
    spend:CoinSpend = CoinSpend(
        coin=Coin(bytes32.fromhex(coin_data['coin_parent']),
                  bytes32.fromhex(coin_data['coin_puzzlehash']),
                  uint64(coin_data['coin_amount'])),
        puzzle_reveal=puzzle.to_serialized_program(),
        solution=solution.to_serialized_program()
    )
    print("Creating matching wager contribution...")
    pubkey = s.get_pk()
    print(f"Fetched pk: {pubkey}")
    match_pzl, match_coin = player2_match_coin(
        pubkey,
        bytes32.fromhex(puzzlehash),
        bytes32.fromhex(preimage),
        coin_data['amount'],
        coin_data['tx_fee']
    )
    print("Created match coin:")
    print(match_coin)
    match_spend = CoinSpend(
        coin=match_coin,
        puzzle_reveal=match_pzl.to_serialized_program(),
        solution=Program.to([spend.coin.name()]).to_serialized_program()
    )
    signature = s.sign_coin_and_puzzlehash(
        hashlib.sha256(bytes32.fromhex(puzzlehash) + bytes32.fromhex(preimage) + spend.coin.name()).digest(),
        match_coin.name()
    )
    spend_bundle: SpendBundle = SpendBundle([spend, match_spend], signature)
    print(spend_bundle.to_json_dict())
    print(spend_bundle)
    print("Broadcasting spend to network...")
    print(push_tx(spend_bundle))


def player1_check_for_accept(coin_data: dict) -> CoinSpend:
    coin_record: CoinRecord = get_coin(bytes32.fromhex(coin_data['coinid']))
    if coin_record is None:
        return None
    if coin_record.spent_block_index == 0:
        return None
    coin_solution: CoinSpend = get_coin_solution(
        bytes32.fromhex(coin_data['coinid']),
        uint32(coin_record.spent_block_index)
    )
    if coin_solution is None:
        print("Found coin record without solution")
        return
    p = Program.from_serialized_program(coin_solution.solution)
    return {'puzzlehash': p.first().atom.hex(), 'preimage': p.rest().first().atom.hex()}


def player1_calculate_acceptance_coin(coin_data: dict, coin_solution: dict):
    puzzle = acceptance_puzzle(
        bytes32.fromhex(coin_data['puzzlehash']),
        bytes32.fromhex(coin_data['hashed_preimage']),
        coin_data['amount'],
        bytes32.fromhex(coin_solution['puzzlehash']),
        bytes32.fromhex(coin_solution['preimage']),
    )
    puzzlehash = puzzle.get_tree_hash()
    print(f"player1 calculated puzzlehash {puzzlehash}")
    print(f"Used coin value: {coin_data['amount'] + coin_data['tx_fee']}")
    targetCoin: Coin = Coin(parent_coin_info=bytes32.fromhex(coin_data['coinid']),
                            puzzle_hash=puzzlehash,
                            amount=coin_data['amount'] * 2 + coin_data['tx_fee'])
    return puzzle, targetCoin


# Changed FROM bytes32
def player1_submit_preimage(preimage: str, coin_data: dict):
    coin_solution = player1_check_for_accept(coin_data)
    print(f"Coin soln: {coin_solution}")
    if coin_solution is None:
        print("Error, coin hasn't been accepted yet.")
        return None
    puzzle, acceptance_coin = player1_calculate_acceptance_coin(coin_data, coin_solution)
    print(f"Coin has been accepted, response id: {acceptance_coin.name()}")
    spend = CoinSpend(
        coin=acceptance_coin,
        puzzle_reveal=puzzle,
        solution=Program.to([bytes32.fromhex(preimage)]).to_serialized_program()
    )
    spend_bundle: SpendBundle = SpendBundle([spend], G2Element())
    try:
        print(push_tx(spend_bundle))
        print("Submitted the preimage, new coin:")
        return spend_bundle.coin_spends[0]
    except Exception as e:
        print("Spend failed :(")
        print(e)


# Changed FROM bytes32
def player2_forfeit(coin_data: dict):
    coin_solution = player1_check_for_accept(coin_data)
    print(f"Coin soln: {coin_solution}")
    if coin_solution is None:
        print("Error, coin hasn't been accepted yet.")
        return None
    puzzle, acceptance_coin = player1_calculate_acceptance_coin(coin_data, coin_solution)
    print(f"Coin has been accepted, response id: {acceptance_coin.name()}")
    spend = CoinSpend(
        coin=acceptance_coin,
        puzzle_reveal=puzzle,
        solution=Program.to([0]).to_serialized_program()
    )
    spend_bundle: SpendBundle = SpendBundle([spend], G2Element())
    try:
        print(push_tx(spend_bundle))
        print("Submitted the preimage, new coin:")
        return spend_bundle.coin_spends[0]
    except Exception as e:
        print("Spend failed :(")
        print(e)


