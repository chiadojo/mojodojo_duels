import hashlib
import json

from blspy import G2Element
from cdv.util.load_clvm import load_clvm
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_record import CoinRecord
from chia.types.coin_spend import CoinSpend
from chia.types.spend_bundle import SpendBundle
from chia.util.ints import uint64, uint32

from .chia_utils import deploy_smart_coin, push_tx, get_coin, get_coin_solution
from .clvm_drivers import acceptance_modhash, initial_puzzle, match_puzzle, acceptance_puzzle, match_puzzle


def player1_create(puzzlehash: str, hashed_preimage: str, amount: int, fee: int) -> str:
    coin: Coin = create_initial_coin(acceptance_modhash(),
                                     bytes32.fromhex(puzzlehash),
                                     bytes32.fromhex(hashed_preimage),
                                     uint64(amount),
                                     uint64(fee))
    json_data = json.dumps({'coinid': coin.name().hex(),
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
                        player1_puzzlehash: bytes32,
                        player1_hashed_preimage: bytes32,
                        amount: uint64,
                        fee: uint64
                        ) -> Coin:
    pzl = initial_puzzle(acceptance_modhash,
                         player1_puzzlehash,
                         player1_hashed_preimage,
                         amount)
    return deploy_smart_coin(pzl.get_tree_hash(), amount + (fee * 2), fee)


# Add security
def player2_match_coin(amount: int, fee: int):
    return deploy_smart_coin(match_puzzle().get_tree_hash(), uint64(amount), uint64(fee))


def player2_spend(coin_data: str, puzzlehash, preimage):
    coin_data = json.loads(coin_data)
    puzzle = initial_puzzle(acceptance_modhash(),
                            bytes32.fromhex(coin_data['puzzlehash']),
                            bytes32.fromhex(coin_data['hashed_preimage']),
                            uint64(coin_data['amount'])
                            )
    solution = Program.to([bytes32.fromhex(puzzlehash), bytes32.fromhex(preimage)])
    print("Creating spend for duel...")
    spend = CoinSpend(
        coin=Coin(bytes32.fromhex(coin_data['coin_parent']),
                  bytes32.fromhex(coin_data['coin_puzzlehash']),
                  uint64(coin_data['coin_amount'])),
        puzzle_reveal=puzzle.to_serialized_program(),
        solution=solution.to_serialized_program()
    )
    print("Creating matching wager contribution...")
    match_coin = player2_match_coin(coin_data['amount'], coin_data['tx_fee'])
    print("Created match coin:")
    print(match_coin)
    match_spend = CoinSpend(
        coin=match_coin,
        puzzle_reveal=match_puzzle(),
        solution=Program.to([])
    )
    spend_bundle: SpendBundle = SpendBundle([spend, match_spend], G2Element())
    print("Broadcasting spend to network...")
    print(push_tx(spend_bundle))
    print(spend_bundle)


def player1_check_for_accept(coin_data: str) -> CoinSpend:
    coin_data = json.loads(coin_data)
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


def player1_calculate_acceptance_coin(coin_data: str, coin_solution: dict):
    coin_data = json.loads(coin_data)
    puzzle = acceptance_puzzle(
        bytes32.fromhex(coin_data['puzzlehash']),
        bytes32.fromhex(coin_data['hashed_preimage']),
        uint64(coin_data['amount']),
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
def player1_submit_preimage(preimage: str, coin_data: str):
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
        print(spend_bundle.coin_spends[0])
        return spend_bundle.coin_spends[0]
    except Exception as e:
        print("Spend failed :(")
        print(e)


