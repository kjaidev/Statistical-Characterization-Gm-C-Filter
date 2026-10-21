import numpy as np
tags = ['nom','ss','ff','v162','v198','tm20','t85']
F0, FTOL, QLO, QHI = 1.6e6, 0.10, 0.6, 0.8
def load(t):
    d = {'pw':[],'f3':[],'f90':[],'pk':[],'g':[]}
    for line in open('results_%s.txt' % t):
        p = line.split()
        if len(p) >= 3 and p[0] in d:
            d[p[0]].append(float(p[2]))
    d = {k: np.array(v) for k, v in d.items()}
    u = (d['f3']/d['f90'])**2
    d['Q'] = 1/np.sqrt((2-(1-u)**2)/u)
    return d
D = {t: load(t) for t in tags}
if __name__ == '__main__':
    print('tag   f3_MHz  sd%   Q     sdQ   P_uW  sdP%  yield%')
    for t in tags:
        d = D[t]
        ok = (abs(d['f3']/F0-1) <= FTOL) & (d['Q'] >= QLO) & (d['Q'] <= QHI)
        print('%-5s %.4f %.2f %.3f %.3f %.1f %.2f %.1f' % (t, d['f3'].mean()/1e6, 100*d['f3'].std()/d['f3'].mean(), np.nanmean(d['Q']), np.nanstd(d['Q']), d['pw'].mean()*1e6, 100*d['pw'].std()/d['pw'].mean(), 100*ok.mean()))
