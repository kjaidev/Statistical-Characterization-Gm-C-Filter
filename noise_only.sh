#!/bin/bash
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
mkdir -p fin_logs
rm -f curves_noise_pt.txt
sed -e "s#@CURV@#$D/curves_noise_pt.txt#" noise.cir > noise_run.cir
sed -e "s#^.lib .*#.lib $L tt#" -e "s#^V1 VDD 0 .*#V1 VDD 0 1.8#" -e "s#^.include .*#.include $D/noise_run.cir#" -e "s#^.param .*#.param iref=12u rt=1.48 alpha=0.6#" gmc_pt.spice > net_noise.spice
sed -i "1a .temp 27" net_noise.spice
ngspice -b net_noise.spice > fin_logs/noise.log 2>&1
ls -l curves_noise_pt.txt 2>/dev/null || echo "no noise curve written"
echo ALLDONE
