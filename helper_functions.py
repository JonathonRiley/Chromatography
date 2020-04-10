import csv
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate, special, interpolate
from math import sqrt, exp, ceil

from settings import XSTEP, TAU_STEP


def load_data(path):
    with open(path, 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')
        _ = next(csv_reader)
        return [[label,
                 float(mu),
                 float(w),
                 float(sigma),
                 float(peak),
                 float(tailing)]
                for label, mu, w, sigma, peak, tailing in csv_reader]


def expo_gauss_curve(xpoints, mu, sigma, peak, lamb):
    intensity = lamb/2
    curve = [np.nan_to_num(intensity * special.erfc((mu+lamb*sigma**2-x)/(sqrt(2)*sigma)) * exp(intensity*(2*mu +lamb*sigma**2 -2*x))) for x in xpoints]
    curve_max = max(curve)
    return [val*peak/curve_max for val in curve]


def make_noise(xpoints):
    return [random.randint(1,100)/20000 for _ in xpoints]


def find_nearest(xrange, array, value):
    array = np.asarray(array)
    max_idx = array.argmax()
    left_idx = (np.abs(np.asarray(array[:max_idx]) - value)).argmin()
    right_idx = (np.abs(np.asarray(array[max_idx:]) - value)).argmin()+max_idx
    return xrange[left_idx], xrange[max_idx], xrange[right_idx]


def find_asym(xrange, array):
    left, middle, right = find_nearest(xrange, array, max(array)/20)
    return (right-left)/(2*(middle-left))


def find_tau_for_tailing(xrange, mu, sigma, peak, tailing):
    test_range = [-10+0.01*x for x in range(2001)]
    val = 0.01
    vals_tried = []
    tailing_factors = []
    asym = 100
    while asym > tailing:
        try:
            asym = find_asym(test_range, expo_gauss_curve(test_range, 0, sigma, peak, val))
            tailing_factors.append(asym)
            vals_tried.append(val)
            if val < 1:
                val += 0.01
            elif val < 10:
                val += 1
            else:
                val += 5
        except OverflowError:
            continue
    reduced_tails = np.array(tailing_factors) - tailing
    f = interpolate.UnivariateSpline(vals_tried, reduced_tails, s=0)
    curve = expo_gauss_curve(xrange, mu, sigma, peak, f.roots()[0])
    return f.roots()[0], find_asym(xrange, curve)-tailing, curve


def generate_curves(data):
    x_max = max([vals[1] for vals in data]) + 5
    data_points = ceil(x_max/XSTEP)+1
    xrange = [x*XSTEP for x in range(0, data_points)]

    peak_curves = [["noise", 0, make_noise(xrange)]]

    peak_heights = [vals[-2] for vals in data if vals[0]!="Main"]
    sum_heights = sum(peak_heights)
    max_height = max(peak_heights)
    main_peak_height = 100 - sum_heights
    for peak in data:
        if peak[0] == "Main":
            peak[-2] = main_peak_height
        lamb, tailing_error, curve = find_tau_for_tailing(xrange, peak[1], peak[3], peak[4], peak[5])
        peak_curves.append([peak[0], tailing_error, curve])

    sum_peak = [sum(item) for item in zip(*[curve for name, error, curve in peak_curves])]
    peak_curves.append(["total", 0, sum_peak])

    return xrange, max_height, peak_curves


def plot_and_save_curves(xrange, data, curves, max_height, filename):
    plt.plot(xrange, curves[-1][-1])
    plt.xlabel('Time (min)')
    plt.ylabel('Response (%)')
    plt.title('Simulated Response')
    plt.ylim((0, max_height*1.1))
    for index, peak in enumerate(data):
        peak_height = max(curves[index+1][-1])
        if peak_height < max_height*1.1:
            plt.text(peak[1], peak_height+0.01, peak[0])
        else:
            plt.text(peak[1]-2.5, 0.2, peak[0])
    plt.savefig(f'output/{filename}.jpg')


def save_simulated_data(xrange, data, curves, filename):
    with open(f'output/{filename}.txt', 'w') as file:
        file.write(f"Peak label,{','.join([str(peak[0]) for peak in data])}\n")
        file.write(f"t (min), ,{','.join([str(peak[1]) for peak in data])}\n")
        file.write(f"w (min), ,{','.join([str(peak[2]) for peak in data])}\n")
        file.write(f"s (min), ,{','.join([str(peak[3]) for peak in data])}\n")
        file.write(f"response (%), ,{','.join([str(peak[4]) for peak in data])}\n")
        file.write(f"tailing_factor, ,{','.join([str(peak[5]) for peak in data])}\n")
        for index, x in enumerate(xrange):
            row_str = [str(x)]
        for peak in curves:
            row_str.append(str(peak[-1][index]))
        file.write(','.join(row_str)+'\n')
