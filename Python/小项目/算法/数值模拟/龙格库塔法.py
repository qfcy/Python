G_const=1;M=100000
def G(r):
    return G_const*M/r**2 # 引力公式的变形

h=100;v=t=0
dt=0.01
surface=1
while h>surface: #1为天体的半径，h到了1表示坠落到了天体表面
    t+=dt
    v1=v
    g1=G(h) # 当前的加速度g
    temp_v=v+g1*dt
    temp_h=h-(v+temp_v)/2*dt
    g2=G(temp_h) # 下一个状态预测的加速度g
    v+=(g1+g2)/2*dt
    h-=(v1+v)/2*dt
    
    print("%.6g: %.6g %.6g"%(t,v,h))
print("坠落用时:",t)