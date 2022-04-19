from blspy import G1Element
from cdv.util.load_clvm import load_clvm
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.ints import uint64

INITIATION_CLSP = "initiation.clsp"
ACCEPTANCE_CLSP = "acceptance.clsp"
MATCH_CLSP = "match.clsp"


def match_puzzle(
        pubkey: bytes32,
        puzzlehash: bytes32,
        preimage: bytes32,
        amount: int
        ) -> Program:
    match = load_clvm(MATCH_CLSP, package_or_requirement=__name__)
    match = match.curry(pubkey, puzzlehash, preimage, amount)
    return match


def acceptance_modhash() -> bytes32:
    acceptance = load_clvm(ACCEPTANCE_CLSP, package_or_requirement=__name__)
    return acceptance.get_tree_hash()


def initial_puzzle(acceptance_modhash: bytes32,
                   player1_pubkey: G1Element,
                   player1_puzzlehash: bytes32,
                   player1_hashed_preimage: bytes32,
                   amount: int
                   ) -> Program:
    initiation = load_clvm(INITIATION_CLSP, package_or_requirement=__name__)
    initiation = initiation.curry(acceptance_modhash, player1_pubkey, player1_puzzlehash, player1_hashed_preimage, amount)
    return initiation


def acceptance_puzzle(player1_puzzlehash: bytes32,
                      player1_hashed_preimage: bytes32,
                      amount: int,
                      player2_puzzlehash: bytes32,
                      player2_preimage: bytes32):
    acceptance = load_clvm(ACCEPTANCE_CLSP, package_or_requirement=__name__)
    acceptance = acceptance.curry(player1_puzzlehash, player1_hashed_preimage, amount, player2_puzzlehash,
                                  player2_preimage)
    return acceptance
