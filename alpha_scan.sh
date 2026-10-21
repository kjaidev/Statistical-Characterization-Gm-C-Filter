#!/bin/bash
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D; mkdir -p fin_logs
cat > ac_meas.cir <<'X'
.control
op
ac dec 100 100k 10Meg
meas ac f3 when vdb(vo2)=-3 fall=1
meas ac f90 when vp(vo2)=-1.5708 fall=1
quit
.endc
X
echo "alpha corner T f3_MHz Q" > alpha_scan.txt
for A in 0.6 1.0; do for C in tt ss ff sf fs; do for T in -20 27 85; do
 sed -e "s#^.lib .*#.lib $L $C#" -e "s#^V1 VDD 0 .*#V1 VDD 0 1.8#" -e "s#^.include .*#.include $D/ac_meas.cir#" -e "s#^.param .*#.param iref=12u rt=1.48 alpha=$A#" gmc_pt.spice > net_s.spice
 sed -i "1a .temp $T" net_s.spice
 ngspice -b net_s.spice > fin_logs/s.log 2>&1
 f3=$(grep -m1 '^f3' fin_logs/s.log | awk '{print $3}'); f90=$(grep -m1 '^f90' fin_logs/s.log | awk '{print $3}')
 echo "$A $C $T $f3 $f90" | awk '{u=($4/$5)^2; printf "%s %s %s %.4f %.4f\n",$1,$2,$3,$4/1e6,1/sqrt((2-(1-u)^2)/u)}' >> alpha_scan.txt
done; done; done
cat alpha_scan.txt
