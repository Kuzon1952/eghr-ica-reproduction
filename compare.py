# EGHR vs FastICA on 20 random mixing matrices
# (EGHR: Isomura & Toyoizumi, Sci. Rep. 6, 28073 (2016), https://doi.org/10.1038/srep28073)
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import FastICA

N, T, TRIALS = 2, 2_000_000, 20
E0, eta, batch = 3.0, 1e-2, 100

def separation_error(s, u):
    """0 when each output follows exactly one source."""
    C = np.abs(np.corrcoef(np.vstack([s, u]))[:N, N:])
    return 1 - C.max(axis=1).mean()

def eghr(x, rng):
    W = rng.normal(scale=0.3, size=(N, N))
    for t in range(0, T, batch):
        xb = x[:, t:t+batch]
        u = W @ xb
        E = np.sqrt(2) * np.abs(u).sum(axis=0)
        g = np.sqrt(2) * np.sign(u)
        W += eta * ((E0 - E) * g) @ xb.T / batch
    return W @ x

cond, err_eghr, err_fast = [], [], []
for trial in range(TRIALS):
    rng = np.random.default_rng(trial)
    s = rng.laplace(0, 1/np.sqrt(2), size=(N, T))
    A = rng.normal(size=(N, N))
    x = A @ s
    cond.append(np.linalg.cond(A))          # how hard the mixture is: 1 = easy, large = nearly identical inputs
    err_eghr.append(separation_error(s, eghr(x, rng)))
    u_fast = FastICA(n_components=N, random_state=trial).fit_transform(x.T).T
    err_fast.append(separation_error(s, u_fast))
    print(f"trial {trial:2d}  cond(A) {cond[-1]:5.1f}  EGHR {err_eghr[-1]:.2e}  FastICA {err_fast[-1]:.2e}")

print(f"\nmedian error  EGHR {np.median(err_eghr):.2e}  FastICA {np.median(err_fast):.2e}")
print(f"EGHR trials with error below 0.01: {np.sum(np.array(err_eghr) < 0.01)} of {TRIALS}")

fig, ax = plt.subplots(figsize=(6, 4))
ax.loglog(cond, err_eghr, "o", label="EGHR (local rule)")
ax.loglog(cond, err_fast, "s", label="FastICA (standard method)")
ax.set_xlabel("condition number of the mixing matrix A")
ax.set_ylabel("separation error (1 - correlation)")
ax.set_title("EGHR vs FastICA, 20 random mixtures, 2 million samples")
ax.legend(loc="upper left")
fig.tight_layout()
fig.savefig("fig4_comparison.png", dpi=150)
print("Saved fig4_comparison.png")