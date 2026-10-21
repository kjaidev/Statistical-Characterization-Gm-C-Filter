import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
wl = np.array([0.5, 2, 8, 32]); sd = np.array([9.852, 3.991, 1.908, 0.904])
x = np.logspace(-0.4, 1.6, 50)
plt.figure(figsize=(5.5, 4))
plt.loglog(wl, sd, 'o', label='simulated sigma(dVgs)')
plt.loglog(x, np.sqrt(2)*3.356/np.sqrt(x), '--', label='hand-calc: sqrt(2)*A_VT/sqrt(WL), A_VT=3.356 mV.um')
plt.xlabel('WL (um^2)'); plt.ylabel('sigma (mV)'); plt.legend(fontsize=7); plt.grid(alpha=0.3, which='both')
plt.tight_layout(); plt.savefig('fig_pelgrom_handcalc.png', dpi=200)
