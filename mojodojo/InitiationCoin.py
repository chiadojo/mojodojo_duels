from blspy import G1Element
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_record import CoinRecord
from chia.types.coin_spend import CoinSpend
from chia.types.spend_bundle import SpendBundle
from chia.util.ints import uint64
from chia.wallet.transaction_record import TransactionRecord

from drivers.chia_utils import deploy_smart_coin, get_coin, get_coin_solution, get_signed_tx, push_tx
from drivers.security import Security
from mojodojo.AcceptanceCoin import AcceptanceCoin

from drivers.clvm_drivers import initial_puzzle


class InitiationCoin:
    initiator_puzzlehash: bytes32
    initiator_hashed_preimage: bytes32
    initiator_pubkey: G1Element
    amount: int
    tx_fee: int

    coin: Coin
    spendBundle: SpendBundle


    def create_coin(self):
        # TODO: Replace with individual standard transaction spendbundle
        tr: TransactionRecord = get_signed_tx(self.get_puzzle().get_tree_hash(),
                                              uint64(self.amount + (self.tx_fee * 2)),
                                              self.tx_fee)
        self.coin = tr.additions[0]
        self.spendBundle = tr.spend_bundle

    # Deploys the coin with the current parameters
    def broadcast(self):
        push_tx(self.spendBundle)

    # Creates a new coin for broadcasting
    # TODO: Must be a better way to do this
    @staticmethod
    def create(
            initiator_puzzlehash: bytes32,
            initiator_hashed_preimage: bytes32,
            initiator_pubkey: G1Element,
            amount: int,
            tx_fee: int
    ):
        init_coin = InitiationCoin()
        init_coin.initiator_puzzlehash = initiator_puzzlehash
        init_coin.initiator_hashed_preimage = initiator_hashed_preimage
        init_coin.initiator_pubkey = initiator_pubkey
        init_coin.amount = amount
        init_coin.tx_fee = tx_fee
        return init_coin

    # Loads an already-created coin (this may now be accepted)
    @staticmethod
    def load(
            initiator_puzzlehash: bytes32,
            initiator_hashed_preimage: bytes32,
            initiator_pubkey: G1Element,
            amount: int,
            tx_fee: int,
            coin_parent: bytes32,
            coin_puzzlehash: bytes32,
            coin_amount: int
    ):
        init_coin = InitiationCoin.create(initiator_puzzlehash, initiator_hashed_preimage, initiator_pubkey, amount,
                                          tx_fee)
        init_coin.coin = Coin(coin_parent, coin_puzzlehash, uint64(coin_amount))
        return init_coin

    def get_puzzle(self) -> Program:
        return initial_puzzle(
            AcceptanceCoin.get_modhash(),
            self.initiator_pubkey,
            self.initiator_puzzlehash,
            self.initiator_hashed_preimage,
            self.amount
        )

    # Get coin spend with parameters
    def get_coin_spend(self, puzzlehash: bytes32 = 0, preimage: bytes32 = 0, pubkey: G1Element = 0) -> CoinSpend:
        # Calculate CoinSpend for Initial coin
        return CoinSpend(
            coin=self.coin,
            puzzle_reveal=self.get_puzzle().to_serialized_program(),
            solution=Program.to([puzzlehash, preimage, pubkey]).to_serialized_program()
        )

    def get_recover_coin_spend(self):
        return self.get_coin_spend(pubkey=self.initiator_pubkey)

    def get_recover_agg_sig(self, s: Security):
        return s.sign_coin_and_message(
            self.initiator_puzzlehash,
            self.coin.name()
        )

    def is_spent(self):
        coin_record: CoinRecord = get_coin(self.coin.name())
        if not coin_record:
            return 0
        if not coin_record.spent:
            return 0
        return coin_record.spent_block_index

    # TODO: maybe make polymorphic with get_coin_spend
    def get_solution(self):
        coin_solution = get_coin_solution(self.coin.name(), self.is_spent())
        p = Program.from_serialized_program(coin_solution.solution)
        return {'puzzlehash': p.first().atom.hex(), 'preimage': p.rest().first().atom.hex()}

    def get_solution_from_spend_bundle(self, cs : CoinSpend):
        p = Program.from_serialized_program(cs.solution)
        return {'puzzlehash': p.first().atom.hex(), 'preimage': p.rest().first().atom.hex()}

    def verify(self):
        return True
    #
