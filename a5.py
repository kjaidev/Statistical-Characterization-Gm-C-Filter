import re, subprocess, math, os
import numpy as np
D='/foss/designs/gmc-filter'
LIB='/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice'
os.chdir(D)
N='sky130_fd_pr__nfet_01v8'; P='sky130_fd_pr__pfet_01v8'
def run(net,fn):
    open(fn,'w').write(net)
    return subprocess.run(['ngspice','-b',fn],capture_output=True,text=True).stdout

mc="""mc vgs
.lib %s tt_mm
Vdd vdd 0 1.8
Ia 0 a DC 6u
XMa a a 0 0 %s L=0.5 W=4 nf=1
Ib 0 b DC 12u
XMb b b 0 0 %s L=1 W=6 nf=1
Ic c 0 DC 6u
XMc c c vdd vdd %s L=0.5 W=8 nf=1
.control
setseed 12345
repeat 750
  reset
  op
  print v(a) v(b) v(c)
end
quit
.endc
.end
"""%(LIB,N,N,P)
out=run(mc,'a5_mc.spice')
va=[float(x) for x in re.findall(r'^v\(a\)\s*=\s*([-+0-9.eE]+)',out,re.M)]
vb=[float(x) for x in re.findall(r'^v\(b\)\s*=\s*([-+0-9.eE]+)',out,re.M)]
vc=[1.8-float(x) for x in re.findall(r'^v\(c\)\s*=\s*([-+0-9.eE]+)',out,re.M)]
sig={'pair':np.std(va),'tail':np.std(vb),'load':np.std(vc)}
print('MC samples: %d %d %d'%(len(va),len(vb),len(vc)))
print('sigma(Vgs at fixed Id): pair(W4/L0.5) %.2f mV  tail/ref(W6/L1) %.2f mV  load(W8/L0.5) %.2f mV'%(sig['pair']*1e3,sig['tail']*1e3,sig['load']*1e3))

def netlist(par):
    p=' '.join('%s=%g'%(k,v) for k,v in par.items())
    L=[]
    L.append('a5 sens'); L.append('.GLOBAL VDD')
    L.append('.param iref=12u rt=1.48 alpha=0.6 '+p)
    L.append('Vinp vin 0 0.9 ac 1'); L.append('V1 VDD 0 1.8'); L.append('Vinn vcm 0 0.9')
    L.append('BIref VDD vbn I = {iref}*pow((temper+273.15)/300.15,{alpha})')
    L.append('Vr1 gr1 vbn DC {dr1}')
    L.append('XMr vbn gr1 0 0 %s L=1 W=6 nf=1 ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0'%N)
    L.append('Vaux vaux 0 1.8')
    L.append('BIref3 vaux vbn3 I = {iref*rt}*pow((temper+273.15)/300.15,{alpha})')
    L.append('Vr3 gr3 vbn3 DC {dr3}')
    L.append('XMr3 vbn3 gr3 0 0 %s L=1 W=6 nf=1 ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0'%N)
    L.append('C1 vo1 0 10p'); L.append('C2 vo2 0 10p')
    L.append('x1 vo1 vin vo2 vbn ota1'); L.append('x2 vo2 vo1 vcm vbn ota2'); L.append('x3 vo1 vcm vo1 vbn3 ota3')
    for k in (1,2,3):
        L.append('.subckt ota%d OUT1 IN1+ IN1- Vbias_tail'%k)
        L.append('Vg1 g1 IN1+ DC {do%d_m1}'%k)
        L.append('XM1 net2 g1 net1 0 %s L=0.5 W=4 nf=1 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0'%N)
        L.append('Vg2 g2 IN1- DC {do%d_m2}'%k)
        L.append('XM2 OUT1 g2 net1 0 %s L=0.5 W=4 nf=1 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0'%N)
        L.append('Vg3 g3 net2 DC {do%d_m3}'%k)
        L.append('XM3 net2 g3 VDD VDD %s L=0.5 W=8 nf=1 ad=2.32 as=2.32 pd=16.58 ps=16.58 nrd=0.03625 nrs=0.03625 sa=0 sb=0 sd=0'%P)
        L.append('Vg4 g4 net2 DC {do%d_m4}'%k)
        L.append('XM4 OUT1 g4 VDD VDD %s L=0.5 W=8 nf=1 ad=2.32 as=2.32 pd=16.58 ps=16.58 nrd=0.03625 nrs=0.03625 sa=0 sb=0 sd=0'%P)
        L.append('Vg5 g5 Vbias_tail DC {do%d_m5}'%k)
        L.append('XM5 net1 g5 0 0 %s L=1 W=6 nf=1 ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0'%N)
        L.append('.ends')
    L.append('.lib %s tt'%LIB)
    L.append('.temp 27')
    L.append('.control'); L.append('op'); L.append('ac dec 200 100k 10Meg')
    L.append('meas ac f3 when vdb(vo2)=-3 fall=1'); L.append('meas ac f90 when vp(vo2)=-1.5708 fall=1')
    L.append('print f3 f90'); L.append('quit'); L.append('.endc'); L.append('.end')
    return '\n'.join(L)+'\n'
