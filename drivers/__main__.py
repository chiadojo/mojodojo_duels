import json
from time import sleep
import os
import hashlib

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.bech32m import decode_puzzle_hash


from time import sleep
from drivers.mojo_dojo_drivers import player1_create, player1_check_for_accept, player2_spend, \
    player1_submit_preimage
import os
import hashlib



def create_duel(payout_address, preimage, wager, fee) -> str:
    address = decode_puzzle_hash(payout_address).hex()
    bytes_preimage = preimage.encode('ascii')
    hashed_preimage = hashlib.sha256(bytes_preimage).hexdigest()
    print("Creating spend transaction...")
    if fee < 10000000:
        print("Fee too low :(")
    return player1_create(address, hashed_preimage, wager, fee)


def accept_duel(json_dict: dict, payout_address, preimage):
    coin_data = json.dumps(json_dict)
    address = decode_puzzle_hash(payout_address).hex()
    print(f"Hex address: {address}")
    print(f"Loaded JSON: {coin_data}")
    preimage_hex = str(preimage.encode('ascii').hex())
    player2_spend(coin_data, address, preimage_hex)


def finalise_duel(preimage, coin_data: dict):
    json_str = json.dumps(coin_data)
    preimage_hex = str(preimage.encode('ascii').hex())
    # print(f"preimage hex: {preimage_hex}")
    preimage_bytes = bytes32.fromhex(preimage_hex)
    return player1_submit_preimage(preimage_bytes, json_str)

# player1 = {}
# player1['puzzlehash'] = "60e4c13699c9c8986d72a9b9ce91630a909d9e0050eb4eaae9ef8e222bd86825"
# player1['preimage'] = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
# player1['hashed_preimage']= "9595c9df90075148eb06860365df33584b75bff782a510c6cd4883a419833d50"
#
# player2 = {}
# player2['puzzlehash'] =  "1cb386f207edc96e0e5c6f4631c148219c46be1aa90c939329d061c6de4f6f00"
# player2['preimage'] = "85dd412ea577147f1e4a41ccde1614253187e3dbf9"

player1 = {}
player1['puzzlehash'] = "txch15w666tgu68lfl937hghqvmsyewrxvyvy5z5w5rr9a62xnennqfls7v8xs0"
player1['preimage'] = "000000000000000000000000weeeeeee"

player2 = {}
player2['puzzlehash'] =  "txch14tuetqca0vrh5u7cqr42nngdxh32s9t96v2wys69q9p8uwzs4yaqjqkf2e"
player2['preimage'] = "000000000000000000000000wooooooo"


tx_fee = 1000000000
amount = 10000

#
# player1 = {}
# player1['puzzlehash'] = "60e4c13699c9c8986d72a9b9ce91630a909d9e0050eb4eaae9ef8e222bd86825"
# player1['random'] = os.urandom(32)
# player1['preimage'] = player1['random'].hex()
# player1['hashed_preimage'] = hashlib.sha256(player1['random']).hexdigest()
#
# player2 = {}
# player2['puzzlehash'] =  "1cb386f207edc96e0e5c6f4631c148219c46be1aa90c939329d061c6de4f6f00"
# player2['preimage'] = os.urandom(32).hex()

# json_data = create_duel(player1['puzzlehash'], player1['preimage'], amount, tx_fee)
# print(json_data)
#
# sleep(300)
#
# #
# #
# # # Player 1 shares json_data to player2
# accept_duel(json.loads(json_data), player2['puzzlehash'], player2['preimage'])
#
# while finalise_duel(player1['preimage'], json.loads(json_data)) is None:
#     print("Sleeping fo 5")
#     sleep(5)
#
# sleep(300)

# while player1_check_for_accept(json_data) is None:
#     sleep(20)

# player1_submit_preimage(player1['preimage'], json_data)


player1 = {}
player1['puzzlehash'] = "60e4c13699c9c8986d72a9b9ce91630a909d9e0050eb4eaae9ef8e222bd86825"
player1['preimage'] = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
player1['hashed_preimage']= "9595c9df90075148eb06860365df33584b75bff782a510c6cd4883a419833d50"

player2 = {}
player2['puzzlehash'] =  "1cb386f207edc96e0e5c6f4631c148219c46be1aa90c939329d061c6de4f6f00"
player2['preimage'] = "82e35a63ceba37e9646434c5dd412ea577147f1e4a41ccde1614253187e3dbf9"


tx_fee = 1000000000
amount = 10000

json_data = player1_create(player1['puzzlehash'], player1['hashed_preimage'], amount, tx_fee)
print(json_data)

# # Player 1 shares json_data to player2
player2_spend(json_data, player2['puzzlehash'], player2['preimage'])

while player1_check_for_accept(json_data) is None:
    sleep(20)

player1_submit_preimage(player1['preimage'], json_data)


