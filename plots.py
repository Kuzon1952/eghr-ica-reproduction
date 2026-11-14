# Plots for the EGHR reproduction (Isomura & Toyoizumi, Sci. Rep. 6, 28073 (2016))
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)
N, T = 2, 200_000
s = rng.laplace(0, 1/np.sqrt(2), size=(N, T))
A = rng.normal(size=(N, N))
x = A @ s

W = rng.normal(scale=0.3, size=(N, N))
W_start = W.copy()
E0, eta, batch = 3.0, 2e-3, 100

def separation_error(W):
    """0 when each output follows exactly one source."""
    C = np.abs(np.corrcoef(np.vstack([s[:, :5000], W @ x[:, :5000]]))[:N, N:])
    return 1 - C.max(axis=1).mean()

steps, errors = [], []
for k, t in enumerate(range(0, T, batch)):
    xb = x[:, t:t+batch]
    u = W @ xb
    E = np.sqrt(2) * np.abs(u).sum(axis=0)
    g = np.sqrt(2) * np.sign(u)
    W += eta * ((E0 - E) * g) @ xb.T / batch
    if k % 20 == 0:
        steps.append(t)
        errors.append(separation_error(W))

u_start, u_end = W_start @ x, W @ x

# Figure 1: the three signals over time
fig, ax = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
for a, data, title in zip(ax, [s, x, u_end], ["Hidden sources s", "Mixed inputs x", "Network outputs u after learning"]):
    a.plot(data[0, :200], lw=1)
    a.plot(data[1, :200], lw=1)
    a.set_title(title, loc="left")
ax[-1].set_xlabel("time step")
fig.tight_layout()
fig.savefig("fig1_signals.png", dpi=150)

# Figure 2: outputs before and after learning
fig, ax = plt.subplots(1, 2, figsize=(8, 4), sharex=True, sharey=True)
for a, data, title in zip(ax, [u_start, u_end], ["Before learning", "After learning"]):
    a.scatter(data[0, :5000], data[1, :5000], s=2, alpha=0.3)
    a.set_title(title)
    a.set_xlabel("output u1")
    a.set_aspect("equal")
ax[0].set_ylabel("output u2")
fig.tight_layout()
fig.savefig("fig2_outputs.png", dpi=150)

# Figure 3: learning curve
fig, ax = plt.subplots(figsize=(6, 4))
ax.semilogy(steps, errors)
ax.set_xlabel("samples seen")
ax.set_ylabel("separation error (1 - correlation)")
ax.set_title("Learning curve")
fig.tight_layout()
fig.savefig("fig3_learning_curve.png", dpi=150)

print("Saved fig1_signals.png, fig2_outputs.png, fig3_learning_curve.png")