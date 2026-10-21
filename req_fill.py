import os, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
CORN=['tt','ss','ff','sf','fs']; VDDS=['1.62','1.8','1.98']; TMPS=['-20','27','85']
OUT='results_package'; os.makedirs(OUT,exist_ok=True)
def load(path):
    if not os.path.exists(path): return pd.DataFrame()
    rows,cur=[],{}
    for line in open(path):
        p=line.split()
        if len(p)<3 or p[0] not in ('pw','f3','f90','pk','g'): continue
        if p[0]=='pw': cur={}
        try: cur[p[0]]=float(p[2])
        except ValueError: continue
        if p[0]=='g' and len(cur)==5: rows.append(cur)
    d=pd.DataFrame(rows)
    if len(d)==0: return d
    u=(d.f3/d.f90)**2
    d['Q']=1/np.sqrt((2-(1-u)**2)/u); d['rip']=d.pk-d.g
    return d.replace([np.inf,-np.inf],np.nan).dropna()
if os.path.exists('curves_ac_nom.txt'):
    a=np.loadtxt('curves_ac_nom.txt'); f=a[:,0]; m=a[:,1]; ph=a[:,3]
    if abs(ph).max()<7: ph=np.degrees(ph)
    fig,ax=plt.subplots(2,1,figsize=(3.6,4),sharex=True)
    ax[0].semilogx(f/1e6,m); ax[0].axhline(-3,ls=':',c='k'); ax[0].axvline(1.6,ls=':',c='g'); ax[0].set_ylabel('magnitude (dB)')
    ax[1].semilogx(f/1e6,ph); ax[1].axhline(-90,ls=':',c='k'); ax[1].set_ylabel('phase (deg)'); ax[1].set_xlabel('frequency (MHz)')
    fig.tight_layout(); fig.savefig(OUT+'/fig5_nominal_ac.png',dpi=300); plt.close(fig); print('wrote fig5_nominal_ac.png')
else: print('NO curves_ac_nom.txt')
G={}
for c in CORN:
    for v in VDDS:
        for t in TMPS:
            d=load('results_pt_%s_%s_%s.txt'%(c,v,t))
            if len(d)>2: G[(c,v,t)]=d
print('PTAT conditions loaded:',len(G))
nom=load('results_pt_s2_tt_1.8_27.txt')
if len(nom)<3: nom=G[('tt','1.8','27')]
worst=load('results_pt_s2_sf_1.62_-20.txt')
if len(worst)<3: worst=G[('sf','1.62','-20')]
fig,ax=plt.subplots(figsize=(3.6,2.8))
ax.hist(nom.rip,40,alpha=.6,label='PTAT tt 1.8 V 27 C (n=%d)'%len(nom))
ax.hist(worst.rip,40,alpha=.6,label='PTAT sf 1.62 V -20 C (n=%d)'%len(worst))
ax.set_xlabel('passband ripple / peaking (dB)'); ax.set_ylabel('runs'); ax.legend(fontsize=6)
fig.tight_layout(); fig.savefig(OUT+'/fig6_ripple_hist.png',dpi=300); plt.close(fig); print('wrote fig6_ripple_hist.png')
def s(d): return dict(f3_mean_MHz=d.f3.mean()/1e6,f3_sd_pct=100*d.f3.std()/d.f3.mean(),Q_mean=d.Q.mean(),Q_sd=d.Q.std(),rip_mean_dB=d.rip.mean(),rip_sd_dB=d.rip.std(),rip_max_dB=d.rip.max())
T=pd.DataFrame({'nominal tt 1.8V 27C':s(nom),'worst sf 1.62V -20C':s(worst)}).T.round(4)
allr=pd.concat(G.values())
cm=pd.DataFrame({k:dict(f3=d.f3.mean()/1e6,Q=d.Q.mean(),rip=d.rip.mean()) for k,d in G.items()}).T
ext=dict(f3_cond_mean_min=cm.f3.min(),f3_cond_mean_max=cm.f3.max(),Q_cond_mean_min=cm.Q.min(),Q_cond_mean_max=cm.Q.max(),rip_cond_mean_min=cm.rip.min(),rip_cond_mean_max=cm.rip.max(),f3_run_min=allr.f3.min()/1e6,f3_run_max=allr.f3.max()/1e6,Q_run_min=allr.Q.min(),Q_run_max=allr.Q.max(),rip_run_min=allr.rip.min(),rip_run_max=allr.rip.max(),runs=len(allr))
E=pd.Series(ext).round(4)
T.to_csv(OUT+'/table_TI_stats.csv'); E.to_csv(OUT+'/table_TI_extremes.csv')
with open(OUT+'/table_TI.md','w') as fh: fh.write(T.to_string()+'\n\n'+E.to_string()+'\n')
print(open(OUT+'/table_TI.md').read())
print('worst-ripple condition (mean):',cm.rip.idxmax(),round(cm.rip.max(),4))
try:
    n=np.loadtxt('curves_noise_pt.txt'); f=n[:,0]; on=n[:,1]
    print('NOISE first rows:',n[:2,:].tolist(),' last row:',n[-1,:].tolist())
    print('NOISE integral of col2 over f, sqrt = %.2f uV'%(1e6*np.sqrt(np.trapezoid(on,f) if hasattr(np,'trapezoid') else np.trapz(on,f))))
except Exception as e: print('NOISE skipped:',e)
