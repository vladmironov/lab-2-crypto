import os
import hashlib
import numpy as np
from PIL import Image

from aes import aes_ctr_encrypt, aes_ctr_decrypt
from lsb import LSB
from metrics import psnr, ssim, change, lsb_p1, chi2, save_histogram, save_diff_map

import csv

os.makedirs("results", exist_ok=True)
os.makedirs("crypt", exist_ok=True)

pw = b"myPassword"
key = hashlib.sha256(pw).digest()[:16]

imgs = ["gradient.png", "noise_texture.png"]
fls = [0.01, 0.05]

with open("results/metrics.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(["Изображение", "fl", "Вариант", "PSNR", "SSIM", "Изм.", "P(LSB=1)", "Chi2", "df", "p-value"])

for n in imgs:
    img = np.array(Image.open(f"img/{n}").convert("RGB"))
    cb = img.tobytes()
    fc = img.reshape(-1)
    base = n.replace(".png", "")

    c1 = lsb_p1(cb)
    cx2, cp, cdf = chi2(cb)
    
    for fl in fls:
        target_bits = int(fc.size * fl)
        m_len = target_bits // 8 - 12
        if m_len <= 0: continue
        
        msg = (b"Hello world" * (m_len // 11 + 1))[:m_len]

        pp = len(msg).to_bytes(4, "big") + msg
        bp = np.unpackbits(np.frombuffer(pp, dtype=np.uint8))

        if bp.size > fc.size:
            print("Не помещается")
            exit()

        fp = fc.copy()
        op = LSB(0)
        for i in range(bp.size):
            op.state = int(fp[i])
            fp[i] = op.bits(int(bp[i]))

        spa = fp.reshape(img.shape)
        Image.fromarray(spa).save(f"crypt/{base}-{fl}_plain.png")

        ct, nonce = aes_ctr_encrypt(msg, key)
        pe = len(ct).to_bytes(4, "big") + nonce + ct
        be = np.unpackbits(np.frombuffer(pe, dtype=np.uint8))

        fe = fc.copy()
        op = LSB(0)
        for i in range(be.size):
            op.state = int(fe[i])
            fe[i] = op.bits(int(be[i]))

        sea = fe.reshape(img.shape)
        Image.fromarray(sea).save(f"crypt/{base}-{fl}_enc.png")

        sd = int.from_bytes(hashlib.sha256(pw).digest()[:8], "big")
        ix = np.random.default_rng(sd).permutation(fc.size)

        fr = fc.copy()
        op = LSB(0)
        for i in range(be.size):
            op.state = int(fr[ix[i]])
            fr[ix[i]] = op.bits(int(be[i]))

        sra = fr.reshape(img.shape)
        Image.fromarray(sra).save(f"crypt/{base}-{fl}_rnd.png")

        ft = spa.reshape(-1)
        ln = int.from_bytes(np.packbits(ft[:32] & 1).tobytes(), "big")
        xp = np.packbits(ft[:32 + ln * 8] & 1).tobytes()[4:]

        ft = sea.reshape(-1)
        ln = int.from_bytes(np.packbits(ft[:32] & 1).tobytes(), "big")
        pl = np.packbits(ft[:(4 + 8 + ln) * 8] & 1).tobytes()
        nx, cx = pl[4:12], pl[12:]
        xe = aes_ctr_decrypt(cx, key, nx)

        ft = sra.reshape(-1)
        ln = int.from_bytes(np.packbits(ft[ix[:32]] & 1).tobytes(), "big")
        pl = np.packbits(ft[ix[:(4 + 8 + ln) * 8]] & 1).tobytes()
        nx, cx = pl[4:12], pl[12:]
        xr = aes_ctr_decrypt(cx, key, nx)


        '''
        c1 = lsb_p1(cb)
        cx2, cp = chi2(cb)
        print(f"Cover\t|\t-\t|\t-\t|\t0\t|\t{round(c1, 4)}\t|\t{round(cx2, 3)}\t|\t{round(cp, 4)}")

        var = [
            ("Plain LSB", spa, "stego_plain.png"),
            ("Encrypted LSB", sea, "stego_enc.png"),
            ("Random LSB", sra, "stego_rnd.png")
        ]

        for n, sa, ip in var:
            sb = sa.tobytes()
            p = psnr(img, sa)
            s = ssim(img, sa)
            _, ch_r = change(cb, sb)
            l_p1 = lsb_p1(sb)
            x2, pv = chi2(sb)
            
            print(f"{n}\t|\t{round(p, 2)}\t|\t{round(s, 4)}\t|\t{round(ch_r, 4)}\t|\t{round(l_p1, 4)}\t|\t{round(x2, 3)}\t|\t{round(pv, 4)}")
            
            if n == "Plain LSB":
                save_diff_map(img, sa, "results/difference.png")
                save_histogram(cb, sb, "results/histogram.png")

        '''


        with open("results/metrics.csv", "a", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=';')

            c1 = lsb_p1(cb)
            cx2, cp, cdf = chi2(cb)

            var = [
                ("Plain LSB", spa, f"crypt/{base}_plain.png"),
                ("Encrypted LSB", sea, f"crypt/{base}_enc.png"),
                ("Random LSB", sra, f"crypt/{base}_rnd.png")
            ]

            for vn, sa, ip in var:
                sb = sa.tobytes()
                p = psnr(img, sa)
                s = ssim(img, sa)
                _, ch_r = change(cb, sb)
                l_p1 = lsb_p1(sb)
                x2, pv, df = chi2(sb)
                
                w.writerow([n, fl, vn, round(p, 2), round(s, 4), round(ch_r, 4), round(l_p1, 4), round(x2, 3), df, round(pv, 4)])
                
                if vn == "Plain LSB":
                    save_diff_map(img, sa, f"results/difference_{base}-{fl}.png")
                    save_histogram(cb, sb, f"results/histogram_{base}-{fl}.png")




