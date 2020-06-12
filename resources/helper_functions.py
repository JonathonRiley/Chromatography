import numpy as np
from math import sqrt, exp
from scipy import special


def expo_gauss_point(x, mu, sigma, peak, lamb):
    return float(peak*lamb/2 * special.erfc((mu+lamb*sigma**2-x)/(sqrt(2)*sigma)) * exp(lamb/2*(2*mu +lamb*sigma**2 -2*x)))


def expo_gauss_curve(xpoints, mu, sigma, peak, lamb):
    return [expo_gauss_point(x,mu,sigma,peak, lamb) for x in xpoints]


def multi_expo_gauss_curve(xpoints, *params):
    yvals = []
    for x in xpoints:
        y = 0
        for i in range(0,len(params),4):
            mu = params[i]
            sigma = params[i+1]
            peak = params[i+2]
            lamb = params[i+3]
            y += expo_gauss_point(x, mu, sigma, peak, lamb)
        yvals.append(y)
    return yvals


def find_nearest(xrange, array, value):
    array = np.asarray(array)
    max_idx = array.argmax()
    left_idx = (np.abs(np.asarray(array[:max_idx]) - value)).argmin()
    right_idx = (np.abs(np.asarray(array[max_idx:]) - value)).argmin()+max_idx
    return xrange[left_idx], xrange[max_idx], xrange[right_idx]


def find_asym(xrange, array):
    left, middle, right = find_nearest(xrange, array, max(array)/20)
    return (right-left)/(2*(middle-left))


def graph_zoom(self, incr):
    y_vals = [y for _, y in self.data]
    ymin = min(y_vals)
    self.zoom += incr
    i = 0
    while i <= self.zoom:
        local_max_index = y_vals.index(max(y_vals))
        for ii in range(local_max_index-75,local_max_index+75):
            y_vals[ii] = 0
        i += 1
        ymax = self.data[local_max_index][1]
    ydelta = ymax - ymin
    self.ymin = ymin-0.05*ydelta
    self.ymax = ymax+0.1*ydelta
    self.ax.set_ylim([self.ymin, self.ymax])
    self.canvas.draw()