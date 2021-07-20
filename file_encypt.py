import hashlib
from Crypto import Random
from Crypto.Cipher import AES


def key_encode(key_str):
    return hashlib.sha256(key_str.encode()).digest()


def create_cipher(key, iv=None):
    return AES.new(key, AES.MODE_CFB, iv)


def get_key_iv(key_str):
    key = key_encode(key_str)
    iv = Random.new().read(AES.block_size)
    return key, iv