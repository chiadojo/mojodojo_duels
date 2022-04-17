import asyncio
import time
import unittest

from blspy import G2Element
from cdv.util.load_clvm import load_clvm
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_record import CoinRecord
from chia.types.coin_spend import CoinSpend
from chia.types.spend_bundle import SpendBundle
from chia.util.ints import uint64

from drivers.chia_utils import push_tx, get_coin
from .mojo_dojo_drivers import acceptance_modhash, create_initial_coin, acceptance_puzzle, initial_puzzle
from .cli_tools import calculate_acceptance_modhash, expected_acceptance_puzzlehash, \
    calculate_initiation_curry_treehash, calculate_initiation_soln_treehash

INITIATION_CLSP = "initiation.clsp"
ACCEPTANCE_CLSP = "acceptance.clsp"

player1 = {}
player1['puzzlehash'] = bytes32.fromhex("7af35fd818ac8cff6ae695adc2389a92db995527d9669d0c5678f12408e2d675")
player1['puzzlehash_str'] = "0x7af35fd818ac8cff6ae695adc2389a92db995527d9669d0c5678f12408e2d675"

player1['preimage'] = bytes32.fromhex("2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")
player1['preimage_str'] = "0x2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

player1['hashed_preimage'] = bytes32.fromhex("9595c9df90075148eb06860365df33584b75bff782a510c6cd4883a419833d50")
player1['hashed_preimage_str'] = "0x9595c9df90075148eb06860365df33584b75bff782a510c6cd4883a419833d50"

player2 = {}
player2['puzzlehash'] = bytes32.fromhex("39efec30b7dd621f59c191d8838d8f383729e838508211a04c1683e5d66b5f3c")
player2['puzzlehash_str'] = "0x39efec30b7dd621f59c191d8838d8f383729e838508211a04c1683e5d66b5f3c"

player2['preimage'] = bytes32.fromhex("82e35a63ceba37e9646434c5dd412ea577147f1e4a41ccde1614253187e3dbf9")
player2['preimage_str'] = "0x82e35a63ceba37e9646434c5dd412ea577147f1e4a41ccde1614253187e3dbf9"

amount = uint64(1000)
amount_str = "1000"

fee = uint64(1000)
fee_str = "1000"


class AllTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(AllTests, self).__init__(*args, **kwargs)
        self._ACCEPTANCE_MODHASH = calculate_acceptance_modhash()
        self._INITIATION_TREEHASH = calculate_initiation_curry_treehash(self._ACCEPTANCE_MODHASH,
                                                        player1['puzzlehash_str'],
                                                        player1['hashed_preimage_str'],
                                                        amount_str)
        self._INITIATION_RESULT = calculate_initiation_soln_treehash(self._ACCEPTANCE_MODHASH,
                                                        player1['puzzlehash_str'],
                                                        player1['hashed_preimage_str'],
                                                        amount_str,
                                                        player2['puzzlehash_str'],
                                                        player2['preimage_str'])
        self._ACCEPTANCE_TREEHASH = expected_acceptance_puzzlehash(
                                                        player1['puzzlehash_str'],
                                                        player1['hashed_preimage_str'],
                                                        amount_str,
                                                        player2['puzzlehash_str'],
                                                        player2['preimage_str'])

    def test_acceptance_modhash(self):
        self.assertEqual(calculate_acceptance_modhash(), bytes32.fromhex(self._ACCEPTANCE_MODHASH))

    # def test_initiation_treehash(self):
    #     self.assertIsNotNone()

    def test_create_and_spend_initiation_coin(self):
        acc_modhash = acceptance_modhash()

        coin: Coin = create_initial_coin(
                                         acc_modhash,
                                         player1['puzzlehash'],
                                         player1['hashed_preimage'],
                                         amount,
                                         fee)

        # Assert that destination puzzlehash is calculated correctly
        self.assertEqual(coin.puzzle_hash, bytes32.fromhex(self._INITIATION_TREEHASH))
        print(coin.get_hash())

        # Spend and find destination puzzlehash (should = self._INITIATION_RESULT
        spend = CoinSpend(
            coin=coin,
            puzzle_reveal=initial_puzzle(
                                              player1['puzzlehash'],
                                              player1['hashed_preimage'],
                                              amount),
            solution=Program.to([player2['puzzlehash'],
                                 player2['preimage']]).to_serialized_program()
        )
        spend_bundle: SpendBundle = SpendBundle([spend], G2Element())
        print(push_tx(spend_bundle))
        print(spend_bundle.coin_spends[0])

        targetCoin: Coin = Coin(parent_coin_info=coin.get_hash(),
                                puzzle_hash=bytes32.fromhex(self._ACCEPTANCE_TREEHASH), amount=amount + 2000000000 + 5000)

        # Doesn't work for some reason?
        coin_record :CoinRecord = get_coin(targetCoin.get_hash())
        while coin_record is None:
            asyncio.sleep(5)
            coin_record: CoinRecord = get_coin(targetCoin.get_hash())
        print(coin_record)

        spend2 = CoinSpend(
            coin=targetCoin,
            puzzle_reveal=acceptance_puzzle(
                                            player1['puzzlehash'],
                                            player1['hashed_preimage'],
                                            amount,
                                            player2['puzzlehash'],
                                            player2['preimage']),
            solution=Program.to([player1['preimage']]).to_serialized_program()
        )

        spend_bundle: SpendBundle = SpendBundle([spend2], G2Element())
        print(spend2)
        print(spend_bundle)
        print(push_tx(spend_bundle))
        print(spend_bundle.coin_spends[0])
        # Add way to check final coin gets created

    def test_acceptance_treehash_cli(self):
        self.assertEqual(self._ACCEPTANCE_TREEHASH, self._INITIATION_RESULT)

    def test_acceptance_treehash(self):
        self.assertEqual(expected_acceptance_puzzlehash(
            player1['puzzlehash'],
            player1['hashed_preimage'],
            amount,
            player2['puzzlehash'],
            player2['preimage']).hex(), self._INITIATION_RESULT)


if __name__ == '__main__':
    unittest.main()
