#!/bin/bash
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
mkdir -p calib_logs
for I in 11u 12u 13u 14u; do
 for R in 1.4 1.6 1.8 2.0 2.2; do
  sed -e "s#^.lib .*#.lib $L tt#" -e "s#^V1 VDD 0 .*#V1 VDD 0 1.8#" -e "s#^.include .*#.include $D/calib.cir#" -e "s#^.param .*#.param iref=$I rt=$R#" gmc_cm.spice > calib_net.spice
  sed -i "1a .temp 27" calib_net.spice
  ngspice -b calib_net.spice > calib_logs/c_${I}_${R}.log 2>&1
  echo "ran $I $R"
 done
done
