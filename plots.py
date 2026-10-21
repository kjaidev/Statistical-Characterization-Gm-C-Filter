import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyze import D, F0
def sv(n):
    plt.tight_layout(); plt.savefig(n, dpi=200); plt.close()
plt.figure(figsize=(6,4))
for t, c in [('ss','C3'),('nom','C0'),('ff','C2')]:
    plt.hist(D[t]['f3']/1e6, bins=30, alpha=0.6, color=c, label=t)
plt.xlabel('f3 (MHz)'); plt.ylabel('count'); plt.legend(); plt.title('f3 over corners, 500 MC runs each')
sv('fig_f3_corners.png')
fig, ax = plt.subplots(1, 3, figsize=(10,3.5))
ax[0].hist(D['nom']['f3']/1e6, bins=30); ax[0].set_xlabel('f3 (MHz)')
ax[1].hist(D['nom']['Q'], bins=30); ax[1].set_xlabel('Q')
ax[2].hist(D['nom']['pw']*1e6, bins=30); ax[2].set_xlabel('power (uW)')
sv('fig_nominal_hist.png')
def ms(ts, k, s=1.0):
    return [D[t][k].mean()*s for t in ts], [D[t][k].std()*s for t in ts]
fig, ax = plt.subplots(1, 3, figsize=(11,3.6), sharey=True)
for a, ts, xs, xl in [(ax[0], ['ss','nom','ff'], [0,1,2], 'corner'), (ax[1], ['v162','nom','v198'], [1.62,1.8,1.98], 'VDD (V)'), (ax[2], ['tm20','nom','t85'], [-20,27,85], 'temperature (C)')]:
    m, s = ms(ts, 'f3', 1e-6)
    a.errorbar(xs, m, yerr=s, marker='o', capsize=4); a.set_xlabel(xl); a.grid(alpha=0.3)
ax[0].set_ylabel('f3 (MHz)'); ax[0].set_xticks([0,1,2]); ax[0].set_xticklabels(['ss','tt','ff'])
sv('fig_pvt.png')
wl = np.array([0.5,2,8,32]); sd = np.array([9.852,3.991,1.908,0.904])
plt.figure(figsize=(5,4))
plt.loglog(wl, sd, 'o', label='simulated'); plt.loglog(wl, 5.4/np.sqrt(wl), '--', label='1/sqrt(WL)')
plt.xlabel('WL (um^2)'); plt.ylabel('sigma(dVgs) (mV)'); plt.legend(); plt.grid(alpha=0.3, which='both')
sv('fig_pelgrom.png')
x = np.loadtxt('tran_out.txt')
plt.figure(figsize=(6,3.5))
plt.plot(x[:,0]*1e9, x[:,1]*1e3); plt.xlabel('time (ns)'); plt.ylabel('vo2 (mV)'); plt.xlim(0,1500); plt.grid(alpha=0.3)
sv('fig_tran.png')
