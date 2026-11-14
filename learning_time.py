# How many samples does the EGHR need, as the mixture gets harder?
# (EGHR: Isomura & Toyoizumi, Sci. Rep. 6, 28073 (2016), https://doi.org/10.1038/srep28073)
import numpy as np
import matplotlib.pyplot as plt

N = 2
E0, eta, batch = 3.0, 1e-2, 100
CHUNK, MAX_SAMPLES, TARGET = 10_000, 30_000_000, 1e-3
KAPPAS = [1, 2, 4, 8, 16, 32]      # condition numbers to test
SEEDS = 10                         # random repeats per condition number

def rotation(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s], [s, c]])

def separation_error(W, A):
    """Exact error from the matrices: 0 when each output follows one source."""
    P = np.abs(W @ A)
    P = P / np.linalg.norm(P, axis=1, keepdims=True)
    return 1 - P.max(axis=0).mean()

def samples_needed(kappa, seed):
    rng = np.random.default_rng(seed)
    # mixing matrix with exactly this condition number, random orientation
    A = rotation(rng.uniform(0, 2*np.pi)) @ np.diag([np.sqrt(kappa), 1/np.sqrt(kappa)]) @ rotation(rng.uniform(0, 2*np.pi))
    W = rng.normal(scale=0.3, size=(N, N))
    seen = 0
    while seen < MAX_SAMPLES:
        x = A @ rng.laplace(0, 1/np.sqrt(2), size=(N, CHUNK))
        for t in range(0, CHUNK, batch):
            xb = x[:, t:t+batch]
            u = W @ xb
            E = np.sqrt(2) * np.abs(u).sum(axis=0)
            g = np.sqrt(2) * np.sign(u)
            W += eta * ((E0 - E) * g) @ xb.T / batch
        seen += CHUNK
        if separation_error(W, A) < TARGET:
            return seen
    return np.nan                  # did not reach the target in time

results = np.array([[samples_needed(k, seed) for seed in range(SEEDS)] for k in KAPPAS])
for k, row in zip(KAPPAS, results):
    print(f"cond {k:3d}: samples needed {row}  median {np.nanmedian(row):.2e}")

fig, ax = plt.subplots(figsize=(6, 4))
for k, row in zip(KAPPAS, results):
    ax.loglog([k] * SEEDS, row, "o", color="tab:blue", alpha=0.5)
ax.loglog(KAPPAS, np.nanmedian(results, axis=1), "-", color="tab:blue", label="median of 10 runs")
ax.set_xlabel("condition number of the mixing matrix A")
ax.set_ylabel(f"samples needed to reach error {TARGET}")
ax.set_title("EGHR learning time vs. difficulty of the mixture")
ax.legend()
fig.tight_layout()
fig.savefig("fig5_learning_time.png", dpi=150)
print("Saved fig5_learning_time.png")