v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 730 -380 730 -350 {lab=0}
N 180 -640 180 -620 {lab=VDD}
N 40 -280 410 -460 {lab=#net1}
N 370 -410 410 -440 {lab=#net2}
N 410 -420 410 -230 {lab=#net3}
N 180 -230 410 -230 {lab=#net3}
N 710 -460 730 -440 {lab=#net4}
C {vsource.sym} 40 -250 0 0 {name=Vinp value="0.9 ac 1" savecurrent=false}
C {vsource.sym} 180 -590 0 0 {name=V1 value=1.8 savecurrent=false}
C {gnd.sym} 180 -560 0 0 {name=l3 lab=0}
C {gnd.sym} 40 -220 0 0 {name=l4 lab=0}
C {vsource.sym} 370 -380 0 0 {name=Vinn value=0.9 savecurrent=false}
C {vsource.sym} 180 -200 0 0 {name=Vbias_tail_v value=0.7 savecurrent=false}
C {gnd.sym} 180 -170 0 0 {name=l6 lab=0}
C {code.sym} 40 -480 0 0 {name=s2 only_toplevel=false value=".lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt"
}
C {code.sym} 40 -620 0 0 {name=s1 only_toplevel=false value=".ac dec 20 1 1G"}
C {capa.sym} 730 -410 0 0 {name=C1
m=1
value=10p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 730 -350 0 0 {name=l8 lab=0}
C {gnd.sym} 370 -350 0 0 {name=l1 lab=0}
C {ota_core.sym} 560 -440 0 0 {name=x1}
C {vdd.sym} 180 -640 0 0 {name=l2 lab=VDD}
