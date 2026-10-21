import re,os,numpy as np
IREF=12e-6;ALPHA=0.6
def load(p):
    R=[];c=None
    for l in open(p,errors='ignore'):
        m=re.match(r'^(pw|f3|f90|pk|g)\s*=\s*([-+0-9.eE]+)',l)
        if not m: continue
        k,v=m.group(1),float(m.group(2))
        if k=='pw': c={'pw':v};R.append(c)
        elif c is not None: c[k]=v
    R=[r for r in R if all(k in r for k in('pw','f3','f90'))]
    f=np.array([r['f3'] for r in R])/1e6;f9=np.array([r['f90'] for r in R])/1e6
    u=(f/f9)**2;q=1/np.sqrt((2-(1-u)**2)/u)
    return f,q,np.array([r['pw'] for r in R])*1e6
print('corner  vdd    T |   n    f3    sd%    Q     P   yFix  yCtr')
Y=[];F=[];P=[];Q=[];rows=[]
for c in['tt','ss','ff','sf','fs']:
  for v in['1.62','1.8','1.98']:
    for t in['-20','27','85']:
      fn='results_pt_%s_%s_%s.txt'%(c,v,t)
      if not os.path.exists(fn): print(c,v,t,'missing');continue
      f,q,p=load(fn);p=p-IREF*(((float(t)+273.15)/300.15)**ALPHA)*float(v)*1e6
      fix=np.mean((abs(f-1.6)<=.16)&(q>=.6)&(q<=.8))*100
      ctr=np.mean((abs(f-f.mean())<=.1*f.mean())&(q>=.6)&(q<=.8))*100
      print('%-6s %5s %4s | %4d %5.3f %5.2f %.3f %5.1f %5.1f %5.1f'%(c,v,t,len(f),f.mean(),f.std()/f.mean()*100,q.mean(),p.mean(),fix,ctr))
      Y.append(fix);F.append(f.mean());P.append(p.mean());Q.append(q.mean());rows.append((c,v,t,fix))
print('\nconditions: %d'%len(Y))
print('mean f3 range %.3f-%.3f MHz (ratio %.3f)'%(min(F),max(F),max(F)/min(F)))
print('Q range %.3f-%.3f'%(min(Q),max(Q)))
print('core power %.1f-%.1f uW'%(min(P),max(P)))
print('fixed-spec yield: mean %.1f%%  min %.1f%%  >=90%%: %d/%d  >=80%%: %d/%d'%(np.mean(Y),min(Y),sum(y>=90 for y in Y),len(Y),sum(y>=80 for y in Y),len(Y)))
print('worst 5:',sorted(rows,key=lambda r:r[3])[:5])
