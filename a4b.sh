#!/bin/bash
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
for V in 1.62 1.80 1.98; do
  sed -e "s#pfet_01v8 L=0.5 W=8#pfet_01v8 L=1 W=16#g" -e "s#^.lib .*#.lib $L tt#" -e "s#^V1 VDD 0 .*#V1 VDD 0 $V#" -e "s#^.include .*#.include $D/a4.cir#" -e "s#^.param .*#.param iref=12u rt=1.48 alpha=0.6#" gmc_pt.spice > a4b_net.spice
  sed -i "1a .temp 27" a4b_net.spice
  ngspice -b a4b_net.spice > a4b_$V.log 2>&1
  echo "=== PMOS L=1 W=16  VDD=$V"
  grep -E "^(v\(vo1|v\(x1.net2|f3 =|f90 =)" a4b_$V.log
done
