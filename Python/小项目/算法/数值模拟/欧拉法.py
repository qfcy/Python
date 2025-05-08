G_const=1;M=100000
def G(r):
    return G_const*M/r**2 # 引力公式的变形

h=100;v=t=0
dt=0.01
while h>1: #1为天体的半径，h到了1表示坠落到了天体表面
    t+=dt
    #old_v=v
    v+=G(h)*dt
    h-=v*dt
    print("%.6g: %.6g %.6g"%(t,v,h))
print("坠落用时:",t)