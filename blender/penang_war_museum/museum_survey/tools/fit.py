import cmath, math, json
# sketch pixel (x,y down) -> real ENU metres
ctrl = [("Information & ticketing", (545,455), (2.8,-17.4)),
        ("Cafeteria", (395,445), (25.5,-12.5)),
        ("Souvenir", (560,400), (4.6,-24.3)),
        ("Gate (path below ticketing)", (525,495), (0.0,0.0)),
        ("#25 Canon firing bay = gun emplacement", (493,240), (66.6,-105.6))]
z = [complex(s[0], -s[1]) for _,s,_ in ctrl]; w = [complex(*r) for _,_,r in ctrl]
zm = sum(z)/len(z); wm = sum(w)/len(w)
a = sum((wi-wm)*(zi-zm).conjugate() for zi,wi in zip(z,w)) / sum(abs(zi-zm)**2 for zi in z)
b = wm - a*zm
def s2r(x,y): r = a*complex(x,-y)+b; return (r.real, r.imag)
print("scale m/sketch-px", round(abs(a),3), "rotation deg (CCW)", round(math.degrees(cmath.phase(a)),1))
for n,s,r in ctrl:
    p=s2r(*s); print(f"  {n:42s} fit=({p[0]:6.1f},{p[1]:6.1f}) real=({r[0]:6.1f},{r[1]:6.1f}) err={math.dist(p,r):5.1f} m")
for n,s,r in [("CHECK B15 blue barrack vs #7 British other ranks 1",(648,285),(-1.1,-70.7)),
              ("CHECK B09 walkway end vs #29 tunnel",(490,292),(91.2,-87.1))]:
    p=s2r(*s); print(f"  {n:50s} fit=({p[0]:6.1f},{p[1]:6.1f}) real=({r[0]:6.1f},{r[1]:6.1f}) d={math.dist(p,r):5.1f}")
json.dump({"a":[a.real,a.imag],"b":[b.real,b.imag]}, open(__file__.replace("fit.py","transform.json"),"w"))
