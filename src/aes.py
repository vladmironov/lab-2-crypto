from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def aes_ctr_encrypt(plain: bytes, key: bytes):
    nonce = get_random_bytes(8) # 8 байт nonce
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    ciphertext = cipher.encrypt(plain)
    return ciphertext, nonce

def aes_ctr_decrypt(ciphertext: bytes, key: bytes, nonce: bytes):
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    return cipher.decrypt(ciphertext)