names=['do%d_m%d'%(k,j) for k in (1,2,3) for j in (1,2,3,4,5)]+['dr1','dr3']
def sim(over):
    par={n:0.0 for n in names}; par.update(over)
    o=run(netlist(par),'a5_net.spice')
    m3=re.search(r'^f3\s*=\s*([-+0-9.eE]+)',o,re.M); m9=re.search(r'^f90\s*=\s*([-+0-9.eE]+)',o,re.M)
    if not(m3 and m9): raise SystemExit('sim failed for %s\n%s'%(over,o[-1500:]))
    f3=float(m3.group(1)); f90=float(m9.group(1)); x=f3/f90; u=x*x
    return f3/1e6, 1/math.sqrt((2-(1-u)**2)/u)
f0,q0=sim({})
print('nominal: f3 %.4f MHz  Q %.4f'%(f0,q0))
dv=0.002
rows=[]
for n in names:
    fp,qp=sim({n:dv}); fm,qm=sim({n:-dv})
    sf=(fp-fm)/(2*dv)/f0; sq=(qp-qm)/(2*dv)/q0
    role='pair' if n.endswith(('m1','m2')) else 'load' if n.endswith(('m3','m4')) else 'tail' if n.endswith('m5') else 'ref'
    rows.append((n,role,sf,sq))
    print('%-7s %-5s dlnf3/dV %8.3f /V   dlnQ/dV %8.3f /V'%(n,role,sf,sq))

def budget(refscale,label):
    sg=dict(sig); sg['ref']=sig['tail']/refscale
    tf=0;tq=0;gf={};gq={}
    for n,role,sf,sq in rows:
        vf=(sf*sg[role])**2; vq=(sq*sg[role])**2
        tf+=vf; tq+=vq; gf[role]=gf.get(role,0)+vf; gq[role]=gq.get(role,0)+vq
    print('\n[%s] predicted sigma f3 = %.2f %%   sigma Q = %.2f %%'%(label,100*math.sqrt(tf),100*math.sqrt(tq)))
    for r in ('pair','load','tail','ref'):
        print('   %-5s  f3 variance share %5.1f %%   Q variance share %5.1f %%'%(r,100*gf[r]/tf,100*gq[r]/tq))
    for k in (1,2,3):
        vf=sum((sf*sg[role])**2 for n,role,sf,sq in rows if n.startswith('do%d_'%k))
        print('   OTA%d f3 variance share %5.1f %%'%(k,100*vf/tf))
budget(1.0,'mirror x1   (MC at 27C: f3 5.91 %, Q 3.68 %)')
budget(2.0,'mirror x4   (MC at 27C: f3 4.81 %, Q 3.13 %)')
