#!/bin/bash
# transistor-level bias probe: beta multiplier, DC temperature sweep
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd /foss/designs/gmc-filter || exit 1
RL=${RL:-65}
: > ptat_probe.txt
for C in tt ss ff; do for V in 1.62 1.8 1.98; do
cat > pp_net.spice <<NET
beta multiplier probe
V1 VDD 0 DC $V
Vsns nr 0 DC 0
XMP1 n1 pg VDD VDD sky130_fd_pr__pfet_01v8 w=8 l=2
XMP2 n2 pg VDD VDD sky130_fd_pr__pfet_01v8 w=8 l=2
XM1 n1 n1 0 0 sky130_fd_pr__nfet_01v8 w=2 l=2
XM2 n2 n1 ns 0 sky130_fd_pr__nfet_01v8 w=8 l=2
XR1 ns nr 0 sky130_fd_pr__res_high_po_1p41 w=1.41 l=$RL
Rst VDD n1 5Meg
Rpg n2 pg 1
.nodeset v(n1)=0.8 v(n2)=0.9 v(pg)=0.9
.lib $L $C
.dc temp -40 125 5
.control
run
let ibr = -i(Vsns)
wrdata pp_out.txt ibr v(n1) v(n2)
quit
.endc
.end
NET
ngspice -b pp_net.spice > pp_log.txt 2>&1
python3 - "$C" "$V" <<PY
import numpy as np,sys
try:
    a=np.loadtxt('pp_out.txt')
    T=a[:,0]; I=a[:,1]
    def at(t): return I[np.argmin(abs(T-t))]
    al=np.log(at(85)/at(-20))/np.log(358.15/253.15)
    print('%s %s I(-20)=%.2fu I(27)=%.2fu I(85)=%.2fu alpha=%.2f'%(sys.argv[1],sys.argv[2],at(-20)*1e6,at(27)*1e6,at(85)*1e6,al))
except Exception as e:
    print(sys.argv[1],sys.argv[2],'FAILED',e)
PY
done; done | tee ptat_probe.txt
tail -3 pp_log.txt
