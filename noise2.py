import numpy as np
n=np.loadtxt('curves_noise_pt.txt'); f=n[:,0]
I=np.trapezoid if hasattr(np,'trapezoid') else np.trapz
for lab,c in (('output',1),('input-referred',3)):
    v=n[:,c]; m=f<=1.6e6
    print('%s: rms 1k-10MHz %.1f uV, 1k-1.6MHz %.1f uV | density at 1k %.0f, 100k %.0f, 1M %.0f nV/rtHz'%(lab,1e6*np.sqrt(I(v**2,f)),1e6*np.sqrt(I(v[m]**2,f[m])),*[1e9*np.interp(x,f,v) for x in (1e3,1e5,1e6)]))
o=1e6*np.sqrt(I(n[f<=1.6e6,1]**2,f[f<=1.6e6]))*1e-6
print('SNR for 100 mV peak sine at output (1k-1.6MHz noise): %.1f dB'%(20*np.log10(0.1/np.sqrt(2)/o)))
