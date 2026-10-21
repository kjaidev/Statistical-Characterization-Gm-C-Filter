#!/bin/bash
D=/foss/designs/gmc-filter
L=/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice
cd $D
sed -e "s#^.lib .*#.lib $L tt#" \
    -e "/^.include/d" -e "/^\.end[[:space:]]*$/Id" \
    -e "s#^BIref VDD vbn .*#BIref VDD vbn I={iref*pow((TEMP+273.15)/300.15,alpha)}#" -e "s#^BIref3 vaux vbn3 .*#BIref3 vaux vbn3 I={iref*rt*pow((TEMP+273.15)/300.15,alpha)}#" -e "s#temper#TEMP#g" \
    -e "s#^Vinp vin 0 0.9 ac 1#Vinp vin 0 DC 0.9 AC 1#" \
    -e "s#^.param .*#.param iref=12u rt=1.48 alpha=0.6#" gmc_pt.spice > xy_nom.cir
cat >> xy_nom.cir <<'EOT'
.global VDD
.options parser scale=1.0u
.dc Vinp 0.9 0.9 1
.print dc format=noindex v(vbn) v(vbn3) v(vo1) v(vo2)
.end
EOT
sed -i '1a .temp 27' xy_nom.cir
Xyce xy_nom.cir > xy_dc.log 2>&1
echo "--- DC (ngspice: vbn 0.6992 vo1 0.9019 vo2 0.8923)"
cat xy_nom.cir.prn 2>/dev/null | tail -2
grep -i -m5 "error\|fatal" xy_dc.log
