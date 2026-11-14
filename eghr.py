# Reproduction of eq. 1 in Isomura & Toyoizumi, Sci. Rep. 6, 28073 (2016), https://doi.org/10.1038/srep28073

import numpy as np
rng = np.random.default_rng(0)

N, T = 2, 200_000
s = rng.laplace(0, 1/np.sqrt(2), size=(N, T))   # two hidden sources
A = rng.normal(size=(N, N))                      # unknown mixing
x = A @ s                                        # what the network sees

W = rng.normal(scale=0.3, size=(N, N))           # weights to learn
E0, eta, batch = 3.0, 2e-3, 100

for t in range(0, T, batch):
    xb = x[:, t:t+batch]
    u = W @ xb
    E = np.sqrt(2) * np.abs(u).sum(axis=0)       # surprise, one number per sample
    g = np.sqrt(2) * np.sign(u)                  # per-neuron factor
    W += eta * ((E0 - E) * g) @ xb.T / batch     # equation 1

u = W @ x
print(np.abs(np.corrcoef(np.vstack([s, u]))[:N, N:]).round(3))