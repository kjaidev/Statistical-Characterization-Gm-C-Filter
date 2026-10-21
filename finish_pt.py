import re, glob, math, os
import numpy as np
_trap = getattr(np, "trapezoid", None) or getattr(np, "trapz")
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.25,'figure.dpi':150})
C1,C2,C3='#1f77b4','#d62728','#2ca02c'

def vals(path,keys):
    d={}
    if not os.path.exists(path): return d
    for line in open(path,errors='ignore'):
        m=re.match(r'^(%s)\s*=\s*([-+0-9.eE]+)'%'|'.join(re.escape(k) for k in keys),line)
        if m: d[m.group(1)]=float(m.group(2))
    return d

# 1) nominal AC
f=mag=ph=None
if os.path.exists('curves_nom_pt.txt'):
    a=np.loadtxt('curves_nom_pt.txt')
    f=a[:,0]/1e6; mag=a[:,1]; ph=np.degrees(a[:,3])
    fig,ax=plt.subplots(1,2,figsize=(10,3.8))
    ax[0].semilogx(f,mag,C1); ax[0].axhline(-3,color=C2,ls=':'); ax[0].set_xlabel('frequency (MHz)'); ax[0].set_ylabel('magnitude (dB)'); ax[0].set_title('Nominal AC response (tt, 27 C, 1.8 V)')
    ax[1].semilogx(f,ph,C1); ax[1].axhline(-90,color=C2,ls=':'); ax[1].set_xlabel('frequency (MHz)'); ax[1].set_ylabel('phase (deg)'); ax[1].set_title('Phase')
    plt.tight_layout(); plt.savefig('fig_nominal_ac.png'); plt.close()
    f3=np.interp(-3,mag[::-1],f[::-1]); print('NOMINAL AC: f3(-3 dB) = %.3f MHz; DC gain %.3f dB; peak %.3f dB'%(f3,mag[0],mag.max()))

# 2) peaking histogram from the PTAT MC (tt, 27 C, 1.8 V): peaking = max|H| - passband gain
fn='results_pt_tt_1.8_27.txt'
if os.path.exists(fn):
    pk=[];g=[]
    for line in open(fn,errors='ignore'):
        m=re.match(r'^(pk|g)\s*=\s*([-+0-9.eE]+)',line)
        if m: (pk if m.group(1)=='pk' else g).append(float(m.group(2)))
    n=min(len(pk),len(g)); pr=np.array(pk[:n])-np.array(g[:n])
    plt.figure(figsize=(5,3.6)); plt.hist(pr,bins=30,color=C1); plt.xlabel('passband peaking (dB)'); plt.ylabel('runs'); plt.title('Peaking, %d-run MC (tt, 27 C)'%n)
    plt.tight_layout(); plt.savefig('fig_ripple_hist.png'); plt.close()
    print('PEAKING (pk - passband gain): mean %.3f dB, max %.3f dB, 99th pct %.3f dB (n=%d)'%(pr.mean(),pr.max(),np.percentile(pr,99),n))

# 3) offset
if os.path.exists('results_off_pt.txt'):
    v1=[];v2=[]
    for line in open('results_off_pt.txt',errors='ignore'):
        m=re.match(r'^v\(vo([12])\)\s*=\s*([-+0-9.eE]+)',line)
        if m: (v1 if m.group(1)=='1' else v2).append(float(m.group(2)))
    n=min(len(v1),len(v2)); v1=np.array(v1[:n]); v2=np.array(v2[:n])
    off=(v2-0.9)*1e3
    plt.figure(figsize=(5,3.6)); plt.hist(off,bins=30,color=C3); plt.xlabel('output DC offset vo2 - 0.9 V (mV)'); plt.ylabel('runs'); plt.title('DC offset, %d-run MC (tt, 27 C)'%n)
    plt.tight_layout(); plt.savefig('fig_offset_hist.png'); plt.close()
    print('OFFSET: vo2 mean %.1f mV, sigma %.1f mV; vo1 sigma %.1f mV; max |offset| %.1f mV (n=%d)'%(off.mean(),off.std(),(v1.std())*1e3,abs(off).max(),n))

