import numpy as np
from PIL import Image
from lsb import LSB

arr = np.array(Image.open("img/gradient.png").convert("RGB"))
flat = arr.reshape(-1)

msg = b"hello, world"
bits = np.unpackbits(np.frombuffer(len(msg).to_bytes(4, "big") + msg, dtype=np.uint8))

if bits.size > flat.size:
    print(f"не помещается: нужно {bits.size}, есть {flat.size}")
    exit()

op = LSB(0)
for i in range(bits.size):
    op.state = int(flat[i])
    flat[i] = op.bits(int(bits[i]))

length = int.from_bytes(np.packbits(flat[:32] & 1).tobytes(), "big")
ext = np.packbits(flat[:32 + length * 8] & 1).tobytes()[4:]

print("текст:", msg.decode())
print("извлечение:", ext.decode())