import json

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.ints import uint64

from mojodojo.Duel import Duel
from drivers import create_duel, accept_duel, finalise_duel, security, cancel_duel, forfeit_duel

tx_fee = 1000000000
amount = 0.0001  # xch
#
# player1 = {}
# player1['puzzlehash'] = bytes32.fromhex("7af35fd818ac8cff6ae695adc2389a92db995527d9669d0c5678f12408e2d675")
# player1['puzzlehash_str'] = "0x7af35fd818ac8cff6ae695adc2389a92db995527d9669d0c5678f12408e2d675"
#
# player1['preimage'] = bytes32.fromhex("2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")
# player1['preimage_str'] = "0x2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
#
# player1['hashed_preimage'] = bytes32.fromhex("9595c9df90075148eb06860365df33584b75bff782a510c6cd4883a419833d50")
# player1['hashed_preimage_str'] = "0x9595c9df90075148eb06860365df33584b75bff782a510c6cd4883a419833d50"
#
# player2 = {}
# player2['puzzlehash'] = bytes32.fromhex("39efec30b7dd621f59c191d8838d8f383729e838508211a04c1683e5d66b5f3c")
# player2['puzzlehash_str'] = "0x39efec30b7dd621f59c191d8838d8f383729e838508211a04c1683e5d66b5f3c"
#
# player2['preimage'] = bytes32.fromhex("82e35a63ceba37e9646434c5dd412ea577147f1e4a41ccde1614253187e3dbf9")
# player2['preimage_str'] = "0x82e35a63ceba37e9646434c5dd412ea577147f1e4a41ccde1614253187e3dbf9"
#
# amount = 0.001
# amount_str = "100000000000"
#
# fee = uint64(1000)
# fee_str = "1000"


s_dev = security.Security(122, 244)
s1 = security.Security(123, 234)
s2 = security.Security(124, 235)
# print(s_dev.get_pk())


d1: Duel = Duel.create_new(s1.get_pk(),
                           "txch15w666tgu68lfl937hghqvmsyewrxvyvy5z5w5rr9a62xnennqfls7v8xs0",
                           "kdfnksabdfas",
                           amount
                           )

print(d1.get_json())
json_dict = json.loads(d1.get_json())
d2 = Duel.from_json(json_dict)
d2.accept(s2,
          "txch1rjecdus8ahykurjudarrrs2gyxwyd0s64yxf8yef6psudhj0duqq86kqc9",
          "slkdfhjklashjfd"
          )


# d1.finalise("kdfnksabdfas")
d2.force_forfeit()

# print(d2.get_json())
#
exit()

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

forfeit_duel(json_dict)
finalise_duel("kdfnksabdfas", json_dict)
