#!/bin/bash
# nominal (tt, no mismatch) f3/Q/P vs temperature for several alpha
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
mkdir -p calib_pt_logs
for A in 0.6 0.8 1.0 1.2 1.4; do
 for T in -20 27 85; do
  sed -e "s#^.lib .*#.lib $L tt#" -e "s#^V1 VDD 0 .*#V1 VDD 0 1.8#" -e "s#^.include .*#.include $D/calib.cir#" -e "s#^.param .*#.param iref=12u rt=1.48 alpha=$A#" gmc_pt.spice > calibpt_net.spice
  sed -i "1a .temp $T" calibpt_net.spice
  ngspice -b calibpt_net.spice > calib_pt_logs/a${A}_T${T}.log 2>&1
  echo "ran alpha=$A T=$T"
 done
done
