import os, subprocess, numpy as np, sys
D='/foss/designs/gmc-filter'; os.chdir(D)
LIB='/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice'
N=int(sys.argv[1]) if len(sys.argv)>1 else 30
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
rng=np.random.default_rng(7)
zero=([dict(m1=0,m2=0,m3=0,m4=0,m5=0)]*3,0.0,0.0)
draws=[zero]+[draw(rng) for _ in range(N)]
res=[]
for i,dr in enumerate(draws):
    try:
        n=run_n(dr,i); x=run_x(dr,i); res.append((n[0],n[1],x[0],x[1]))
        print('%2d ngspice f3 %.4f Q %.4f | Xyce f3 %.4f Q %.4f | df3 %+.3f%%'%(i,n[0],n[1],x[0],x[1],100*(x[0]/n[0]-1)),flush=True)
    except Exception as e: print(i,'failed',e,flush=True)
R=np.array(res); np.savetxt('inj_results.txt',R,header='f3_ng Q_ng f3_xy Q_xy')
r=R[1:]; d=100*(r[:,2]/r[:,0]-1); dq=100*(r[:,3]/r[:,1]-1)
print('\nnominal: ngspice f3 %.4f Q %.4f | Xyce f3 %.4f Q %.4f'%tuple(R[0]))
print('runs %d: f3 sigma/mean  ngspice %.2f%%  Xyce %.2f%%'%(len(r),100*r[:,0].std()/r[:,0].mean(),100*r[:,2].std()/r[:,2].mean()))
print('Q sigma ngspice %.4f Xyce %.4f'%(r[:,1].std(),r[:,3].std()))
print('per-run f3 difference Xyce vs ngspice: mean %+.3f%%, max abs %.3f%%; Q: mean %+.3f%%, max abs %.3f%%'%(d.mean(),abs(d).max(),dq.mean(),abs(dq).max()))
print('f3 correlation ngspice vs Xyce: %.5f'%np.corrcoef(r[:,0],r[:,2])[0,1])
