import json
from chia.types.blockchain_format.sized_bytes import bytes32
from blspy import G1Element, G2Element
from chia.cmds.units import units
from chia.types.spend_bundle import SpendBundle
from chia.util.bech32m import decode_puzzle_hash
from time import sleep
from drivers.chia_utils import push_tx
import hashlib

from drivers.security import Security
from mojodojo.InitiationCoin import InitiationCoin
from mojodojo.MatchCoin import MatchCoin
from mojodojo.AcceptanceCoin import AcceptanceCoin


# TODO: Chialisp fees, separate optional and gas - this doesn't exist
# TODO: Option to select wallet
# TODO: Add ways to check that spends are successful
# TODO: Add async to everything
# TODO: Clarification between bytes and bytes32?
# TODO: move drivers into objects?
# TODO: improvements / minification to chia_utils
# TODO: make light-wallet compatible
class Duel:
    initiator_preimage: bytes32

    tx_fee: int

    acceptor_puzzlehash: bytes32
    acceptor_preimage: bytes32

    initial_coin: InitiationCoin

    match_coin: MatchCoin
    acceptance_coin: AcceptanceCoin

    # TODO: Validate JSON when input
    # TODO: Verify JSON when input
    @staticmethod
    def from_json(json: dict, initiation_spend: SpendBundle = None):
        new_duel = Duel()
        new_duel.initial_coin = InitiationCoin.load(
            bytes32.fromhex(json['puzzlehash']),
            bytes32.fromhex(json['hashed_preimage']),
            G1Element.from_bytes(bytes.fromhex(json['pubkey'])),
            int(json['amount']),
            int(json['tx_fee']),
            bytes32.fromhex(json['coin_parent']),
            bytes32.fromhex(json['coin_puzzlehash']),
            int(json['coin_amount']),
        )
        new_duel.initial_coin.spendBundle = initiation_spend
        return new_duel

    def get_json(self):
        return json.dumps({'coinid': self.initial_coin.coin.name().hex(),
                           'pubkey': bytes(self.initial_coin.initiator_pubkey).hex(),
                           'coin_parent': self.initial_coin.coin.parent_coin_info.hex(),
                           'coin_puzzlehash': self.initial_coin.coin.puzzle_hash.hex(),
                           'coin_amount': self.initial_coin.coin.amount,
                           'puzzlehash': self.initial_coin.initiator_puzzlehash.hex(),
                           'hashed_preimage': self.initial_coin.initiator_hashed_preimage.hex(),
                           'amount': self.initial_coin.amount,
                           'tx_fee': self.initial_coin.tx_fee
                           })

    # TODO: add ability to input raw preimage/ hashed preimage
    @staticmethod
    def create_new(pubkey: G1Element, payout_address: str, random: str, wager: float, fee=1000000000):
        new_duel = Duel()
        preimage = hashlib.sha256(random.encode())
        hashed_preimage = bytes32.from_bytes(hashlib.sha256(preimage.digest()).digest())
        new_duel.initial_coin = InitiationCoin.create(
            decode_puzzle_hash(payout_address),
            hashed_preimage,
            pubkey,
            int(units['chia'] * wager),
            int(fee)
        )
        print("Creating initial coin spend...")
        new_duel.initial_coin.create_coin()
        return new_duel

    def recover(self, s: Security):
        recover_spend = self.initial_coin.get_recover_coin_spend()
        signature = self.initial_coin.get_recover_agg_sig(s)
        spend_bundle: SpendBundle = SpendBundle([recover_spend], signature)
        print("Recovery SpendBundle:")
        print(spend_bundle.to_json_dict())
        push_tx(spend_bundle)

    # TODO: replace security with CLI for Chia keys.
    # TODO: add ability to input raw preimage
    # TODO: include MatchCoin creation in secondary SpendBundle
    # TODO: make async
    def accept(self, s: Security, payout_address: str, random: str, fee: int = 1000000000):
        pubkey = s.get_pk()
        preimage = bytes32.from_bytes(hashlib.sha256(random.encode()).digest())
        puzzlehash = bytes32.from_bytes(decode_puzzle_hash(payout_address))
        initial_spend = self.initial_coin.get_coin_spend(puzzlehash, preimage, pubkey)
        self.match_coin = MatchCoin.create(
            s.get_pk(),
            puzzlehash,
            preimage,
            self.initial_coin.amount,
            fee
        )
        match_spend = self.match_coin.get_coin_spend(initial_spend.coin.name())
        signature = self.match_coin.get_agg_sig(s, initial_spend.coin.name())
        spend_bundle: SpendBundle = SpendBundle([initial_spend, match_spend], signature)
        pk = s.sk.__bytes__().hex()
        print(self.get_json())
        # print(push_tx(spend_bundle))
        print(self.initial_coin.spendBundle)
        return SpendBundle.aggregate([self.initial_coin.spendBundle, self.match_coin.spendBundle, spend_bundle])

    def finalise(self, random: str, acceptance_spend_bundle: SpendBundle):
        preimage = bytes32.from_bytes(hashlib.sha256(random.encode()).digest())

        solution = None
        if acceptance_spend_bundle is None:

            while not self.initial_coin.is_spent():
                sleep(5)
                print("Initial coin not spent, sleeping for 5 seconds")

            solution = self.initial_coin.get_solution()

        else:
            # print(acceptance_spend_bundle)
            exit()
            solution = self.initial_coin.get_solution_from_spend_bundle(acceptance_spend_bundle.coin_spends[1])
            # print(acceptance_spend)
            # print(acceptance_spend.coin_spends[1])
            # print(type(acceptance_spend.coin_spends[1]))

        acceptance_coin = AcceptanceCoin.load(
            self.initial_coin.initiator_puzzlehash,
            self.initial_coin.initiator_hashed_preimage,
            self.initial_coin.amount,
            bytes32.fromhex(solution['puzzlehash']),  # TODO: I think these are already in bytes?
            bytes32.fromhex(solution['preimage'])
        )

        acceptance_coin.calculate_coin(self.initial_coin.coin.name(),
                                       (self.initial_coin.amount * 2 + self.initial_coin.tx_fee))
        acceptance_spend = acceptance_coin.get_coin_spend(preimage)
        spend_bundle: SpendBundle = SpendBundle([acceptance_spend], G2Element())
        # print(f"Raw preimage: {preimage.hex()}")
        # print("Final SpendBundle")
        # print(spend_bundle)
        print(acceptance_spend_bundle)
        print(spend_bundle)
        return SpendBundle.aggregate([spend_bundle, acceptance_spend_bundle])

    # TODO: remove duplicated code
    def force_forfeit(self):
        while not self.initial_coin.is_spent():
            sleep(5)
            print("Initial coin not spent, sleeping for 5 seconds")

        # We could try to fetch this directly - if done by the acceptor
        # i.e if self.match_coin
        solution = self.initial_coin.get_solution()

        acceptance_coin = AcceptanceCoin.load(
            self.initial_coin.initiator_puzzlehash,
            self.initial_coin.initiator_hashed_preimage,
            self.initial_coin.amount,
            bytes32.fromhex(solution['puzzlehash']),  # TODO: I think these are already in bytes?
            bytes32.fromhex(solution['preimage'])
        )

        acceptance_coin.calculate_coin(self.initial_coin.coin.name(),
                                       (self.initial_coin.amount * 2 + self.initial_coin.tx_fee))
        acceptance_spend = acceptance_coin.get_coin_spend(0)
        spend_bundle: SpendBundle = SpendBundle([acceptance_spend], G2Element())
        print(push_tx(spend_bundle))
