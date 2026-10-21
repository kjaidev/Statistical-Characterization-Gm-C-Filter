#!/bin/bash
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
for V in 1.62 1.68 1.74 1.80 1.86 1.92 1.98; do
  sed -e "s#^.lib .*#.lib $L tt#" -e "s#^V1 VDD 0 .*#V1 VDD 0 $V#" -e "s#^.include .*#.include $D/a4.cir#" -e "s#^.param .*#.param iref=12u rt=1.48 alpha=0.6#" gmc_pt.spice > a4_net.spice
  sed -i "1a .temp 27" a4_net.spice
  ngspice -b a4_net.spice > a4_$V.log 2>&1
  echo "=== VDD=$V"
  grep -E "^(v\(|f3|f90)" a4_$V.log
done
