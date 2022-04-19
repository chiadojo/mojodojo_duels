import json
from chia.types.blockchain_format.sized_bytes import bytes32
from blspy import G1Element, G2Element
from chia.cmds.units import units
from chia.types.spend_bundle import SpendBundle
from chia.util.bech32m import decode_puzzle_hash
from time import sleep
from drivers import Security
from drivers.chia_utils import push_tx
import hashlib
from mojodojo.InitiationCoin import InitiationCoin
from mojodojo.MatchCoin import MatchCoin
from mojodojo.AcceptanceCoin import AcceptanceCoin

# TODO: Chialisp fees, separate optional and gas
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

    # final_coin: FinalCoin


    # TODO: Validate JSON when input
    # TODO: Verify JSON when input
    @staticmethod
    def from_json(json: dict):
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

    # payout_address    : The string value of the TXCH payout address to be used. e.g "txch1d31.."
    # random            : The random entropy to be used, e.g "hello123"
    # wager             : The integer wager in XCH to be committed to the smart coin, e.g 0.1
    # fee               : The transactional network fee to be used, default for testnet = 1000000000
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
        print("Broadcasting initial coin spend...")
        new_duel.initial_coin.broadcast()
        return new_duel

    def recover(self, s: Security):
        recover_spend = self.initial_coin.get_recover_coin_spend()
        signature = self.initial_coin.get_recover_agg_sig(s)
        spend_bundle: SpendBundle = SpendBundle([recover_spend], signature)
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
        self.match_coin.broadcast()
        match_spend = self.match_coin.get_coin_spend(initial_spend.coin.name())
        signature = self.match_coin.get_agg_sig(s, initial_spend.coin.name())
        spend_bundle: SpendBundle = SpendBundle([initial_spend, match_spend], signature)
        push_tx(spend_bundle)
        return spend_bundle.to_json_dict()

    def finalise(self, random: str):
        preimage = bytes32.from_bytes(hashlib.sha256(random.encode()).digest())
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
        acceptance_spend = acceptance_coin.get_coin_spend(preimage)
        spend_bundle: SpendBundle = SpendBundle([acceptance_spend], G2Element())
        push_tx(spend_bundle)

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
