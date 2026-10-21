import re,numpy as np
def load(p):
    R=[];c=None
    for l in open(p,errors='ignore'):
        m=re.match(r'^(pw|f3|f90|pk|g)\s*=\s*([-+0-9.eE]+)',l)
        if not m: continue
        k,v=m.group(1),float(m.group(2))
        if k=='pw': c={'pw':v};R.append(c)
        elif c is not None: c[k]=v
    R=[r for r in R if all(k in r for k in('pw','f3','f90'))]
    f=np.array([r['f3'] for r in R])/1e6;f9=np.array([r['f90'] for r in R])/1e6
    u=(f/f9)**2;q=1/np.sqrt((2-(1-u)**2)/u)
    return f,q
fa,qa=load('results_pt_tt_1.8_27.txt'); fb,qb=load('results_pt_tight_tt_1.8_27.txt')
n=min(len(fb),300); fa,qa,fb,qb=fa[:n],qa[:n],fb[:n],qb[:n]
df=100*(fb-fa)/fa; dq=100*(qb-qa)/qa
print('runs compared: %d (same seed, same mismatch draws)'%n)
print('standard : f3 mean %.4f MHz sd %.3f %%   Q mean %.4f'%(fa.mean(),fa.std()/fa.mean()*100,qa.mean()))
print('tight/fine: f3 mean %.4f MHz sd %.3f %%   Q mean %.4f'%(fb.mean(),fb.std()/fb.mean()*100,qb.mean()))
print('per-run f3 difference: mean %+.4f %%  sd %.4f %%  max |d| %.4f %%'%(df.mean(),df.std(),abs(df).max()))
print('per-run Q  difference: mean %+.4f %%  sd %.4f %%  max |d| %.4f %%'%(dq.mean(),dq.std(),abs(dq).max()))
y=lambda f,q:np.mean((abs(f-1.6)<=0.16)&(q>=0.6)&(q<=0.8))*100
print('fixed-spec yield: standard %.1f %%  tight %.1f %%'%(y(fa,qa),y(fb,qb)))
