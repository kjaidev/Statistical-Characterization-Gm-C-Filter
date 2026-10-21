import os, subprocess, numpy as np, sys
D='/foss/designs/gmc-filter'; os.chdir(D)
LIB='/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice'
SIG=dict(pair=2.76e-3, tail=1.45e-3, load=2.89e-3)
NP='sky130_fd_pr__nfet_01v8'; PP='sky130_fd_pr__pfet_01v8'
def ota(k,out,inp,inn,vb,dv):
    n1,n2='n1_%d'%k,'n2_%d'%k
    a="ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0 mult=1"
    b="ad=2.32 as=2.32 pd=16.58 ps=16.58 nrd=0.03625 nrs=0.03625 sa=0 sb=0 sd=0 mult=1"
    c="ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0 mult=1"
    return [
     'XM1_%d %s g1_%d %s 0 %s L=0.5 W=4 nf=1 %s'%(k,n2,k,n1,NP,a), 'Vo1_%d g1_%d %s DC %.6e'%(k,k,inp,dv['m1']),
     'XM2_%d %s g2_%d %s 0 %s L=0.5 W=4 nf=1 %s'%(k,out,k,n1,NP,a), 'Vo2_%d g2_%d %s DC %.6e'%(k,k,inn,dv['m2']),
     'XM3_%d %s g3_%d VDD VDD %s L=0.5 W=8 nf=1 %s'%(k,n2,k,PP,b), 'Vo3_%d g3_%d %s DC %.6e'%(k,k,n2,dv['m3']),
     'XM4_%d %s g4_%d VDD VDD %s L=0.5 W=8 nf=1 %s'%(k,out,k,PP,b), 'Vo4_%d g4_%d %s DC %.6e'%(k,k,n2,dv['m4']),
     'XM5_%d %s g5_%d 0 0 %s L=1 W=6 nf=1 %s'%(k,n1,k,NP,c), 'Vo5_%d g5_%d %s DC %.6e'%(k,k,vb,dv['m5'])]
def draw(rng):
    d=[]
    for k in range(3):
        d.append(dict(m1=rng.normal(0,SIG['pair']),m2=rng.normal(0,SIG['pair']),m3=rng.normal(0,SIG['load']),m4=rng.normal(0,SIG['load']),m5=rng.normal(0,SIG['tail'])))
    return d, rng.normal(0,SIG['tail']), rng.normal(0,SIG['tail'])
def netlist(dr,sim,outfile):
    d,r1,r2=dr
    L=['inj '+sim]
    if sim=='x': L.append('.options parser scale=1.0u')
    L+=['Vinp vin 0 DC 0.9 AC 1','V1 VDD 0 DC 1.8','Vinn vcm 0 DC 0.9','Vaux vaux 0 DC 1.8','Iref VDD vbn DC 12u','Iref3 vaux vbn3 DC 17.76u',
        'Vor1 gr1 vbn DC %.6e'%r1,'XMr vbn gr1 0 0 %s L=1 W=6 nf=1 ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0 mult=1'%NP,
        'Vor2 gr2 vbn3 DC %.6e'%r2,'XMr3 vbn3 gr2 0 0 %s L=1 W=6 nf=1 ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0 mult=1'%NP,
        'C1 vo1 0 10p','C2 vo2 0 10p']
    L+=ota(1,'vo1','vin','vo2','vbn',d[0])+ota(2,'vo2','vo1','vcm','vbn',d[1])+ota(3,'vo1','vcm','vo1','vbn3',d[2])
    L+=['.lib %s tt'%LIB,'.temp 27']
    if sim=='n': L+=['.control','op','ac dec 200 100k 10Meg','wrdata %s vdb(vo2) vp(vo2)'%outfile,'quit','.endc','.end']
    else: L+=['.ac dec 200 100k 10Meg','.print ac format=noindex vdb(vo2) vp(vo2)','.end']
    return '\n'.join(L)+'\n'
def cross(x,y,lvl):
    for i in range(len(y)-1):
        if (y[i]-lvl)*(y[i+1]-lvl)<=0 and y[i]!=y[i+1]: return x[i]+(lvl-y[i])/(y[i+1]-y[i])*(x[i+1]-x[i])
def fq(f,m,ph):
    if abs(ph).max()<7: ph=np.degrees(ph)
    lf=np.log10(f); f3=10**cross(lf,m,-3)/1e6; f90=10**cross(lf,ph,-90)/1e6
    u=(f3/f90)**2; return f3, 1/np.sqrt((2-(1-u)**2)/u)
def run_n(dr,i):
    out='inj_n_%d.txt'%i; open('inj_n.cir','w').write(netlist(dr,'n',out))
    if os.path.exists(out): os.remove(out)
    subprocess.run(['ngspice','-b','inj_n.cir'],capture_output=True,text=True)
    a=np.loadtxt(out); return fq(a[:,0],a[:,1],a[:,3])
