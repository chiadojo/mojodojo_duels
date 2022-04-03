from cdv.util.load_clvm import load_clvm
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.bech32m import decode_puzzle_hash, encode_puzzle_hash
from chia.util.ints import uint64


INITIATION_CLSP = "initiation.clsp"
ACCEPTANCE_CLSP = "acceptance.clsp"
MATCH_CLSP = "match.clsp"

def match_puzzle() -> Program:
    mod = load_clvm(MATCH_CLSP, package_or_requirement=__name__)
    return mod

def acceptance_modhash() -> bytes32:
    acceptance = load_clvm(ACCEPTANCE_CLSP, package_or_requirement=__name__)
    return acceptance.get_tree_hash()

def initial_puzzle(acceptance_modhash: bytes32,
                   player1_puzzlehash: bytes32,
                   player1_hashed_preimage: bytes32,
                   amount: uint64
                   ) -> Program:
    initiation = load_clvm(INITIATION_CLSP, package_or_requirement=__name__)
    initiation = initiation.curry(acceptance_modhash, player1_puzzlehash, player1_hashed_preimage, amount)
    return initiation


def acceptance_puzzle(player1_puzzlehash: bytes32,
                      player1_hashed_preimage: bytes32,
                      amount: uint64,
                      player2_puzzlehash: bytes32,
                      player2_preimage: bytes32):
    acceptance = load_clvm(ACCEPTANCE_CLSP, package_or_requirement=__name__)
    acceptance = acceptance.curry(player1_puzzlehash, player1_hashed_preimage, amount, player2_puzzlehash,
                                  player2_preimage)
    return acceptance
