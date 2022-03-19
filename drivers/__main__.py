from time import sleep
from drivers.mojo_dojo_drivers import player1_create, player1_check_for_accept, player2_spend, player1_submit_preimage
import os
import hashlib

# player1 = {}
# player1['puzzlehash'] = "60e4c13699c9c8986d72a9b9ce91630a909d9e0050eb4eaae9ef8e222bd86825"
# player1['preimage'] = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
# player1['hashed_preimage']= "9595c9df90075148eb06860365df33584b75bff782a510c6cd4883a419833d50"
#
# player2 = {}
# player2['puzzlehash'] =  "1cb386f207edc96e0e5c6f4631c148219c46be1aa90c939329d061c6de4f6f00"
# player2['preimage'] = "82e35a63ceba37e9646434c5dd412ea577147f1e4a41ccde1614253187e3dbf9"


player1 = {}
player1['puzzlehash'] = "60e4c13699c9c8986d72a9b9ce91630a909d9e0050eb4eaae9ef8e222bd86825"
player1['random'] = os.urandom(32)
player1['preimage'] = player1['random'].hex()
player1['hashed_preimage'] = hashlib.sha256(player1['random']).hexdigest()

player2 = {}
player2['puzzlehash'] =  "1cb386f207edc96e0e5c6f4631c148219c46be1aa90c939329d061c6de4f6f00"
player2['preimage'] = os.urandom(32).hex()

tx_fee = 1000000000
amount = 10000

json_data = player1_create(player1['puzzlehash'], player1['hashed_preimage'], amount, tx_fee)
print(json_data)
#
#
# # Player 1 shares json_data to player2
player2_spend(json_data, player2['puzzlehash'], player2['preimage'])

while player1_check_for_accept(json_data) is None:
    sleep(20)

player1_submit_preimage(player1['preimage'], json_data)

