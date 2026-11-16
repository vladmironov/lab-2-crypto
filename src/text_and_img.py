import numpy as np
from PIL import Image
from lsb import LSB

arr = np.array(Image.open("img/gradient.png").convert("RGB"))
flat = arr.reshape(-1)

msg = b"hello, world"
bits = np.unpackbits(np.frombuffer(len(msg).to_bytes(4, "big") + msg, dtype=np.uint8))

if bits.size > flat.size:
    print(f"Не помещается: нужно {bits.size}, есть {flat.size}")
    exit()

op = LSB(0)
for i in range(bits.size):
    op.state = int(flat[i])
    flat[i] = op.bits(int(bits[i]))

Image.fromarray(flat.reshape(arr.shape)).save("stego.png")

flat = np.array(Image.open("stego.png").convert("RGB")).reshape(-1)
length = int.from_bytes(np.packbits(flat[:32] & 1).tobytes(), "big")
print(np.packbits(flat[:32 + length * 8] & 1).tobytes()[4:])