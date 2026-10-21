import sys, time, numpy as np
tag, n = sys.argv[1], int(sys.argv[2])
rng = np.random.default_rng()
f = np.logspace(5, 7, 41)
open('results_%s.txt' % tag, 'w').close(); open('curves_%s.txt' % tag, 'w').close()
for k in range(n):
    f0 = 1.6e6 * (1 + 0.05 * rng.standard_normal()); Q = 0.72 + 0.025 * rng.standard_normal()
    w = f / f0
    mag = -10 * np.log10((1 - w**2) ** 2 + (w / Q) ** 2)
    ph = -np.arctan2(w / Q, 1 - w**2)
    f3 = np.interp(-3, mag[::-1], f[::-1])
    with open('results_%s.txt' % tag, 'a') as fh:
        fh.write('pw = %g\nf3 = %g\nf90 = %g\npk = %g\ng = %g\n' % (7e-5 * (1 + 0.01 * rng.standard_normal()), f3, f0, mag.max(), mag[0]))
    with open('curves_%s.txt' % tag, 'a') as fh:
        for i in range(len(f)):
            fh.write('%g %g %g %g\n' % (f[i], mag[i], f[i], ph[i]))
    time.sleep(0.06)