def run_x(dr,i):
    open('inj_x.cir','w').write(netlist(dr,'x',None))
    if os.path.exists('inj_x.cir.FD.prn'): os.remove('inj_x.cir.FD.prn')
    subprocess.run(['Xyce','inj_x.cir'],capture_output=True,text=True)
    r=[[float(x) for x in l.split()] for l in open('inj_x.cir.FD.prn') if len(l.split())==3 and l.split()[0][0].isdigit()]
    a=np.array(r); return fq(a[:,0],a[:,1],a[:,2])

CL=float(os.environ.get('CL','2')); K=CL/2.0
def core(RL):
    return ['Vsns nr 0 DC 0',
     'XMP1 n1c pg VDD VDD %s w=%g l=%g'%(PP,8*K,CL),'XMP2 n2c pg VDD VDD %s w=%g l=%g'%(PP,8*K,CL),
     'XMc1 n1c n1c 0 0 %s w=%g l=%g'%(NP,2*K,CL),'XMc2 n2c n1c ns 0 %s w=%g l=%g'%(NP,8*K,CL),
     'XRc ns nr 0 sky130_fd_pr__res_high_po_1p41 w=1.41 l=%.3f'%RL,
     'Rst VDD n1c 5Meg','Rpg n2c pg 1',
     'XMP3 vbn pg VDD VDD %s w=%g l=%g'%(PP,8*K,CL),'XMP4 vbn3 pg VDD VDD %s w=%g l=%g'%(PP,11.84*K,CL),
     '.nodeset v(n1c)=0.8 v(n2c)=0.9 v(pg)=0.9 v(vbn)=0.6 v(vbn3)=0.6']
def netlist2(RL,corner,vdd,temp,out):
    d=[dict(m1=0,m2=0,m3=0,m4=0,m5=0)]*3
    L=['full ptat']
    L+=['Vinp vin 0 DC 0.9 AC 1','V1 VDD 0 DC %s'%vdd,'Vinn vcm 0 DC 0.9',
        'XMr vbn vbn 0 0 %s L=1 W=6 nf=1 ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0 mult=1'%NP,
        'XMr3 vbn3 vbn3 0 0 %s L=1 W=6 nf=1 ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0 mult=1'%NP,
        'C1 vo1 0 10p','C2 vo2 0 10p']
    L+=core(RL)
    L+=ota(1,'vo1','vin','vo2','vbn',d[0])+ota(2,'vo2','vo1','vcm','vbn',d[1])+ota(3,'vo1','vcm','vo1','vbn3',d[2])
    L+=['.lib %s %s'%(LIB,corner),'.temp %s'%temp,'.control','op','let ib = -i(Vsns)','echo IB $&ib','ac dec 200 100k 10Meg','wrdata %s vdb(vo2) vp(vo2)'%out,'quit','.endc','.end']
    return '\n'.join(L)+'\n'
def run(RL,corner,vdd,temp):
    out='pf_out.txt'
    open('pf.cir','w').write(netlist2(RL,corner,vdd,temp,out))
    if os.path.exists(out): os.remove(out)
    r=subprocess.run(['ngspice','-b','pf.cir'],capture_output=True,text=True)
    ib=[l for l in r.stdout.splitlines() if l.startswith('IB ')]
    ib=float(ib[0].split()[1]) if ib else float('nan')
    a=np.loadtxt(out); f3,q=fq(a[:,0],a[:,1],a[:,3]); return ib,f3,q
RL=65.0
for it in range(4):
    ib,f3,q=run(RL,'tt',1.8,27); print('calib RL=%.2f  Ibias=%.3fu  f3=%.4f Q=%.4f'%(RL,abs(ib)*1e6,f3,q),flush=True)
    RL*=np.sqrt(abs(ib)/12e-6)
print('using RL=%.2f'%RL)
rows=[]
for c in ['tt','ss','ff','sf','fs']:
    for v in ['1.62','1.8','1.98']:
        for t in [-20,27,85]:
            try:
                ib,f3,q=run(RL,c,v,t)
                rows.append((c,v,t,abs(ib)*1e6,f3,q)); print('%s %s %4d  I=%.2fu f3=%.4f Q=%.4f'%(c,v,t,abs(ib)*1e6,f3,q),flush=True)
            except Exception as e:
                print(c,v,t,'FAILED',e,flush=True)
open('ptat_full_L%g.txt'%CL,'w').write('corner vdd T I_uA f3_MHz Q\n'+'\n'.join('%s %s %d %.3f %.4f %.4f'%r for r in rows)+'\n')
f=np.array([r[4] for r in rows]); q=np.array([r[5] for r in rows])
print('SUMMARY n=%d  f3 min/max %.4f/%.4f  worst |dev from 1.6| = %.2f%%  Q min/max %.4f/%.4f'%(len(f),f.min(),f.max(),100*abs(f/1.6-1).max(),q.min(),q.max()))
print('in-spec (f3 +-10%% and Q 0.6-0.8): %d / %d'%(int(((abs(f/1.6-1)<=0.1)&(q>=0.6)&(q<=0.8)).sum()),len(f)))
