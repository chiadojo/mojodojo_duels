import json

from drivers import create_duel, accept_duel, finalise_duel

tx_fee = 1000000000
amount = 0.0001 # xch

# json_data = create_duel("txch15w666tgu68lfl937hghqvmsyewrxvyvy5z5w5rr9a62xnennqfls7v8xs0",
#                         "weeeseseseseseese6465",
#                         amount,
#                         tx_fee
#                         )
#
# json_dict = json.loads(json_data)
#
# accept_duel(json_dict,
#             "txch1rjecdus8ahykurjudarrrs2gyxwyd0s64yxf8yef6psudhj0duqq86kqc9",
#             "woooooo"
#             )
#
# finalise_duel("weeeseseseseseese6465", json_dict)
