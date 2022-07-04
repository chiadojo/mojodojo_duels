import json

from chia.types.blockchain_format.sized_bytes import bytes32

import drivers.chia_utils
from drivers.security import Security
from mojodojo.Duel import Duel

tx_fee = 1000000000
amount = 0.000001

s_dev = Security(122, 244)
s1 = Security(123, 234)
s2 = Security(124, 235)

print(s1.get_pk())
print(s1.sk)


# TODO: Prepend 0's to numbers like frontend
# TODO: Add tests for forfeiting and recovering

def test_aggregate_spend_bundles():
    d1: Duel = Duel.create_new(s1.get_pk(),
                               "txch15w666tgu68lfl937hghqvmsyewrxvyvy5z5w5rr9a62xnennqfls7v8xs0",
                               "kdfnksabdfas",
                               amount
                               )

    json_dict = json.loads(d1.get_json())
    print(json_dict)
    d2 = Duel.from_json(json_dict, d1.initial_coin.spendBundle)
    spendBundle = d2.accept(s2,
                            "txch1rjecdus8ahykurjudarrrs2gyxwyd0s64yxf8yef6psudhj0duqq86kqc9",
                            "slkdfhjklashjfd"
                            )
    print(spendBundle)
    finalsb = d1.finalise("kdfnksabdfas", spendBundle)
    print(finalsb)
    drivers.chia_utils.push_tx(finalsb)
    # print(spendBundle)


def test_complete():
    d1: Duel = Duel.create_new(s1.get_pk(),
                               "txch15w666tgu68lfl937hghqvmsyewrxvyvy5z5w5rr9a62xnennqfls7v8xs0",
                               "kdfnksabdfas",
                               amount
                               )
    json_dict = json.loads(d1.get_json())
    print(json_dict)
    d2 = Duel.from_json(json_dict)
    d2.accept(s2,
              "txch1rjecdus8ahykurjudarrrs2gyxwyd0s64yxf8yef6psudhj0duqq86kqc9",
              "slkdfhjklashjfd"
              )
    d1.finalise("kdfnksabdfas")


test_aggregate_spend_bundles()

# from cli_tools import calculate_acceptance_modhash, calculate_initiation_curry_treehash, calculate_initiation_soln_treehash, expected_acceptance_puzzlehash
#
# acceptance_modhash = calculate_acceptance_modhash()
# print(f"Acceptance Modhash {acceptance_modhash}")
#
# initiation_curry_treehash = calculate_initiation_curry_treehash(acceptance_modhash, player1['puzzlehash_str'], player1['hashed_preimage_str'], amount_str)
# print(f"Initiation Curry Treehash {initiation_curry_treehash}")

# json_data = create_duel(s1.get_pk(),
#                         "txch15w666tgu68lfl937hghqvmsyewrxvyvy5z5w5rr9a62xnennqfls7v8xs0",
#                         "kdfnksabdfas",
#                         amount,
#                         tx_fee
#                         )

# json_dict = json.loads(json_data)

# accept_duel(json_dict,
#             s2,
#             "txch1rjecdus8ahykurjudarrrs2gyxwyd0s64yxf8yef6psudhj0duqq86kqc9",
#             "slkdfhjklashjfd"
#             )
