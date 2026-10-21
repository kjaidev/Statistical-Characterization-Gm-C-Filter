import re, subprocess, os, math
import numpy as np
D='/foss/designs/gmc-filter'; LIB='/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice'
os.chdir(D)
t=open('gmc_pt.spice').read()
t=re.sub(r'(?m)^\.lib .*',".lib %s tt"%LIB,t)
t=re.sub(r'(?m)^\.include .*','',t)
t=re.sub(r'(?m)^\.param .*','',t)
t=re.sub(r'(?m)^Vinp .*','Vinp vin 0 DC 0.9 AC 1',t)
t=re.sub(r'(?m)^BIref .*','IIref VDD vbn DC 12u',t)
t=re.sub(r'(?m)^BIref3 .*','IIref3 vaux vbn3 DC 17.76u',t)
t=t.replace('IN1+','INP').replace('IN1-','INM')
t=re.sub(r'(?m)^\.end\s*$','',t)
t+='\n.TEMP 27\n.AC DEC 200 100k 10Meg\n.PRINT AC FORMAT=CSV FILE=%s/a12x.csv FREQ VR(vo2) VI(vo2)\n.END\n'%D
open('a12x.cir','w').write(t)
r=subprocess.run(['Xyce','a12x.cir'],capture_output=True,text=True)
print((r.stdout+r.stderr)[-1500:])
if not os.path.exists('a12x.csv'): raise SystemExit('Xyce produced no output')
d=np.genfromtxt('a12x.csv',delimiter=',',skip_header=1)
f=d[:,-3]; H=d[:,-2]+1j*d[:,-1]; mag=20*np.log10(abs(H)); ph=np.unwrap(np.angle(H))
def cross(y,lvl):
    i=int(np.argmax(y<=lvl)); return np.exp(np.interp(lvl,[y[i],y[i-1]],[np.log(f[i]),np.log(f[i-1])]))
f3=cross(mag,-3.0); f90=cross(ph,-math.pi/2)
x=f3/f90; u=x*x; q=1/math.sqrt((2-(1-u)**2)/u)
print('\nXyce nominal (tt, 27C, 1.8V): f3 = %.4f MHz  f90 = %.4f MHz  Q = %.4f  gain@100k = %.3f dB'%(f3/1e6,f90/1e6,q,mag[0]))
print('ngspice nominal (A7):          f3 = 1.6102 MHz  Q = 0.7218  gain@100k = -0.150 dB')
