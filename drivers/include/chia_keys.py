from chia.util import keychain

from drivers.chia_utils import config

dat = keychain.Keychain()
print(dat)
pk = dat.get_all_public_keys()
print(pk)
privkey = dat.get_all_private_keys()
print(privkey)
# kr = dat.get_keyring()
# print(kr)
# fkr = kr.load_keyring()