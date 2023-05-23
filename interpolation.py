import numpy as np
import matplotlib.pyplot as plt

class BSpline:
    def __init__(self, t, c, d):
        """
        t = knots
        c = bspline coeff
        d = bspline degree
        """
        self.t = t
        self.c = c
        self.d = d
        assert self.is_valid()

    def is_valid(self) -> bool:
        if len(self.t) <= len(self.c):
            return False
        if (len(self.t) - len(self.c) - 1) == self.d:
            return True
        return False

    def bases(self, x, k, i):
        if k == 1:
            if (self.t[i] <= x) and (x < self.t[i+1]):
                return 1
            return 0
        if (x < self.t[i]) or (x >= self.t[i+k]):
            return 0
        return self.w(x,k-1,i) * self.bases(x,k-1,i) + (1 - self.w(x,k-1,i+1)) * self.bases(x,k-1,i+1)

    def w(self,x,k,i):
        if self.t[i+k] == self.t[i]:
            return 0
        return (x - self.t[i])/(self.t[i+k]-self.t[i])


    def interp(self, x):
        return sum([self.c[i]*self.bases(x,self.d+1,i) for i in range(len(self.c))])

#def interpolate(n_frames,)

def interpolate(keyframes,degree = 3,sub_sample=2):
    control_ys = keyframes[::sub_sample]
    n = len(control_ys)-1
    m = n+1+degree
    t = [0] * (degree+1) + np.linspace(0,1,(n-degree) + 2)[1:-1].tolist() + [1] * (degree+1)
    spline = BSpline(t, control_ys, degree)
    out_ys = []
    out_xs = np.linspace(0,1,len(keyframes)+1)[:-1]
    for value in out_xs:
        out_ys.append(spline.interp(value))
    return np.array(out_ys)


if __name__ == '__main__':
    #n_knots = 6
    #t = list(range(n_knots))
    #n_frames = 7
    #t = [0]*3 + list(range(1,n_frames-2)) + [n_frames]*3
    keyframes = [0,0,0,0,0,0,0.01,0.01,0.02,0.03,0.04,0.05,0.06]
    plt.plot(interpolate(keyframes))
    plt.show()
    exit()
    degree = 3
    #t = [0,0,0,1,2,3,4,6,6,6]
    control_ys = [1,0,0,1,1,0,-1,-2,0,2,0] # set some control colors. change this.
    n = len(control_ys)-1
    m = n+1+degree
    t = [0] * (degree+1) + np.linspace(0,1,(n-degree) + 2)[1:-1].tolist() + [1] * (degree+1)
    #control_xs = np.linspace(min(t),max(t),len(control_ys)+2)[1:-1]
    print(t)

    #plt.scatter(control_xs,control_ys)
    
    d = len(t) - len(control_ys) - 1 # set the degree.  change this.
    print("d =",d)
    spline = BSpline(t, control_ys, d)
    # now interpolate at some value
    out_ys = []
    out_xs = np.linspace(0,1,len(control_ys)*2)[:-1]
    for value in out_xs:
        out_ys.append(spline.interp(value))
    print(out_xs,out_ys)
    plt.plot(out_ys)
    plt.show()