# The Mojo Dojo User Guide
### Installation
The dependencies are packaged with PyPi.  
The only requirement is a synced full-node on testnet10.

```angular2html
git clone https://github.com/chiadojo/mojodojo_duels
cd mojodojo-defi
python3 -m venv venv
. venv/bin/activate
python -m pip install -r requirements.txt
```

Starting Python (interactive mode) and importing functions.
Ensure you haven't changed directory from the previous block.
```angular2html
python3
from drivers import create_duel, accept_duel, finalise_duel
```

## Creating a Duel
### Parameters
payout_address : The string value of the TXCH payout address to be used. e.g "txch1d31.."  
random         : The random entropy to be used, e.g "hello123"  
wager          : The integer wager in XCH to be committed to the smart coin, e.g 0.1  
fee (optional) : The transactional network fee to be used, default for testnet = 1000000000

### Usage
```angular2html
>>> create_duel("txch1u3dtz4t03ea8jzez6uq5xrgk5qvp4wsevtmtq07wv0ty3zrpdplq87wwa7", "sd97a98s67a8", 0.1)
```
Response:
```Generated preimage: 945b0365661c355034708afb89204ae33517bc33a1bad99a437300b0e41e61c7
Creating spend transaction...
Successfully created coin, printing JSON:
{"coinid": "1db6bfecabce2f82741197d2185b0ba7c1109d9cd606f720097319ff0f1c486c", "coin_parent": "2ebfc01c428e4534b3511a9c8babd539cd37cb45e35801312c1d9608675871ee", "coin_puzzlehash": "1ff86512622362be2d685f371b01e254ec5dbcef3afd49b41372a3f56e525547", "coin_amount": 102000000000, "puzzlehash": "e45ab1556f8e7a790b22d701430d16a0181aba1962f6b03fce63d6488861687e", "hashed_preimage": "1efee26f44f547e6de8b875248f4d35a278171fab46c98ec47a6be6b8253714e", "amount": 100000000000.0, "tx_fee": 1000000000}
```
The final line of this starting {"coinid... can now be shared with the user you want to duel against.

## Accepting a duel
json_dict     : The JSON variable copied from the 
payout_address : The string value of the TXCH payout address to be used. e.g "txch1d31.."  
random         : The random entropy to be used, e.g "hello123"  

### Usage
```angular2html
>>> accept_duel({"coinid": "1db6bfecabce2f82741197d2185b0ba7c1109d9cd606f720097319ff0f1c486c", "coin_parent": "2ebfc01c428e4534b3511a9c8babd539cd37cb45e35801312c1d9608675871ee", "coin_puzzlehash": "1ff86512622362be2d685f371b01e254ec5dbcef3afd49b41372a3f56e525547", "coin_amount": 102000000000, "puzzlehash": "e45ab1556f8e7a790b22d701430d16a0181aba1962f6b03fce63d6488861687e", "hashed_preimage": "1efee26f44f547e6de8b875248f4d35a278171fab46c98ec47a6be6b8253714e", "amount": 100000000000.0, "tx_fee": 1000000000},
...             "txch1j6nsqq8faehtyd0ggqvrwzcgxv2vmyysywuuvwrq88n4nvkpq3pqkczlfs",
...             "as87d9a7s9d")
```
Response:
```
Generated preimage: 5529167a65018bf1315a6c8ac2a2658291a0552c6ad8225f81fa90789eb13075
Creating spend for duel...
Creating matching wager contribution...
Created match coin:
{'amount': 100000000000,
 'parent_coin_info': '0x6ceff4b0b68024ec65acc5717b9041b44304bb49b03cf343f1d5a67f8216b040',
 'puzzle_hash': '0x4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a'}
Broadcasting spend to network...
{'status': 'SUCCESS', 'success': True}
{'aggregated_signature': '0xc00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
 'coin_spends': [{'coin': {'amount': 102000000000,
                           'parent_coin_info': '0x2ebfc01c428e4534b3511a9c8babd539cd37cb45e35801312c1d9608675871ee',
                           'puzzle_hash': '0x1ff86512622362be2d685f371b01e254ec5dbcef3afd49b41372a3f56e525547'},
                  'puzzle_reveal': '0xff02ffff01ff02ffff01ff02ff2affff04ff02ffff04ff05ffff04ff0bffff04ff17ffff04ff2fffff04ff5fffff04ff81bfff808080808080808080ffff04ffff01ffffff02ff3304ff01ff0134ffff02ffff04ffff04ff28ffff04ffff02ff3affff04ff02ffff04ff05ffff04ffff02ff3effff04ff02ffff04ff0bff80808080ffff04ffff02ff3effff04ff02ffff04ff17ff80808080ffff04ffff02ff3effff04ff02ffff04ff2fff80808080ffff04ffff02ff3effff04ff02ffff04ff5fff80808080ffff04ffff02ff3effff04ff02ffff04ff81bfff80808080ff808080808080808080ffff04ffff10ffff01843b9aca00ffff12ffff0102ff2f8080ff80808080ffff04ffff04ff3cffff01ff843b9aca008080ff808080ff02ff2effff04ff02ffff04ff05ffff04ff81bfffff04ff5fffff04ff2fffff04ff17ffff04ff0bff808080808080808080ffff02ffff03ff05ffff01ff02ff16ffff04ff02ffff04ff0dffff04ffff0bff12ffff0bff14ff3880ffff0bff12ffff0bff12ffff0bff14ff2c80ff0980ffff0bff12ff0bffff0bff14ff8080808080ff8080808080ffff010b80ff0180ffff0bff12ffff0bff14ff1080ffff0bff12ffff0bff12ffff0bff14ff2c80ff0580ffff0bff12ffff02ff16ffff04ff02ffff04ff07ffff04ffff0bff14ff1480ff8080808080ffff0bff14ff8080808080ff02ffff03ffff07ff0580ffff01ff0bffff0102ffff02ff3effff04ff02ffff04ff09ff80808080ffff02ff3effff04ff02ffff04ff0dff8080808080ffff01ff0bffff0101ff058080ff0180ff018080ffff04ffff01a0931f88fd2cbc1f30a6d8f2a7707b7757ecc1fc7d92e3af745d42e760ca09a66effff04ffff01a0e45ab1556f8e7a790b22d701430d16a0181aba1962f6b03fce63d6488861687effff04ffff01a01efee26f44f547e6de8b875248f4d35a278171fab46c98ec47a6be6b8253714effff04ffff0185174876e800ff018080808080',
                  'solution': '0xffa096a70000e9ee6eb235e84018370b083314cd909023b9c6386039e759b2c10442ffa05529167a65018bf1315a6c8ac2a2658291a0552c6ad8225f81fa90789eb1307580'},
                 {'coin': {'amount': 100000000000,
                           'parent_coin_info': '0x6ceff4b0b68024ec65acc5717b9041b44304bb49b03cf343f1d5a67f8216b040',
                           'puzzle_hash': '0x4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a'},
                  'puzzle_reveal': '0x80',
                  'solution': '0x80'}]}
```

## Finalising a duel
As the blockchain still does not know the preimage of the maker, the player who created the duel is required to `finalise` the duel by submitting their preimage again.

### Usage
random         : The random entropy used to create the duel
json_dict     : The JSON string generated when creating the duel

```angular2html
>>> finalise_duel("sd97a98s67a8", {"coinid": "1db6bfecabce2f82741197d2185b0ba7c1109d9cd606f720097319ff0f1c486c", "coin_parent": "2ebfc01c428e4534b3511a9c8babd539cd37cb45e35801312c1d9608675871ee", "coin_puzzlehash": "1ff86512622362be2d685f371b01e254ec5dbcef3afd49b41372a3f56e525547", "coin_amount": 102000000000, "puzzlehash": "e45ab1556f8e7a790b22d701430d16a0181aba1962f6b03fce63d6488861687e", "hashed_preimage": "1efee26f44f547e6de8b875248f4d35a278171fab46c98ec47a6be6b8253714e", "amount": 100000000000.0, "tx_fee": 1000000000}
... )
```
Response:
```
Coin soln: {'puzzlehash': '96a70000e9ee6eb235e84018370b083314cd909023b9c6386039e759b2c10442', 'preimage': '5529167a65018bf1315a6c8ac2a2658291a0552c6ad8225f81fa90789eb13075'}
player1 calculated puzzlehash dbc0a8c26778d486e7614419aa075798aec02925392c2a959477fb9496a12a36
Used coin value: 101000000000.0
Coin has been accepted, response id: fa7927f61d21c5ebc4febc845092c3bbb983e4fe1b2aaa2d391908f598df76ac
{'status': 'SUCCESS', 'success': True}
Submitted the preimage, new coin:
CoinSpend(coin=Coin(parent_coin_info=<bytes32: 1db6bfecabce2f82741197d2185b0ba7c1109d9cd606f720097319ff0f1c486c>, puzzle_hash=<bytes32: dbc0a8c26778d486e7614419aa075798aec02925392c2a959477fb9496a12a36>, amount=201000000000), puzzle_reveal=SerializedProgram(ff02ffff01ff02ffff01ff02ffff03ffff09ffff0bff81bf80ff0b80ffff01ff02ff0effff04ff02ffff04ff05ffff04ff81bfffff04ff2fffff04ff5fffff04ff17ff8080808080808080ffff01ff08ffff01a75072652d696d61676520646f6573206e6f74206d6174636820737570706c6965642068617368218080ff0180ffff04ffff01ffff3334ffff06ffff14ffff17ffff1aff05ff0b80ffff0182ff1480ffff018227108080ff02ffff03ffff15ffff02ff0affff04ff02ffff04ff0bffff04ff2fff8080808080ffff0182138880ffff01ff04ffff04ff08ffff04ff05ffff04ffff12ffff0102ff5f80ff80808080ffff04ffff04ff0cffff01ff843b9aca008080ff808080ffff01ff04ffff04ff08ffff04ff17ffff04ffff12ffff0102ff5f80ff80808080ffff04ffff04ff0cffff01ff843b9aca008080ff80808080ff0180ff018080ffff04ffff01a0e45ab1556f8e7a790b22d701430d16a0181aba1962f6b03fce63d6488861687effff04ffff01a01efee26f44f547e6de8b875248f4d35a278171fab46c98ec47a6be6b8253714effff04ffff0185174876e800ffff04ffff01a096a70000e9ee6eb235e84018370b083314cd909023b9c6386039e759b2c10442ffff04ffff01a05529167a65018bf1315a6c8ac2a2658291a0552c6ad8225f81fa90789eb13075ff01808080808080), solution=SerializedProgram(ffa0945b0365661c355034708afb89204ae33517bc33a1bad99a437300b0e41e61c780))
```
