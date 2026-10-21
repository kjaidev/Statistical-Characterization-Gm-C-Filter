import re, glob, math
res={}
for f in sorted(glob.glob('calib_pt_logs/a*_T*.log')):
    m=re.match(r'calib_pt_logs/a([\d.]+)_T(-?\d+)\.log',f)
    d={}
    for line in open(f,errors='ignore'):
        mm=re.match(r'^(pw|f3|f90|pk)\s*=\s*([-+0-9.eE]+)',line)
        if mm: d[mm.group(1)]=float(mm.group(2))
    if {'pw','f3','f90','pk'}<=d.keys():
        x=d['f3']/d['f90']; u=x*x; q=1/math.sqrt((2-(1-u)**2)/u)
        res[(float(m.group(1)),int(m.group(2)))]=(d['f3']/1e6,q,d['pw']*1e6)
    else: print('FAILED',f)
print('alpha |  f3 @-20   f3 @27   f3 @85 | spread (max/min) | Q @-20 @27 @85')
best=None
for a in sorted({k[0] for k in res}):
    try: v=[res[(a,t)] for t in (-20,27,85)]
    except KeyError: continue
    f=[x[0] for x in v]; sp=max(f)/min(f)
    print('%4.1f  | %8.3f %8.3f %8.3f | %6.3f | %.3f %.3f %.3f'%(a,*f,sp,*[x[1] for x in v]))
    if best is None or sp<best[1]: best=(a,sp)
if best: print('flattest f3 over temperature: alpha=%.1f (spread %.3f)'%best)
