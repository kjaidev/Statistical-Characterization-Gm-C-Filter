v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 300 -290 480 -290 {lab=#net1}
N 390 -290 390 -260 {lab=#net1}
N 260 -410 300 -410 {lab=#net2}
N 260 -440 260 -410 {lab=#net2}
N 260 -520 260 -440 {lab=#net2}
N 260 -520 440 -520 {lab=#net2}
N 440 -520 440 -440 {lab=#net2}
N 300 -410 300 -350 {lab=#net2}
N 480 -410 480 -350 {lab=OUT1}
N 300 -580 300 -470 {lab=VDD}
N 300 -580 380 -580 {lab=VDD}
N 380 -580 480 -580 {lab=VDD}
N 480 -580 480 -470 {lab=VDD}
N 390 -200 390 -170 {lab=0}
N 480 -380 520 -380 {lab=OUT1}
N 40 -320 40 -280 {lab=IN1+}
N 180 -620 380 -620 {lab=VDD}
N 380 -620 380 -580 {lab=VDD}
N 370 -410 390 -410 {lab=IN1-}
N 390 -410 390 -320 {lab=IN1-}
N 390 -320 440 -320 {lab=IN1-}
N 40 -320 260 -320 {lab=IN1+}
N 180 -230 350 -230 {lab=Vbias_tail}
N 300 -320 490 -230 {lab=0}
N 480 -320 490 -320 {lab=0}
N 490 -320 490 -230 {lab=0}
N 390 -230 490 -230 {lab=0}
N 300 -440 380 -440 {lab=VDD}
N 380 -580 380 -440 {lab=VDD}
N 480 -440 530 -440 {lab=VDD}
N 530 -600 530 -440 {lab=VDD}
N 400 -600 530 -600 {lab=VDD}
N 380 -580 400 -600 {lab=VDD}
N 520 -380 730 -440 {lab=OUT1}
N 730 -380 730 -350 {lab=0}
C {sky130_fd_pr/nfet_01v8.sym} 280 -320 0 0 {name=M1
W=4
L=0.5
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 460 -320 0 0 {name=M2
W=4
L=0.5
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 280 -440 0 0 {name=M3
W=8
L=0.5
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 460 -440 0 0 {name=M4
W=8
L=0.5
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 370 -230 0 0 {name=M5
W=6
L=1
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {vdd.sym} 380 -580 0 0 {name=l1 lab=VDD}
C {gnd.sym} 390 -170 0 0 {name=l2 lab=0}
C {ipin.sym} 230 -320 0 0 {name=p1 lab=IN1+}
C {ipin.sym} 420 -320 0 0 {name=p2 lab=IN1-
}
C {opin.sym} 520 -380 0 0 {name=p3 lab=OUT1}
C {ipin.sym} 310 -230 0 0 {name=p4 lab=Vbias_tail}
C {vsource.sym} 40 -250 0 0 {name=Vinp value="0.9 ac 1" savecurrent=false}
C {vsource.sym} 180 -590 0 0 {name=V1 value=1.8 savecurrent=false}
C {gnd.sym} 180 -560 0 0 {name=l3 lab=0}
C {gnd.sym} 40 -220 0 0 {name=l4 lab=0}
C {vsource.sym} 370 -380 0 0 {name=Vinn value=0.9 savecurrent=false}
C {gnd.sym} 370 -350 0 0 {name=l5 lab=0}
C {vsource.sym} 180 -200 0 0 {name=Vbias_tail_v value=0.7 savecurrent=false}
C {gnd.sym} 180 -170 0 0 {name=l6 lab=0}
C {code.sym} 40 -480 0 0 {name=s2 only_toplevel=false value=".lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt"
}
C {gnd.sym} 490 -230 0 0 {name=l7 lab=0}
C {code.sym} 40 -620 0 0 {name=s1 only_toplevel=false value=".ac dec 20 1 1G"}
C {capa.sym} 730 -410 0 0 {name=C1
m=1
value=10p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 730 -350 0 0 {name=l8 lab=0}
