import re, subprocess, os, math
import numpy as np
D='/foss/designs/gmc-filter'; LIB='/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice'
os.chdir(D)
base=open('gmc_pt.spice').read()
def run(A,f):
    t=re.sub(r'(?m)^\.lib .*',".lib %s tt"%LIB,base)
    t=re.sub(r'(?m)^V1 VDD 0 .*','V1 VDD 0 1.8',t)
    t=re.sub(r'(?m)^Vinp .*','Vinp vin 0 dc 0.9 ac 1 sin(0.9 %g %g)'%(A,f),t)
    t=re.sub(r'(?m)^\.include .*','.include %s/a9.cir'%D,t)
    t=re.sub(r'(?m)^\.param .*','.param iref=12u rt=1.48 alpha=0.6',t)
    tstop=10.0/f; tmax=1.0/(f*200)
    open('a9.cir','w').write('.control\nop\nac dec 100 10k 100Meg\nmeas ac gdb find vdb(vo2) at=%g\nmeas ac ph find vp(vo2) at=%g\ntran %g %g 0 %g\nwrdata a9_wave.txt v(vo2) v(vin)\nquit\n.endc\n'%(f,f,tmax,tstop,tmax))
    L=t.split('\n'); L.insert(1,'.temp 27'); open('a9_net.spice','w').write('\n'.join(L))
    o=subprocess.run(['ngspice','-b','a9_net.spice'],capture_output=True,text=True).stdout
    g=re.search(r'^gdb\s*=\s*([-+0-9.eE]+)',o,re.M); p=re.search(r'^ph\s*=\s*([-+0-9.eE]+)',o,re.M)
    d=np.loadtxt('a9_wave.txt')
    tt=d[:,0]; vo=d[:,1]; vi=d[:,-1]
    T=1.0/f; t0=tt[-1]-5*T
    tg=np.linspace(t0,tt[-1],5*256,endpoint=False)
    vo=np.interp(tg,tt,vo); vi=np.interp(tg,tt,vi)
    Vo=np.fft.rfft(vo-vo.mean())/len(vo)*2; Vi=np.fft.rfft(vi-vi.mean())/len(vi)*2
    h=[abs(Vo[5*k]) for k in range(1,6)]
    gain=20*math.log10(h[0]/A); ph=np.angle(Vo[5]/Vi[5])
    thd=math.sqrt(sum(x*x for x in h[1:]))/h[0]
    return dict(gain=gain,ph=ph,thd=100*thd,hd2=20*math.log10(max(h[1],1e-12)/h[0]),hd3=20*math.log10(max(h[2],1e-12)/h[0]),
                acg=float(g.group(1)) if g else float('nan'),acp=float(p.group(1)) if p else float('nan'),dc=float(vo.mean()),pp=float(vo.max()-vo.min()))
amps=[0.005,0.01,0.02,0.05,0.1,0.15,0.2,0.3]
for f in (200e3,1.6e6):
    print('\nTHD vs amplitude at %.1f kHz (tt, 27C, 1.8V)'%(f/1e3))
    print('A(mV pk)  gain(dB)  THD(%)   HD2(dB)  HD3(dB)  Vout pk-pk(mV)')
    res=[]
    for A in amps:
        r=run(A,f); res.append((A,r['gain']))
        print('%7.0f   %7.2f  %7.2f  %7.1f  %7.1f   %8.0f'%(A*1e3,r['gain'],r['thd'],r['hd2'],r['hd3'],r['pp']*1e3))
    g0=res[0][1]; cp=None
    for (a1,g1),(a2,g2) in zip(res,res[1:]):
        if g0-g1<1.0<=g0-g2:
            cp=a1+(a2-a1)*((g0-1.0)-g1)/(g2-g1); break
    print('small-signal gain (5 mV): %.2f dB ; 1 dB compression input: %s'%(g0,('%.0f mV pk'%(cp*1e3)) if cp else 'not reached up to 300 mV'))
print('\nAC vs transient (10 mV pk): freq   AC gain  tran gain  diff(dB)  AC phase  tran phase (deg)')
for f in (1e5,2e5,4e5,8e5,1.6e6,3.2e6,6.4e6):
    r=run(0.01,f)
    print('%8.0f kHz   %7.3f  %7.3f   %6.3f   %8.2f  %8.2f'%(f/1e3,r['acg'],r['gain'],r['gain']-r['acg'],math.degrees(r['acp']),math.degrees(r['ph'])))