# 4) input common-mode range
rows=[]
for fl in sorted(glob.glob('fin_logs/cmr_*.log'),key=lambda s: float(re.search(r'cmr_([\d.]+)\.log',s).group(1))):
    v=float(re.search(r'cmr_([\d.]+)\.log',fl).group(1))
    d=vals(fl,['v(vo2)','pw','f3','f90','pk','g'])
    if {'f3','f90'}<=d.keys():
        x=d['f3']/d['f90']; u=x*x; q=1/math.sqrt((2-(1-u)**2)/u)
        rows.append((v,d.get('v(vo2)',float('nan')),d['f3']/1e6,q,d.get('g',float('nan')),d.get('pw',float('nan'))*1e6))
    else: rows.append((v,float('nan'),float('nan'),float('nan'),float('nan'),float('nan')))
if rows:
    print('INPUT COMMON-MODE SWEEP  Vcm   vo2(V)   f3(MHz)   Q     gain@100k(dB)  P(uW)')
    for r in rows: print('                         %.2f  %7.3f  %8.3f  %.3f  %8.3f  %7.1f'%r)
    R=np.array(rows); ok=(abs(R[:,2]-1.6)/1.6<=0.05)&(abs(R[:,4])<=0.5)
    good=R[ok,0]
    print('  within f3 +/-5 %% and gain loss <=0.5 dB: Vcm = %s'%(', '.join('%.2f'%g for g in good) if len(good) else 'none'))
    fig,ax=plt.subplots(1,2,figsize=(9,3.6))
    ax[0].plot(R[:,0],R[:,2],'o-',color=C1); ax[0].axhspan(1.52,1.68,color=C3,alpha=.2); ax[0].set_xlabel('input common-mode (V)'); ax[0].set_ylabel('f3 (MHz)')
    ax[1].plot(R[:,0],R[:,4],'o-',color=C2); ax[1].set_xlabel('input common-mode (V)'); ax[1].set_ylabel('passband gain (dB)')
    plt.tight_layout(); plt.savefig('fig_cm_range.png'); plt.close()

# 5) noise
d=vals('fin_logs/noise.log',['onoise_total','inoise_total'])
if os.path.exists('curves_noise_pt.txt'):
    a=np.loadtxt('curves_noise_pt.txt'); fr=a[:,0]; on=np.abs(a[:,1]); inn=np.abs(a[:,3])
    f3n=1.61e6
    band=(fr>=1e3)&(fr<=f3n)
    onb=math.sqrt(_trap(on[band]**2,fr[band])); inb=math.sqrt(_trap(inn[band]**2,fr[band]))
    i100=np.argmin(abs(fr-1e5)); i10k=np.argmin(abs(fr-1e4))
    print('NOISE (tt, 27 C): output integrated 1 kHz-f3 = %.1f uVrms; input-referred integrated 1 kHz-f3 = %.1f uVrms'%(onb*1e6,inb*1e6))
    print('  input-referred density: %.1f nV/rtHz @10 kHz, %.1f nV/rtHz @100 kHz; output density @100 kHz %.1f nV/rtHz'%(inn[i10k]*1e9,inn[i100]*1e9,on[i100]*1e9))
    print('  dynamic range for a 100 mVrms input: %.1f dB (signal / output noise to f3)'%(20*math.log10(0.1/onb)))
    plt.figure(figsize=(5,3.8)); plt.loglog(fr,on*1e9,C1,label='output'); plt.loglog(fr,inn*1e9,C2,label='input-referred'); plt.axvline(f3n,color='gray',ls=':')
    plt.xlabel('frequency (Hz)'); plt.ylabel('noise density (nV/rtHz)'); plt.legend(); plt.title('Noise spectrum (tt, 27 C)'); plt.tight_layout(); plt.savefig('fig_noise.png'); plt.close()
elif d: print('NOISE: only totals available (output %.1f uVrms); run finish_pt2.sh for the spectrum'%(d.get('onoise_total',float('nan'))*1e6))
else: print('NOISE: no result found (see fin_logs/noise.log)')
