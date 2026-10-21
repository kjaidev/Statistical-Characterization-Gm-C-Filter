#!/bin/bash
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
cat > ac_nom.cir <<'X'
.control
ac dec 40 100k 10Meg
let mg=db(v(vo2))
let pg=180/pi*cph(v(vo2))
wrdata @CURV@ mg pg
.endc
X
rm -f curves_ac_nom.txt
sed -e "s#@CURV@#$D/curves_ac_nom.txt#" ac_nom.cir > ac_run.cir
sed -e "s#^.lib .*#.lib $L tt#" -e "s#^V1 VDD 0 .*#V1 VDD 0 1.8#" -e "s#^.include .*#.include $D/ac_run.cir#" -e "s#^.param .*#.param iref=12u rt=1.48 alpha=0.6#" gmc_pt.spice > net_ac.spice
sed -i "1a .temp 27" net_ac.spice
ngspice -b net_ac.spice > fin_logs/ac_nom.log 2>&1
ls -l curves_ac_nom.txt || tail -5 fin_logs/ac_nom.log
