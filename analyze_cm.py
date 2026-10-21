import re, math, os, sys
IREF=float(sys.argv[1])*1e-6 if len(sys.argv)>1 else 12e-6   # reference leg current (A), subtracted from current-mode power
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

def load(path):
    recs=[]; cur=None
    for line in open(path,errors='ignore'):
        m=re.match(r'^(pw|f3|f90|pk|g)\s*=\s*([-+0-9.eE]+)',line)
        if not m: continue
        k,v=m.group(1),float(m.group(2))
        if k=='pw':
            cur={'pw':v}; recs.append(cur)
        elif cur is not None: cur[k]=v
    ok=[r for r in recs if all(k in r for k in ('pw','f3','f90','pk'))]
    f3=np.array([r['f3'] for r in ok])/1e6
    f90=np.array([r['f90'] for r in ok])/1e6
    x=f3/f90; u=x*x; q=1/np.sqrt((2-(1-u)**2)/u)
    return f3,q,np.array([r['pw'] for r in ok])*1e6

def stats(f3,q,p):
    fix=np.mean((abs(f3-1.6)<=0.16)&(q>=0.6)&(q<=0.8))*100
    ctr=np.mean((abs(f3-f3.mean())<=0.1*f3.mean())&(q>=0.6)&(q<=0.8))*100
    return dict(n=len(f3),f3=f3.mean(),sd=f3.std()/f3.mean()*100,q=q.mean(),p=p.mean(),fix=fix,ctr=ctr)

def get(prefix,c,v,t):
    fn='results_%s_%s_%s_%s.txt'%(prefix,c,v,t)
    if not os.path.exists(fn): return None
    f3,q,p=load(fn)
    if prefix=='cm': p=p-IREF*float(v)*1e6   # core power, reference leg excluded
    return stats(f3,q,p)

rows=[]
print('P = core power (uW); current-mode P excludes the %.0f uA reference leg'%(IREF*1e6))
print('corner vdd   T |  VOLTAGE BIAS: f3   sd%   Q    P   yFix | CURRENT MODE: f3   sd%   Q    P   yFix yCtr')
conds=[(c,'1.8',t) for c in ['tt','ss','ff','sf','fs'] for t in ['-20','27','85']]+[('tt','1.62','27'),('tt','1.98','27')]
for c,v,t in conds:
    a=get('g',c,v,t); b=get('cm',c,v,t)
    rows.append((c,v,t,a,b))
    fa='%5.3f %5.2f %.3f %5.1f %5.1f'%(a['f3'],a['sd'],a['q'],a['p'],a['fix']) if a else ' '*30
    fb='%5.3f %5.2f %.3f %5.1f %5.1f %5.1f'%(b['f3'],b['sd'],b['q'],b['p'],b['fix'],b['ctr']) if b else 'missing'
    print('%-4s %-5s %4s | %s | %s'%(c,v,t,fa,fb))

def span(key,which):
    vals=[r[which][key] for r in rows if r[which] and r[1]=='1.8']
    return (min(vals),max(vals)) if vals else None
for key,name in (('f3','f3 MHz'),('p','power uW'),('q','Q')):
    for which,lab in ((3,'voltage bias'),(4,'current mode')):
        s=span(key,which)
        if s: print('%-9s %-13s min %.3f max %.3f ratio %.2f'%(name,lab,s[0],s[1],s[1]/s[0]))

# figure: f3 and power vs temperature per corner, both bias schemes
plt.style.use('dark_background')
fig,ax=plt.subplots(1,2,figsize=(12,4.5))
T=[-20,27,85]; cols=dict(tt='#4cc9f0',ss='#f72585',ff='#ffd166',sf='#80ed99',fs='#b8a1ff')
for c in cols:
    for which,ls in ((3,'--'),(4,'-')):
        for i,key in enumerate(('f3','p')):
            y=[next((r[which][key] for r in rows if r[0]==c and r[1]=='1.8' and r[2]==str(t) and r[which]),np.nan) for t in T]
            ax[i].plot(T,y,ls,marker='o',color=cols[c],label=c if which==4 else None)
ax[0].axhspan(1.44,1.76,color='#2d6a4f',alpha=.3); ax[0].set_ylabel('mean f3 (MHz)'); ax[1].set_ylabel('mean power (uW)')
for a in ax: a.set_xlabel('temperature (C)'); a.grid(alpha=.2)
ax[0].legend(title='solid = current-mode, dashed = voltage-bias',fontsize=8)
ax[0].set_title('f3 vs temperature (VDD 1.8 V)'); ax[1].set_title('power vs temperature')
plt.tight_layout(); plt.savefig('fig_cm_compare.png',dpi=150); print('saved fig_cm_compare.png')
