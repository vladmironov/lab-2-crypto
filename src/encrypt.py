import hashlib
import numpy as np
from PIL import Image
from aes import aes_ctr_encrypt, aes_ctr_decrypt
from lsb import LSB

password = b"myPassword"
key = hashlib.sha256(password).digest()[:16]

arr = np.array(Image.open("img/gradient.png").convert("RGB"))
flat = arr.reshape(-1)

msg = b"hello, world"
ct, nonce = aes_ctr_encrypt(msg, key)

p = len(ct).to_bytes(4, "big") + nonce + ct
bits = np.unpackbits(np.frombuffer(p, dtype=np.uint8))

if bits.size > flat.size:
    print(f"Не помещается: нужно {bits.size}, есть {flat.size}")
    exit()

op = LSB(0)
for i in range(bits.size):
    op.state = int(flat[i])
    flat[i] = op.bits(int(bits[i]))

Image.fromarray(flat.reshape(arr.shape)).save("stego_enc.png")