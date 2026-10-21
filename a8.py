import re, subprocess, math, os
from math import sqrt, log, exp
D='/foss/designs/gmc-filter'; LIB='/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice'
os.chdir(D)
N='sky130_fd_pr__nfet_01v8'; P='sky130_fd_pr__pfet_01v8'
def ota(name,wt):
    return ['.subckt %s OUT1 IN1+ IN1- Vbias_tail'%name,
    'XM1 net2 IN1+ net1 0 %s L=0.5 W=4 nf=1 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0'%N,
    'XM2 OUT1 IN1- net1 0 %s L=0.5 W=4 nf=1 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0'%N,
    'XM3 net2 net2 VDD VDD %s L=0.5 W=8 nf=1 ad=2.32 as=2.32 pd=16.58 ps=16.58 nrd=0.03625 nrs=0.03625 sa=0 sb=0 sd=0'%P,
    'XM4 OUT1 net2 VDD VDD %s L=0.5 W=8 nf=1 ad=2.32 as=2.32 pd=16.58 ps=16.58 nrd=0.03625 nrs=0.03625 sa=0 sb=0 sd=0'%P,
    'XM5 net1 Vbias_tail 0 0 %s L=1 W=%g nf=1'%(N,wt),
    '.ends']
def parse(o):
    a=re.search(r'^f3\s*=\s*([-+0-9.eE]+)',o,re.M); b=re.search(r'^f90\s*=\s*([-+0-9.eE]+)',o,re.M)
    c=re.search(r'v1#branch\s*=\s*([-+0-9.eE]+)',o); d=re.search(r'^v\(a\)\s*=\s*([-+0-9.eE]+)',o,re.M)
    if not(a and b and c): return None
    f3=float(a.group(1)); f90=float(b.group(1)); u=(f3/f90)**2
    return f3/1e6, 1/sqrt((2-(1-u)**2)/u), -float(c.group(1)), (float(d.group(1)) if d else float('nan'))
def sim_cg(R,corner,vdd,T,K=4,rt=1.48):
    L=['cg bias','.GLOBAL VDD','Vinp vin 0 0.9 ac 1','V1 VDD 0 %g'%vdd,'Vinn vcm 0 0.9',
    'XMN1 a a 0 0 %s L=1 W=6 nf=1'%N,
    'XMN2 b a rs 0 %s L=1 W=%g nf=1'%(N,6*K),
    'RS rs 0 %g'%R,
    'XMP1 b b VDD VDD %s L=2 W=16 nf=1'%P,
    'XMP2 a b VDD VDD %s L=2 W=16 nf=1'%P,
    '.nodeset v(a)=0.7 v(b)=1.0',
    'C1 vo1 0 10p','C2 vo2 0 10p',
    'x1 vo1 vin vo2 a ota_a','x2 vo2 vo1 vcm a ota_a','x3 vo1 vcm vo1 a ota_b']
    L+=ota('ota_a',6)+ota('ota_b',6*rt)
    L+=['.lib %s %s'%(LIB,corner),'.temp %d'%T,'.control','op','print v1#branch v(a)','ac dec 100 100k 10Meg',
        'meas ac f3 when vdb(vo2)=-3 fall=1','meas ac f90 when vp(vo2)=-1.5708 fall=1','print f3 f90','quit','.endc','.end']
    open('a8_net.spice','w').write('\n'.join(L)+'\n')
    return parse(subprocess.run(['ngspice','-b','a8_net.spice'],capture_output=True,text=True).stdout)
base=open('gmc_pt.spice').read()
def sim_pt(corner,vdd,T):
    t=re.sub(r'(?m)^\.lib .*',".lib %s %s"%(LIB,corner),base)
    t=re.sub(r'(?m)^V1 VDD 0 .*','V1 VDD 0 %g'%vdd,t)
    t=re.sub(r'(?m)^\.include .*','.include %s/a8_pt.cir'%D,t)
    t=re.sub(r'(?m)^\.param .*','.param iref=12u rt=1.48 alpha=0.6',t)
    open('a8_pt.cir','w').write('.control\nop\nprint v1#branch\nac dec 100 100k 10Meg\nmeas ac f3 when vdb(vo2)=-3 fall=1\nmeas ac f90 when vp(vo2)=-1.5708 fall=1\nprint f3 f90\nquit\n.endc\n')
    L=t.split('\n'); L.insert(1,'.temp %d'%T); open('a8_ptnet.spice','w').write('\n'.join(L))
    return parse(subprocess.run(['ngspice','-b','a8_ptnet.spice'],capture_output=True,text=True).stdout)
print('calibration (tt, 27C, 1.8V, K=4):')
pts=[]
for R in (3e3,4e3,5e3,6e3,7e3,8e3,10e3,12e3):
    r=sim_cg(R,'tt',1.8,27)
    if r: pts.append((R,r[0])); print('  R %5.1f k  f3 %.3f MHz  Q %.3f  Isupply %.1f uA  v(a) %.3f V'%(R/1e3,r[0],r[1],r[2]*1e6,r[3]))
    else: print('  R %5.1f k  failed'%(R/1e3))
Rsel=None
for (r1,f1),(r2,f2) in zip(pts,pts[1:]):
    if (f1-1.6)*(f2-1.6)<=0:
        t=(log(1.6)-log(f1))/(log(f2)-log(f1)); Rsel=exp(log(r1)+t*(log(r2)-log(r1))); break
if Rsel is None: raise SystemExit('f3=1.6 MHz not bracketed - send me this output')
r=sim_cg(Rsel,'tt',1.8,27); print('selected R = %.0f ohm -> f3 %.3f MHz Q %.3f'%(Rsel,r[0],r[1]))
conds=[(c,1.8,T) for c in ('tt','ss','ff','sf','fs') for T in (-20,27,85)]+[('tt',1.62,27),('tt',1.98,27)]
print('\ncorner  vdd   T | CONST-GM: f3     Q   Ptot(uW) | PTAT ideal-ref: f3     Q')
F1=[];F2=[]
for c,v,T in conds:
    a=sim_cg(Rsel,c,v,T); b=sim_pt(c,v,T)
    if a and b:
        print('%-5s %5.2f %4d |        %6.3f %.3f %7.1f |             %6.3f %.3f'%(c,v,T,a[0],a[1],a[2]*v*1e6,b[0],b[1]))
        if v==1.8: F1.append(a[0]); F2.append(b[0])
    else: print(c,v,T,'failed',bool(a),bool(b))
print('\nf3 max/min at 1.8 V over corners x T:  const-gm %.3f   PTAT %.3f'%(max(F1)/min(F1),max(F2)/min(F2)))
print('\nresistor spread (tt, 1.8 V):')
for s in (0.85,1.0,1.15):
    row=[sim_cg(Rsel*s,'tt',1.8,T) for T in (-20,27,85)]
    print('  R x%.2f : '%s+'   '.join('%.3f/%.3f'%(x[0],x[1]) if x else 'failed' for x in row)+'   (f3 MHz / Q at -20, 27, 85 C)')
