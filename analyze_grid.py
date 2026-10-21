import numpy as np, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
F0, FTOL, QLO, QHI = 1.6e6, 0.10, 0.6, 0.8
CORN = ['ss','tt','ff','sf','fs']; VDD = ['1.62','1.8','1.98']; TMP = ['-20','27','85']
def load(t):
    d = {'pw':[],'f3':[],'f90':[],'pk':[],'g':[]}
    for line in open('results_%s.txt' % t):
        p = line.split()
        if len(p) >= 3 and p[0] in d:
            d[p[0]].append(float(p[2]))
    d = {k: np.array(v) for k, v in d.items()}
    u = (d['f3']/d['f90'])**2
    d['Q'] = 1/np.sqrt((2-(1-u)**2)/u)
    d['rip'] = d['pk'] - d['g']
    return d
rows = []
S = {}
for c in CORN:
    for v in VDD:
        for t in TMP:
            d = load('g_%s_%s_%s' % (c, v, t))
            ok = (abs(d['f3']/F0-1) <= FTOL) & (d['Q'] >= QLO) & (d['Q'] <= QHI)
            m = d['f3'].mean()
            ok2 = (abs(d['f3']/m-1) <= FTOL) & (d['Q'] >= QLO) & (d['Q'] <= QHI)
            r = dict(corner=c, vdd=v, temp=t, n=len(d['f3']), f3_MHz=m/1e6, f3_sd_pct=100*d['f3'].std()/m, Q=np.nanmean(d['Q']), Q_sd=np.nanstd(d['Q']), ripple_dB=d['rip'].mean(), P_uW=d['pw'].mean()*1e6, yield_fixed=100*ok.mean(), yield_centered=100*ok2.mean())
            rows.append(r); S[(c, v, t)] = r
w = csv.DictWriter(open('grid_summary.csv', 'w'), fieldnames=list(rows[0].keys()))
w.writeheader(); w.writerows(rows)
print('corner vdd   T   n   f3MHz sd%  Q     P_uW  rip_dB yFix yCtr')
for r in rows:
    print('%-6s %-4s %-4s %d %.3f %.2f %.3f %.1f %.3f %5.1f %5.1f' % (r['corner'], r['vdd'], r['temp'], r['n'], r['f3_MHz'], r['f3_sd_pct'], r['Q'], r['P_uW'], r['ripple_dB'], r['yield_fixed'], r['yield_centered']))
lo = min(rows, key=lambda r: r['f3_MHz']); hi = max(rows, key=lambda r: r['f3_MHz'])
print('f3 min: %s %s %s %.3f MHz | max: %s %s %s %.3f MHz' % (lo['corner'], lo['vdd'], lo['temp'], lo['f3_MHz'], hi['corner'], hi['vdd'], hi['temp'], hi['f3_MHz']))
print('Q range: %.3f - %.3f | power range: %.1f - %.1f uW' % (min(r['Q'] for r in rows), max(r['Q'] for r in rows), min(r['P_uW'] for r in rows), max(r['P_uW'] for r in rows)))
def heat(key, fn, title, fmt):
    fig, ax = plt.subplots(1, 5, figsize=(15, 3.2), sharey=True)
    vals = [S[k][key] for k in S]
    for a, c in zip(ax, CORN):
        M = np.array([[S[(c, v, t)][key] for t in TMP] for v in VDD])
        a.imshow(M, vmin=min(vals), vmax=max(vals), cmap='viridis', aspect='auto')
        a.set_title(c); a.set_xticks(range(3)); a.set_xticklabels(TMP); a.set_xlabel('T (C)')
        for i in range(3):
            for j in range(3):
                a.text(j, i, fmt % M[i, j], ha='center', va='center', color='w', fontsize=8)
    ax[0].set_yticks(range(3)); ax[0].set_yticklabels(VDD); ax[0].set_ylabel('VDD (V)')
    fig.suptitle(title); plt.tight_layout(); plt.savefig(fn, dpi=200); plt.close()
heat('f3_MHz', 'fig_grid_f3.png', 'mean f3 (MHz)', '%.2f')
heat('Q', 'fig_grid_q.png', 'mean Q', '%.2f')
heat('P_uW', 'fig_grid_power.png', 'mean power (uW)', '%.0f')
heat('yield_fixed', 'fig_grid_yield.png', 'yield vs fixed spec (%)', '%.0f')
