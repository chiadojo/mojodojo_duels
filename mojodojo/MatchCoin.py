import hashlib

from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_spend import CoinSpend
from chia.types.spend_bundle import SpendBundle
from chia.util.ints import uint64
from chia.wallet.transaction_record import TransactionRecord

from drivers.chia_utils import deploy_smart_coin, get_signed_tx
from drivers.clvm_drivers import match_puzzle
from drivers.security import Security


class MatchCoin:
    acceptor_pubkey: bytes32
    acceptor_puzzlehash: bytes32
    acceptor_preimage: bytes32
    amount: int
    tx_fee: int

    coin: Coin
    spendBundle: SpendBundle

    def create_coin(self):
        # TODO: Replace with individual standard transaction spendbundle
        print(self.tx_fee)
        tr: TransactionRecord = get_signed_tx(self.get_puzzle().get_tree_hash(), uint64(self.amount),
                                              uint64(self.tx_fee))
        self.coin = tr.additions[0]
        self.spendBundle = tr.spend_bundle

    # TODO: Must be a better way to do this
    @staticmethod
    def create(
            acceptor_pubkey: bytes32,
            acceptor_puzzlehash: bytes32,
            acceptor_preimage: bytes32,
            amount: int,
            tx_fee: int
    ):
        new_coin = MatchCoin()
        new_coin.acceptor_pubkey = acceptor_pubkey
        new_coin.acceptor_puzzlehash = acceptor_puzzlehash
        new_coin.acceptor_preimage = acceptor_preimage
        new_coin.amount = amount
        new_coin.tx_fee = tx_fee

        new_coin.create_coin()
        return new_coin

    def get_puzzle(self):
        return match_puzzle(
            self.acceptor_pubkey,
            self.acceptor_puzzlehash,
            self.acceptor_preimage,
            self.amount
        )

    def broadcast(self):
        self.coin = deploy_smart_coin(self.get_puzzle().get_tree_hash(), uint64(self.amount), uint64(self.tx_fee))

    def get_coin_spend(self, initial_coin_id: bytes32 = 0) -> CoinSpend:
        return CoinSpend(
            coin=self.coin,
            puzzle_reveal=self.get_puzzle().to_serialized_program(),
            solution=Program.to([initial_coin_id]).to_serialized_program()
        )

    def get_agg_sig(self, s: Security, initial_coin_id: bytes32 = 0):
        return s.sign_coin_and_message(
            hashlib.sha256(self.acceptor_puzzlehash + self.acceptor_preimage + initial_coin_id).digest(),
            self.coin.name()
        )
