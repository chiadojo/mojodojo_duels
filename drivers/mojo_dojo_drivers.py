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

INITIATION_CLSP = "initiation.clsp"
ACCEPTANCE_CLSP = "acceptance.clsp"
MATCH_CLSP = "match.clsp"


def str_to_bytes32(my_str: str) -> bytes32:
    return bytes32.fromhex(my_str)


def calculate_acceptance_modhash(acceptance_clsp: str) -> bytes32:
    acceptance = load_clvm(acceptance_clsp, package_or_requirement=__name__)
    return acceptance.get_tree_hash()


def player1_create(puzzlehash, hashed_preimage, amount, fee) -> str:
    coin: Coin = create_initial_coin(INITIATION_CLSP,
                                     calculate_acceptance_modhash(ACCEPTANCE_CLSP),
                                     str_to_bytes32(puzzlehash),
                                     str_to_bytes32(hashed_preimage),
                                     uint64(amount),
                                     uint64(amount + fee*2),
                                     uint64(fee))
    return json.dumps({'coinid': coin.name().hex(),
                       'coin_parent': coin.parent_coin_info.hex(),
                       'coin_puzzlehash': coin.puzzle_hash.hex(),
                       'coin_amount': coin.amount,
                       'puzzlehash': puzzlehash,
                       'hashed_preimage': hashed_preimage,
                       'amount': amount,
                       'tx_fee': fee
                       })

def player2_match_coin(amount: int, fee: int):
    mod = load_clvm(MATCH_CLSP, package_or_requirement=__name__)
    treehash=mod.get_tree_hash()
    return deploy_smart_coin(treehash, uint64(amount), uint64(fee))

# Can change for optional fee
# Potentially can restrict to a certain fee set by maker for dust storms
def player2_spend(coin_data: str, puzzlehash, preimage):
    coin_data = json.loads(coin_data)
    puzzle = initial_coin_puzzle(INITIATION_CLSP,
                                 calculate_acceptance_modhash(ACCEPTANCE_CLSP),
                                 str_to_bytes32(coin_data['puzzlehash']),
                                 str_to_bytes32(coin_data['hashed_preimage']),
                                 uint64(coin_data['amount'])
                                 )
    solution = Program.to([str_to_bytes32(puzzlehash), str_to_bytes32(preimage)])
    spend = CoinSpend(
        coin=Coin(str_to_bytes32(coin_data['coin_parent']),
                  str_to_bytes32(coin_data['coin_puzzlehash']),
                  uint64(coin_data['coin_amount'])),
        puzzle_reveal=puzzle,
        solution=solution
    )
    match_spend = CoinSpend(
        coin=player2_match_coin(coin_data['amount'], coin_data['tx_fee']),
        puzzle_reveal=load_clvm(MATCH_CLSP, package_or_requirement=__name__),
        solution=Program.to([])
    )
    spend_bundle: SpendBundle = SpendBundle([spend, match_spend], G2Element())
    print(push_tx(spend_bundle))


def player1_check_for_accept(coin_data: str) -> CoinSpend:
    coin_data = json.loads(coin_data)
    coin_record: CoinRecord = get_coin(str_to_bytes32(coin_data['coinid']))
    if coin_record is None:
        return None  # Could not find parent coin
    if coin_record.spent_block_index == 0:
        return None  # Could not find spent index
    coin_solution: CoinSpend = get_coin_solution(
        str_to_bytes32(coin_data['coinid']),
        uint32(coin_record.spent_block_index)
    )
    if coin_solution is None:
        print(coin_record)
        print("Found coin record without solution")
    p = Program.from_serialized_program(coin_solution.solution)
    return {'puzzlehash': p.first().atom.hex(), 'preimage': p.rest().first().atom.hex()}


