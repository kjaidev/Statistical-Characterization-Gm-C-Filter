import re, math, os, sys
IREF=float(sys.argv[1])*1e-6 if len(sys.argv)>1 else 12e-6   # reference leg current at 27C (A), subtracted from current-mode power
ALPHA=float(sys.argv[2]) if len(sys.argv)>2 else 0.6
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
    if prefix=='pt': p=p-IREF*(((float(t)+273.15)/300.15)**ALPHA)*float(v)*1e6
    return stats(f3,q,p)

rows=[]
print('P = core power (uW), reference leg excluded for cm/pt')
print('corner vdd   T |  VOLTAGE BIAS        | CURRENT MODE        | CURRENT MODE + PTAT ref')
print('                 |  f3    sd%   Q   yFix |  f3    sd%   Q   yFix |  f3    sd%   Q    P   yFix yCtr')
conds=[(c,'1.8',t) for c in ['tt','ss','ff','sf','fs'] for t in ['-20','27','85']]+[('tt','1.62','27'),('tt','1.98','27')]
def fmt(b,full=False):
    if not b: return 'missing'
    s='%5.3f %5.2f %.3f %5.1f'%(b['f3'],b['sd'],b['q'],b['fix'])
    return s if not full else '%5.3f %5.2f %.3f %5.1f %5.1f %5.1f'%(b['f3'],b['sd'],b['q'],b['p'],b['fix'],b['ctr'])
for c,v,t in conds:
    a=get('g',c,v,t); b=get('cm',c,v,t); d=get('pt',c,v,t)
    rows.append((c,v,t,a,b,d))
    print('%-4s %-5s %4s | %s | %s | %s'%(c,v,t,fmt(a),fmt(b),fmt(d,True)))
print()
names={3:'voltage bias',4:'current mode',5:'current + PTAT'}
for key,name in (('f3','f3 MHz'),('p','core power uW'),('q','Q')):
    for w in (3,4,5):
        vals=[r[w][key] for r in rows if r[w] and r[1]=='1.8']
        if vals: print('%-14s %-15s min %.3f max %.3f ratio %.2f'%(name,names[w],min(vals),max(vals),max(vals)/min(vals)))
for w in (3,4,5):
    ys=[r[w]['fix'] for r in rows if r[w] and r[1]=='1.8']
    if ys: print('fixed-spec yield %-15s mean %.1f%%  worst %.1f%%  conditions>=90%%: %d/%d'%(names[w],np.mean(ys),min(ys),sum(y>=90 for y in ys),len(ys)))
plt.style.use('dark_background')
fig,ax=plt.subplots(1,3,figsize=(16,4.5))
T=[-20,27,85]; cols=dict(tt='#4cc9f0',ss='#f72585',ff='#ffd166',sf='#80ed99',fs='#b8a1ff')
sty={3:':',4:'--',5:'-'}
for c in cols:
    for w in (3,4,5):
        for i,key in enumerate(('f3','p','fix')):
            y=[next((r[w][key] for r in rows if r[0]==c and r[1]=='1.8' and r[2]==str(t) and r[w]),np.nan) for t in T]
            ax[i].plot(T,y,sty[w],marker='o',color=cols[c],label=c if w==5 and i==0 else None)
ax[0].axhspan(1.44,1.76,color='#2d6a4f',alpha=.3)
ax[0].set_ylabel('mean f3 (MHz)'); ax[1].set_ylabel('mean core power (uW)'); ax[2].set_ylabel('yield, fixed spec (%)')
for a in ax: a.set_xlabel('temperature (C)'); a.grid(alpha=.2)
ax[0].legend(title='dotted=voltage, dashed=current, solid=PTAT',fontsize=8)
ax[0].set_title('f3 vs temperature (VDD 1.8 V)'); ax[1].set_title('core power'); ax[2].set_title('fixed-spec yield')
plt.tight_layout(); plt.savefig('fig_pt_compare.png',dpi=150); print('saved fig_pt_compare.png')
