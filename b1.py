import os, glob, numpy as np, pandas as pd
TGT, TOL, QLO, QHI = 1.6e6, 0.10, 0.6, 0.8
CORN, VDDS, TMPS = ['tt','ss','ff','sf','fs'], ['1.62','1.8','1.98'], ['-20','27','85']
OUT = 'results_package'; os.makedirs(OUT, exist_ok=True)
def load(path):
    if not os.path.exists(path): return pd.DataFrame()
    rows, cur = [], {}
    for line in open(path):
        p = line.split()
        if len(p) < 3 or p[0] not in ('pw','f3','f90','pk','g'): continue
        if p[0] == 'pw': cur = {}
        try: cur[p[0]] = float(p[2])
        except ValueError: continue
        if p[0] == 'g' and len(cur) == 5: rows.append(cur)
    d = pd.DataFrame(rows)
    if len(d) == 0: return d
    u = (d.f3/d.f90)**2
    d['Q'] = 1/np.sqrt((2-(1-u)**2)/u); d['rip'] = d.pk-d.g
    return d.replace([np.inf,-np.inf],np.nan).dropna()
def st(d):
    ok = (abs(d.f3/TGT-1) <= TOL) & (d.Q >= QLO) & (d.Q <= QHI)
    m = d.f3.mean()
    return dict(n=len(d), f3_MHz=m/1e6, f3_sd_pct=100*d.f3.std()/m, Q=d.Q.mean(), Q_sd=d.Q.std(), P_uW=d.pw.mean()*1e6, P_sd_pct=100*d.pw.std()/d.pw.mean(), ripple_dB=d.rip.mean(), yield_pct=100*ok.mean(), f3_in_pct=100*(abs(d.f3/TGT-1)<=TOL).mean())
def grid(pfx):
    R = []
    for c in CORN:
        for v in VDDS:
            for t in TMPS:
                d = load('results_%s_%s_%s_%s.txt' % (pfx,c,v,t))
                if len(d) > 2:
                    r = st(d); r.update(design=pfx, corner=c, VDD=v, T=t); R.append(r)
    return pd.DataFrame(R)
g, p = grid('g'), grid('pt')
al = pd.concat([g, p]); al['design'] = al.design.map({'g':'voltage','pt':'PTAT'})
al.round(4).to_csv(OUT+'/table_all_conditions.csv', index=False)
def summ(df):
    return pd.Series(dict(conditions=len(df), runs=df.n.sum(), mean_yield=df.yield_pct.mean(), min_yield=df.yield_pct.min(), worst_f3_shift_MHz=(df.f3_MHz-1.6).abs().max(), mean_f3_sd_pct=df.f3_sd_pct.mean(), worst_f3_sd_pct=df.f3_sd_pct.max(), Q_min=df.Q.min(), Q_max=df.Q.max(), P_min_uW=df.P_uW.min(), P_max_uW=df.P_uW.max()))
S = al.groupby('design').apply(summ).round(3); S.to_csv(OUT+'/table_summary.csv')
C = al.groupby(['design','corner'])[['f3_MHz','f3_sd_pct','Q','P_uW','yield_pct']].mean().round(3); C.to_csv(OUT+'/table_by_corner.csv')
tt = al[(al.corner=='tt')&(al.VDD=='1.8')].pivot(index='T', columns='design', values=['f3_MHz','Q','P_uW','yield_pct']).round(3)
tt.to_csv(OUT+'/table_tt_temperature.csv')
ex = []
for fn, lab in [('results_pt_s2_tt_1.8_27','PTAT tt 1.8V 27C seed2 1500'),('results_pt_s2_sf_1.62_-20','PTAT sf 1.62V -20C seed2 1500'),('results_pt_tight_tt_1.8_27','PTAT tight 300'),('results_ptm_m1_tt_1.8_27','mirror x1 27C'),('results_ptm_m4_tt_1.8_27','mirror x4 27C'),('results_ptm_m16_tt_1.8_27','mirror x16 27C'),('results_ptm_m1_tt_1.8_-20','mirror x1 -20C'),('results_ptm_m4_tt_1.8_-20','mirror x4 -20C'),('results_ptm_m16_tt_1.8_-20','mirror x16 -20C')]:
    d = load(fn+'.txt')
    if len(d) > 2: r = st(d); r['set'] = lab; ex.append(r)
