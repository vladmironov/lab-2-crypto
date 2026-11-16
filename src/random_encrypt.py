import hashlib
import numpy as np
from PIL import Image
from aes import aes_ctr_encrypt
from lsb import LSB

password = b"myPassword"
key = hashlib.sha256(password).digest()[:16]

arr = np.array(Image.open("img/gradient.png").convert("RGB"))
flat = arr.reshape(-1)

msg = b"hello, world"
ct, nonce = aes_ctr_encrypt(msg, key)

p = len(ct).to_bytes(4, "big") + nonce + ct
bits = np.unpackbits(np.frombuffer(p, dtype=np.uint8))
seed = int.from_bytes(hashlib.sha256(password).digest()[:8], "big")
idx = np.random.default_rng(seed).permutation(flat.size)

if bits.size > flat.size:
    print(f"Не помещается: нужно {bits.size}, есть {flat.size}")
    exit()

op = LSB(0)
for i in range(bits.size):
    op.state = int(flat[idx[i]])
    flat[idx[i]] = op.bits(int(bits[i]))

Image.fromarray(flat.reshape(arr.shape)).save("stego_rnd.png")

flat = np.array(Image.open("stego_rnd.png").convert("RGB")).reshape(-1)
length = int.from_bytes(np.packbits(flat[idx[:32]] & 1).tobytes(), "big")
bytes = 4 + 8 + length
pl = np.packbits(flat[idx[:bytes * 8]] & 1).tobytes()

nonce = pl[4:12]
ct = pl[12:]