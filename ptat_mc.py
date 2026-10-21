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
def netlist2_unused(RL,corner,vdd,temp,out):
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
import time

import multiprocessing as mp
def netlist3(RL,corner,vdd,temp,N,seed,out):
    d=[dict(m1=0,m2=0,m3=0,m4=0,m5=0)]*3
    nm=NP
    L=['mc ptat','Vinp vin 0 DC 0.9 AC 1','V1 VDD 0 DC %s'%vdd,'Vinn vcm 0 DC 0.9',
       'XMr vbn vbn 0 0 %s L=1 W=6 nf=1 ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0 mult=1'%NP,
       'XMr3 vbn3 vbn3 0 0 %s L=1 W=6 nf=1 ad=1.74 as=1.74 pd=12.58 ps=12.58 nrd=0.0483333333333333 nrs=0.0483333333333333 sa=0 sb=0 sd=0 mult=1'%NP,
       'C1 vo1 0 10p','C2 vo2 0 10p']
    L+=core(RL)
    L+=ota(1,'vo1','vin','vo2','vbn',d[0])+ota(2,'vo2','vo1','vcm','vbn',d[1])+ota(3,'vo1','vcm','vo1','vbn3',d[2])
    L+=['.lib %s %s_mm'%(LIB,corner),'.temp %s'%temp,'.control','setseed %d'%seed,'let n = %d'%N,'let k = 0','while k < n','reset','op',
        'let ibx = -i(Vsns)','set ibs = $&ibx','ac dec 20 100k 10Meg','meas ac f3 when vdb(vo2)=-3 fall=1','meas ac f90 when vp(vo2)=-1.5708 fall=1',
        'meas ac pk max vdb(vo2)','echo RES $ibs $&f3 $&f90 $&pk >> %s'%out,'let k = k + 1','end','quit','.endc','.end']
    return '\n'.join(L)+'\n'
def job(a):
    idx,corner,vdd,temp,N,RL=a
    base='mcw_%d'%idx; out=base+'.out'
    if os.path.exists(out): os.remove(out)
    open(base+'.cir','w').write(netlist3(RL,corner,vdd,temp,N,12345+idx,out))
    subprocess.run(['ngspice','-b',base+'.cir'],capture_output=True,text=True)
    rows=[]
    for l in open(out) if os.path.exists(out) else []:
        p=l.split()
        try:
            ib,f3,f90,pk=[float(x) for x in p[1:5]]
            if f3>0 and f90>0:
                u=(f3/f90)**2; q=1/np.sqrt((2-(1-u)**2)/u); rows.append((abs(ib)*1e6,f3/1e6,q,pk))
        except Exception: pass
    return (corner,vdd,temp,rows)
if __name__=='__main__':
    N=int(sys.argv[1]) if len(sys.argv)>1 else 100
    RL=float(sys.argv[2]) if len(sys.argv)>2 else 51.47
    conds=[(i,c,v,t,N,RL) for i,(c,v,t) in enumerate([(c,v,t) for c in ['tt','ss','ff','sf','fs'] for v in ['1.62','1.8','1.98'] for t in [-20,27,85]])]
    nc=os.cpu_count() or 4; print('cores',nc,'conditions',len(conds),'runs/cond',N,flush=True)
    t0=time.time(); res=[]
    import time as _t
    with mp.Pool(nc) as p:
        for r in p.imap_unordered(job,conds):
            res.append(r); print('done %s %s %s  n=%d  (%.0fs)'%(r[0],r[1],r[2],len(r[3]),time.time()-t0),flush=True)
    res.sort(key=lambda r:(r[0],float(r[1]),r[2]))
    import csv
    with open('ptat_mc_runs.csv','w') as fh:
        w=csv.writer(fh); w.writerow(['corner','vdd','T','I_uA','f3_MHz','Q','pk_dB'])
        for c,v,t,rows in res:
            for r in rows: w.writerow([c,v,t]+['%.5g'%x for x in r])
    ys=[];tab=[]
    for c,v,t,rows in res:
        a=np.array(rows)
        if len(a)==0: continue
        ok=(abs(a[:,1]/1.6-1)<=0.1)&(a[:,2]>=0.6)&(a[:,2]<=0.8)
        ys.append(ok.mean()); tab.append((c,v,t,len(a),a[:,1].mean(),100*a[:,1].std()/a[:,1].mean(),a[:,2].mean(),100*ok.mean()))
    open('ptat_mc_summary.txt','w').write('corner vdd T n f3_mean f3_sd_pct Q_mean yield_pct\n'+'\n'.join('%s %s %d %d %.4f %.2f %.4f %.1f'%r for r in tab)+'\n')
    print('TOTAL runs',sum(r[3] for r in tab),' MEAN yield %.1f%%  WORST yield %.1f%% (%s)  BEST %.1f%%'%(100*np.mean(ys),100*min(ys),[r[:3] for r in tab if abs(r[7]-100*min(ys))<1e-9][0],100*max(ys)))
    nom=[r for r in tab if r[:3]==('tt','1.8',27)]
    print('nominal tt 1.8V 27C:',nom)
    mm=[r[4] for r in tab]; print('per-condition mean f3 min/max %.4f / %.4f'%(min(mm),max(mm)))
