import numpy as np
from scipy.stats import chi2
from skimage.metrics import structural_similarity
import matplotlib.pyplot as plt

def psnr(cv, st):
    mse = np.mean((cv.astype(float) - st.astype(float)) ** 2)
    return 10 * np.log10(255**2 / mse) if mse > 0 else float('inf')

def ssim(cv, st):
    return structural_similarity(cv, st, channel_axis=2, data_range=255)

def change(cv_bytes, st_bytes):
    a = np.frombuffer(cv_bytes, dtype=np.uint8)
    b = np.frombuffer(st_bytes, dtype=np.uint8)
    return int(np.sum(a != b)), float(np.mean(a != b))

def lsb_p1(data_bytes):
    arr = np.frombuffer(data_bytes, dtype=np.uint8)
    return float(np.mean(arr & 1))

def chi2(data_bytes):
    arr = np.frombuffer(data_bytes, dtype=np.uint8)
    counts = np.bincount(arr, minlength=256).reshape(128, 2)
    exp = counts.mean(axis=1)
    mask = exp > 0
    x2 = float(np.sum((counts[mask, 0] - exp[mask])**2 / exp[mask]))
    p_val = float(1 - chi2.cdf(x2, df=127))
    return x2, p_val

def save_histogram(cover_bytes, stego_bytes, filename):
    plt.figure(figsize=(10, 4))
    plt.hist(np.frombuffer(cover_bytes, np.uint8), bins=256, range=(0, 256), alpha=0.5, label="cov")
    plt.hist(np.frombuffer(stego_bytes, np.uint8), bins=256, range=(0, 256), alpha=0.5, label="stg")
    plt.legend()
    plt.savefig(filename)
    plt.close()

def save_diff_map(cover_arr, stego_arr, filename):
    diff = np.abs(cover_arr.astype(np.int16) - stego_arr.astype(np.int16))
    vis = np.clip(diff * 20, 0, 255).astype(np.uint8)
    plt.imsave(filename, vis)