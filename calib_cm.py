import re, glob, math
rows=[]
for f in sorted(glob.glob('calib_logs/c_*.log')):
    m=re.match(r'calib_logs/c_([\d.]+)u_([\d.]+)\.log',f)
    if not m: continue
    d={}
    for line in open(f,errors='ignore'):
        mm=re.match(r'^(pw|f3|f90|pk)\s*=\s*([-+0-9.eE]+)',line)
        if mm: d[mm.group(1)]=float(mm.group(2))
    if {'pw','f3','f90','pk'} <= d.keys():
        x=d['f3']/d['f90']; u=x*x; q=1/math.sqrt((2-(1-u)**2)/u)
        rows.append((float(m.group(1)),float(m.group(2)),d['f3']/1e6,q,d['pk'],d['pw']*1e6))
    else:
        print('FAILED', f, d)
print('Iref(uA) rt   f3(MHz)  Q      pk(dB)  P(uW)')
for r in rows: print('%7.1f  %.1f  %7.3f  %.3f  %6.3f  %6.1f'%r)
if rows:
    best=min(rows,key=lambda r:((r[2]-1.622)/1.622)**2+((r[3]-0.723)/0.723)**2)
    print('closest to f3=1.622 MHz, Q=0.723 (voltage-bias nominal): Iref=%.1fu rt=%.1f -> f3=%.3f Q=%.3f P=%.1f uW'%(best[0],best[1],best[2],best[3],best[5]))
