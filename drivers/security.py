from blspy import PrivateKey, G1Element, AugSchemeMPL
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util import keychain

# from chia.consensus.default_constants import DEFAULT_CONSTANTS
# AGG_SIG_ME_ADDITIONAL_DATA = DEFAULT_CONSTANTS.GENESIS_CHALLENGE
AGG_SIG_ME_ADDITIONAL_DATA = bytes32.fromhex("ae83525ba8d1dd3f09b277de18ca3e43fc0af20d20c4b3e92ef2a48bd291ccb2")


class Security:

    def __init__(self, c_idx, gc_idx):
        k = keychain.Keychain()
        if k.is_keyring_locked():
            return "Error keyring is locked"
        master_sk: PrivateKey = k.get_all_private_keys()[0][0]
        child: PrivateKey = AugSchemeMPL.derive_child_sk(master_sk, c_idx)
        self.sk: PrivateKey = AugSchemeMPL.derive_child_sk(child, gc_idx)
        self.pk: G1Element = self.sk.get_g1()

    def get_pk(self) -> G1Element:
        return self.pk

    # Many obvious improvements here
    def sign_coin_and_message(self, message: bytes, coin_id: bytes):
        to_sign = message + coin_id + AGG_SIG_ME_ADDITIONAL_DATA
        signature = AugSchemeMPL.sign(self.sk, to_sign)
        return signature
