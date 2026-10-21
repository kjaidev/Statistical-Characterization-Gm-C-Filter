import re, subprocess, math, os
from math import erf, sqrt
D='/foss/designs/gmc-filter'; LIB='/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice'
os.chdir(D)
base=open('gmc_pt.spice').read()
def sim(iref,rt,alpha,T):
    t=re.sub(r'(?m)^\.lib .*',".lib %s tt"%LIB,base)
    t=re.sub(r'(?m)^V1 VDD 0 .*','V1 VDD 0 1.8',t)
    t=re.sub(r'(?m)^\.include .*','.include %s/a4.cir'%D,t)
    t=re.sub(r'(?m)^\.param .*','.param iref=%g rt=%g alpha=%g'%(iref,rt,alpha),t)
    L=t.split('\n'); L.insert(1,'.temp %d'%T); open('a7_net.spice','w').write('\n'.join(L))
    o=subprocess.run(['ngspice','-b','a7_net.spice'],capture_output=True,text=True).stdout
    a=re.search(r'^f3\s*=\s*([-+0-9.eE]+)',o,re.M); b=re.search(r'^f90\s*=\s*([-+0-9.eE]+)',o,re.M)
    if not(a and b): return None
    f3=float(a.group(1)); f90=float(b.group(1)); u=(f3/f90)**2
    return f3/1e6, 1/sqrt((2-(1-u)**2)/u)
SD={-20:(7.12,4.30),27:(5.91,3.68),85:(4.95,3.5)}
def phi(z): return 0.5*(1+erf(z/sqrt(2)))
def yest(f,q,T):
    sf,sq=SD[T]; sf=sf/100*f; sq=sq/100*q
    pf=phi((1.76-f)/sf)-phi((1.44-f)/sf); pq=phi((0.8-q)/sq)-phi((0.6-q)/sq)
    return 100*pf*pq
def table(title,cases):
    print('\n'+title)
    print('%-16s | %s'%('case','  -20C: f3    Q   yEst |   27C: f3    Q   yEst |   85C: f3    Q   yEst'))
    for lab,(ir,rt,al) in cases:
        cells=[]
        for T in (-20,27,85):
            r=sim(ir,rt,al,T)
            cells.append('%6.3f %.3f %5.1f'%(r[0],r[1],yest(r[0],r[1],T)) if r else '   failed        ')
        print('%-16s | %s | %s | %s'%(lab,*cells))
table('Reference current scale (both legs, ratio kept; alpha=0.6, rt=1.48)',[('Iref x%.2f'%s,(12e-6*s,1.48,0.6)) for s in (0.8,0.9,0.95,1.0,1.05,1.1,1.2)])
table('PTAT exponent alpha (Iref=12u, rt=1.48)',[('alpha %.1f'%a,(12e-6,1.48,a)) for a in (0.0,0.2,0.4,0.6,0.8,1.0)])
table('Leg ratio rt (Iref=12u, alpha=0.6)',[('rt %.3f (%+d%%)'%(1.48*(1+d/100),d),(12e-6,1.48*(1+d/100),0.6)) for d in (-10,-5,0,5,10)])