def player1_calculate_acceptance_coin(coin_data: str, coin_solution: dict):
    coin_data = json.loads(coin_data)
    print(coin_data, coin_solution)
    puzzle = acceptance_puzzle(
        ACCEPTANCE_CLSP,
        str_to_bytes32(coin_data['puzzlehash']),
        str_to_bytes32(coin_data['hashed_preimage']),
        uint64(coin_data['amount']),
        str_to_bytes32(coin_solution['puzzlehash']),
        str_to_bytes32(coin_solution['preimage']),
    )
    puzzlehash = calculate_acceptance_treehash(
        ACCEPTANCE_CLSP,
        str_to_bytes32(coin_data['puzzlehash']),
        str_to_bytes32(coin_data['hashed_preimage']),
        uint64(coin_data['amount']),
        str_to_bytes32(coin_solution['puzzlehash']),
        str_to_bytes32(coin_solution['preimage']),
    )
    print(f"player1 calculated puzzlehash {puzzlehash}")
    print(f"Used coin value: {coin_data['amount'] + coin_data['tx_fee']}")
    targetCoin: Coin = Coin(parent_coin_info=str_to_bytes32(coin_data['coinid']),
                            puzzle_hash=puzzlehash,
                            amount=coin_data['amount'] * 2 + coin_data['tx_fee'])
    return puzzle, targetCoin

def player1_submit_preimage(preimage: str, coin_data: str):
    coin_solution = player1_check_for_accept(coin_data)
    if coin_solution is None:
        print("Error, coin hasn't been accepted yet.")
        return None

    puzzle, acceptance_coin = player1_calculate_acceptance_coin(coin_data, coin_solution)
    print(f"Acceptance coin id: {acceptance_coin.name()}")

    spend = CoinSpend(
        coin=acceptance_coin,
        puzzle_reveal=puzzle,
        solution=Program.to([str_to_bytes32(preimage)]).to_serialized_program()
    )


    spend_bundle: SpendBundle = SpendBundle([spend], G2Element())
    print(spend)
    print(spend_bundle)
    print(push_tx(spend_bundle))
    print(spend_bundle.coin_spends[0])


# def player1_spend(coin_solution: str, )

def create_initial_coin(initiation_clsp: str,
                        acceptance_modhash: bytes32,
                        player1_puzzlehash: bytes32,
                        player1_hashed_preimage: bytes32,
                        amount: uint64,
                        amount_to_send: uint64,
                        fee: uint64
                        ) -> Coin:
    initiation = load_clvm(initiation_clsp, package_or_requirement=__name__)
    initiation = initiation.curry(acceptance_modhash, player1_puzzlehash, player1_hashed_preimage, amount)
    return deploy_smart_coin(initiation.get_tree_hash(), amount_to_send, fee)


def initial_coin_puzzle(initiation_clsp: str,
                        acceptance_modhash: bytes32,
                        player1_puzzlehash: bytes32,
                        player1_hashed_preimage: bytes32,
                        amount: uint64
                        ) -> Coin:
    initiation = load_clvm(initiation_clsp, package_or_requirement=__name__)
    initiation = initiation.curry(acceptance_modhash, player1_puzzlehash, player1_hashed_preimage, amount)
    return initiation.to_serialized_program()


def calculate_acceptance_treehash(acceptance_clsp: str,
                                  player1_puzzlehash: bytes32,
                                  player1_hashed_preimage: bytes32,
                                  amount: uint64,
                                  player2_puzzlehash: bytes32,
                                  player2_preimage: bytes32):
    acceptance = load_clvm(acceptance_clsp, package_or_requirement=__name__)
    acceptance = acceptance.curry(player1_puzzlehash, player1_hashed_preimage, amount, player2_puzzlehash,
                                  player2_preimage)
    return acceptance.get_tree_hash()


def acceptance_puzzle(acceptance_clsp: str,
                      player1_puzzlehash: bytes32,
                      player1_hashed_preimage: bytes32,
                      amount: uint64,
                      player2_puzzlehash: bytes32,
                      player2_preimage: bytes32):
    acceptance = load_clvm(acceptance_clsp, package_or_requirement=__name__)
    acceptance = acceptance.curry(player1_puzzlehash, player1_hashed_preimage, amount, player2_puzzlehash,
                                  player2_preimage)
    return acceptance.to_serialized_program()
