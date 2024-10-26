h=100;v=t=0
g=10
dt=0.01
while h>0:
    t+=dt
    v1=v
    v+=g*dt
    h-=(v1+v)/2*dt
    print("%.6g: %.6g %.6g"%(t,v,h))
print("坠落用时:",t)