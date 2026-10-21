import re,os,math,numpy as np
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
def yfix(f,q,tol=0.10): return np.mean((abs(f-1.6)<=1.6*tol)&(q>=0.6)&(q<=0.8))*100
def yctr(f,q,tol=0.10): return np.mean((abs(f-f.mean())<=tol*f.mean())&(q>=0.6)&(q<=0.8))*100
def row(lab,f,q):
    y=yfix(f,q); ci=1.96*math.sqrt(max(y*(100-y),0)/len(f))
    print('%-22s n=%4d  f3 %.3f  sd %.2f%%  Q %.3f  yFix %5.1f +/-%.1f  yCtr %5.1f'%(lab,len(f),f.mean(),f.std()/f.mean()*100,q.mean(),y,ci,yctr(f,q)))
print('PART 1: seed reproducibility (95% binomial CI on yFix)')
for c,v,t in (('tt','1.8','27'),('sf','1.62','-20')):
    a='results_pt_%s_%s_%s.txt'%(c,v,t); b='results_pt_s2_%s_%s_%s.txt'%(c,v,t)
    if os.path.exists(a):
        f,q=load(a); row('%s %s %sC seed1'%(c,v,t),f,q)
    if os.path.exists(b):
        f2,q2=load(b); n=len(f2)
        row('%s %s %sC seed2 all'%(c,v,t),f2,q2)
        if n>=1500:
            row('   seed2 first 750',f2[:750],q2[:750]); row('   seed2 last 750',f2[750:1500],q2[750:1500])
            if os.path.exists(a):
                fa,qa=load(a); row('   pooled 2250',np.concatenate([fa,f2]),np.concatenate([qa,q2]))
    else: print('   (missing %s)'%b)
print('\nPART 2: yield vs f3 tolerance window (Q window 0.6-0.8 kept), 45 PVT conditions, 750 runs each')
data={}
for c in ('tt','ss','ff','sf','fs'):
    for v in ('1.62','1.8','1.98'):
        for t in ('-20','27','85'):
            p='results_pt_%s_%s_%s.txt'%(c,v,t)
            if os.path.exists(p): data[(c,v,t)]=load(p)
print('conditions loaded: %d'%len(data))
print('tol    |  fixed spec (window on 1.6 MHz)          |  re-centred (window on own mean)')
print('       |  mean   min   >=90%%  >=80%% | tt/1.8/27 |  mean   min   >=90%%')
for tol in (0.05,0.10,0.15,0.20,0.25):
    Y=[yfix(f,q,tol) for f,q in data.values()]; C=[yctr(f,q,tol) for f,q in data.values()]
    f0,q0=data[('tt','1.8','27')]
    print('+/-%2d%% | %5.1f %5.1f   %2d     %2d   |  %5.1f    | %5.1f %5.1f   %2d'%(tol*100,np.mean(Y),min(Y),sum(y>=90 for y in Y),sum(y>=80 for y in Y),yfix(f0,q0,tol),np.mean(C),min(C),sum(y>=90 for y in C)))
