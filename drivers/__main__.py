from chia.util.bech32m import decode_puzzle_hash
from time import sleep
from drivers.mojo_dojo_drivers import player1_create, player1_check_for_accept, player2_spend, \
    player1_submit_preimage
import hashlib

tx_fee = 1000000000
amount = 10000


def create_duel(payout_address, preimage, wager, fee) -> str:
    address = decode_puzzle_hash(payout_address).hex()
    total_preimage = "0" * (32 - len(preimage)) + preimage
    hashed_preimage = hashlib.sha256(total_preimage.encode()).hexdigest()
    print("Creating spend transaction...")
    if fee < 10000000:
        print("Fee too low :(")
    return player1_create(address, hashed_preimage, wager, fee)


json_data = create_duel("txch15w666tgu68lfl937hghqvmsyewrxvyvy5z5w5rr9a62xnennqfls7v8xs0",
                        "weeeeeee",
                        amount,
                        tx_fee
                        )


def accept_duel(json_dict: str, payout_address, preimage):
    # coin_data = json.dumps(json_dict)
    address = decode_puzzle_hash(payout_address).hex()
    total_preimage = "0" * (32 - len(preimage)) + preimage
    player2_spend(json_dict, address, total_preimage.encode().hex())

accept_duel(json_data,
            "txch1rjecdus8ahykurjudarrrs2gyxwyd0s64yxf8yef6psudhj0duqq86kqc9",
            "wooooooo"
            )


def finalise_duel(preimage, coin_data: str):
    total_preimage = "0" * (32 - len(preimage)) + preimage
    print(total_preimage)
    ret = player1_submit_preimage(total_preimage.encode().hex(), coin_data)
    while ret is None:
        sleep(5)
        ret = player1_submit_preimage(total_preimage.encode().hex(), coin_data)
    return ret

finalise_duel("weeeeeee", json_data)


# player1 = {}
# # player1['puzzlehash'] = "3b5ad2d1cd1fe9f963eba2e066e04cb86661184a0a8ea0c65ee9469e673027f"
# player1['puzzlehash'] = decode_puzzle_hash("txch15w666tgu68lfl937hghqvmsyewrxvyvy5z5w5rr9a62xnennqfls7v8xs0").hex()
# # player1['preimage'] = "3030303030303030303030303030303030303030303030307765656565656565"
# player1['preimage'] = "000000000000000000000000weeeeeee".encode('ascii').hex()
# player1['hashed_preimage'] = "b3793c69669b733dae3a30fbaa78862efd172dc2da69bd9a217549bf7a96ef5d"
#
# player2 = {}
# # player2['puzzlehash'] =  "1cb386f207edc96e0e5c6f4631c148219c46be1aa90c939329d061c6de4f6f00"
# player2['puzzlehash'] = decode_puzzle_hash("txch1rjecdus8ahykurjudarrrs2gyxwyd0s64yxf8yef6psudhj0duqq86kqc9").hex()
# # player2['preimage'] = "303030303030303030303030303030303030303030303030776F6F6F6F6F6F6F"
# player2['preimage'] = "000000000000000000000000wooooooo".encode('ascii').hex()

# tx_fee = 1000000000
# amount = 1000000000000

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