if ex: pd.DataFrame(ex).set_index('set').round(3).to_csv(OUT+'/table_extra_sets.csv')
with open(OUT+'/tables.md','w') as f:
    for name, df in [('Summary',S),('By corner',C),('tt 1.8 V vs temperature',tt)]:
        f.write('## %s\n\n%s\n\n' % (name, df.to_string()))
    if ex: f.write('## Extra sets\n\n%s\n' % pd.DataFrame(ex).set_index('set').round(3).to_string())
print(open(OUT+'/tables.md').read())
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
except ImportError:
    print('NO_MATPLOTLIB: run  pip install --user matplotlib  then rerun'); raise SystemExit
col = {'voltage':'#d98e04','PTAT':'#1f77b4'}
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
fig, ax = plt.subplots(1, 2, figsize=(7.2,3), sharey=True)
for a, dn in zip(ax, ['voltage','PTAT']):
    for c in CORN:
        s = al[(al.design==dn)&(al.corner==c)&(al.VDD=='1.8')].copy(); s['t']=s['T'].astype(float); s=s.sort_values('t')
        a.errorbar(s.t, s.f3_MHz, yerr=s.f3_MHz*s.f3_sd_pct/100, marker='o', ms=3, capsize=2, label=c)
    a.axhline(1.6, ls=':', c='k'); a.set_title(dn+' bias'); a.set_xlabel('temperature (°C)')
ax[0].set_ylabel('f3 (MHz), bars = ±1σ'); ax[1].legend(ncol=5, fontsize=7, loc='lower center')
fig.tight_layout(); fig.savefig(OUT+'/fig1_f3_vs_temperature.png', dpi=300); plt.close(fig)
fig, ax = plt.subplots(figsize=(3.5,2.8)); w = 0.38
for i, dn in enumerate(['voltage','PTAT']):
    y = [al[(al.design==dn)&(al.corner==c)].yield_pct.mean() for c in CORN]
    ax.bar(np.arange(5)+(i-0.5)*w, y, w, label=dn, color=col[dn])
ax.set_xticks(range(5)); ax.set_xticklabels(CORN); ax.set_ylabel('mean yield (%)'); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(OUT+'/fig2_yield_by_corner.png', dpi=300); plt.close(fig)
fig, ax = plt.subplots(1, 2, figsize=(7.2,2.8))
dg, dp = load('results_g_tt_1.8_27.txt'), load('results_pt_s2_tt_1.8_27.txt')
if len(dp) < 3: dp = load('results_pt_tt_1.8_27.txt')
for d, dn in [(dg,'voltage'),(dp,'PTAT')]:
    if len(d):
        ax[0].hist(d.f3/1e6, 30, alpha=.6, color=col[dn], label=dn); ax[1].hist(d.Q, 30, alpha=.6, color=col[dn], label=dn)
ax[0].axvspan(1.44, 1.76, color='g', alpha=.08); ax[0].set_xlabel('f3 (MHz)'); ax[1].set_xlabel('Q'); ax[1].axvspan(QLO, QHI, color='g', alpha=.08); ax[0].legend(fontsize=7)
fig.tight_layout(); fig.savefig(OUT+'/fig3_histograms_tt.png', dpi=300); plt.close(fig)
fig, ax = plt.subplots(figsize=(3.5,3))
for fn, lab in [('results_pt_s2_tt_1.8_27.txt','tt 27C'),('results_pt_s2_sf_1.62_-20.txt','sf 1.62V -20C')]:
    d = load(fn)
    if len(d): ax.scatter(d.f3/1e6, d.Q, s=3, alpha=.4, label=lab)
ax.add_patch(plt.Rectangle((1.44,QLO), .32, QHI-QLO, fill=False, ls=':')); ax.set_xlabel('f3 (MHz)'); ax.set_ylabel('Q'); ax.legend(fontsize=7, markerscale=3)
fig.tight_layout(); fig.savefig(OUT+'/fig4_f3_vs_Q.png', dpi=300); plt.close(fig)
print('FILES:', sorted(os.listdir(OUT)))
