from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_spend import CoinSpend
from chia.util.ints import uint64

from drivers.clvm_drivers import acceptance_modhash, acceptance_puzzle


class AcceptanceCoin:
    initiatior_puzzlehash: bytes32
    initiator_hashed_preiamge: bytes32
    amount: int

    acceptor_puzzlehash: bytes32
    acceptor_preimage: bytes32

    coin: Coin

    # TODO: Definitely a better way to do this too
    @staticmethod
    def load(
            initiatior_puzzlehash: bytes32,
            initiator_hashed_preiamge: bytes32,
            amount: int,
            acceptor_puzzlehash: bytes32,
            acceptor_preimage: bytes32
    ):
        new_coin = AcceptanceCoin()
        new_coin.initiatior_puzzlehash = initiatior_puzzlehash
        new_coin.initiator_hashed_preiamge = initiator_hashed_preiamge
        new_coin.amount = amount
        new_coin.acceptor_puzzlehash = acceptor_puzzlehash
        new_coin.acceptor_preimage = acceptor_preimage
        return new_coin

    @staticmethod
    def get_modhash() -> bytes32:
        return acceptance_modhash()

    def get_puzzle(self):
        return acceptance_puzzle(
            self.initiatior_puzzlehash,
            self.initiator_hashed_preiamge,
            self.amount,
            self.acceptor_puzzlehash,
            self.acceptor_preimage
        )

    def calculate_coin(self, initial_coin_id: bytes32, amount: int):
        self.coin = Coin(
            parent_coin_info=initial_coin_id,
            puzzle_hash=self.get_puzzle().get_tree_hash(),
            amount=uint64(amount)
        )

    def get_coin_spend(self, initiator_preimage):
        return CoinSpend(
            coin=self.coin,
            puzzle_reveal=self.get_puzzle(),
            solution=Program.to([initiator_preimage]).to_serialized_program()
        )
