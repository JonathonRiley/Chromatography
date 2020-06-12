import csv
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from math import ceil

from settings import XSTEP, TAU_STEP
from helper_functions import expo_gauss_curve, find_asym


def load_data(path):
    with open(f"input/{path}", 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')
        _ = next(csv_reader)
        return [[label,
                 float(mu),
                 float(w),
                 float(sigma),
                 float(peak),
                 float(tailing)]
                for label, mu, w, sigma, peak, tailing in csv_reader]


def make_noise(xpoints):
    return [random.randint(1,100)/5000 for _ in xpoints]


def find_tau_for_tailing(xrange, mu, sigma, peak, tailing):
    test_range = [-10+0.002*x for x in range(10001)]
    valstep = 0.01
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
                val += 0.25
            else:
                val += 1
        except OverflowError:
            continue
    reduced_tails = np.array(tailing_factors) - tailing
    f = interpolate.UnivariateSpline(vals_tried, reduced_tails, s=0)
    curve = expo_gauss_curve(xrange, mu, sigma, peak, f.roots()[0])
    tailing_actual = find_asym(xrange, curve)
    return f.roots()[0], tailing_actual, tailing_actual-tailing


def find_tailing(xrange, mu, sigma, peak, tailings):
    lambda_step = 0.01
    lambda_to_try = [x*lambda_step for x in range(1, int(60/lambda_step)+1)]
    asyms = []
    for lamb in lambda_to_try:
        try:
            asyms.append(find_asym(xrange, expo_gauss_curve(xrange, mu, sigma, peak, lamb)))
        except:
            asyms.append(None)
    calc_tailings = {}
    for tailing in tailings:
        try:
            reduced_tails = np.array(asyms) - tailing
            f = interpolate.UnivariateSpline(lambda_to_try, reduced_tails, s=0)
            curve = expo_gauss_curve(xrange, mu, sigma, peak, f.roots()[0])
            tailing_actual = find_asym(xrange, curve)
            calc_tailings[tailing] = {'lambda':f.roots()[0], 'actual_asym':tailing_actual, 'error':round((tailing_actual-tailing)/tailing*100,2)}
        except:
            calc_tailings[tailing] = {'lambda':None, 'actual_asym':None, 'error':None}
    return calc_tailings


lambs_to_tailing2 = {}
xvals = [-10+0.002*x for x in range(10001)]
for sigma in [x/100 for x in range(1,101)]:
    lambs_to_tailing2[sigma] = find_tailing(xvals, 0, sigma, 1, [1+x/100 for x in range(1,80)])


def avg(lst):
    return sum(lst) / len(lst)


def generate_curves(data):
    x_max = max([vals[1] for vals in data]) + 5
    data_points = ceil(x_max/XSTEP)+1
    xrange = [x*XSTEP for x in range(0, int(data_points))]
    peak_curves = [["noise", 0, 0, make_noise(xrange)]]
    peak_heights = [vals[-2] for vals in data if vals[0]!="Main"]
    sum_heights = sum(peak_heights)
    main_peak_height = 100 - sum_heights
    for peak in data:
        if peak[0] == "Main":
            peak[-2] = main_peak_height
        lamb, tailing, tailing_error, curve = find_tau_for_tailing(xrange, peak[1], peak[3], peak[4], peak[5])
        peak_curves.append([peak[0], tailing, tailing_error, curve])
    sum_peak = [sum(item) for item in zip(*[curve for name, tailing, error, curve in peak_curves[1:]])]
    peak_curves.append(["total",
                        avg([peak[1] for peak in peak_curves[1:]]),
                        avg([peak[2] for peak in peak_curves[1:]]),
                        np.array(sum_peak) + np.array(peak_curves[0][-1])
                        ])
    return xrange, peak_curves


def plot_and_save_curves(xrange, data, curves, filename):
    max_height = max(curves[-1][-1])
    peak_heights = [peak[-2] for peak in data]
    sorted_peak_heights = sorted(peak_heights, reverse=True)
    plt.plot(xrange, curves[-1][-1]*max(peak_heights)/max_height)
    plt.xlabel('Time (min)')
    plt.ylabel('Response (%)')
    plt.title('Simulated Response')
    plt.ylim((0, sorted_peak_heights[1]*1.1))
    for index, peak in enumerate(data):
        peak_height = max(curves[index+1][-1])*max(peak_heights)/max_height
        if peak_height < sorted_peak_heights[1]*1.1:
            plt.text(peak[1], peak_height+0.01, peak[0])
        else:
            plt.text(peak[1]-2.5, 0.2, peak[0])
    plt.savefig(f"output/{filename}.jpg")


def save_simulated_data(xrange, data, curves, filename):
    with open(f'output/{filename}.txt', 'w') as file:
        file.write(f"Peak label,{','.join([str(peak[0]) for peak in curves])}\n")
        file.write(f"t (min), ,{','.join([str(peak[1]) for peak in data])}\n")
        file.write(f"w (min), ,{','.join([str(peak[2]) for peak in data])}\n")
        file.write(f"s (min), ,{','.join([str(peak[3]) for peak in data])}\n")
        file.write(f"response (%), ,{','.join([str(peak[4]) for peak in data])}\n")
        file.write(f"tailing_factor,{','.join([str(peak[1]) for peak in curves])}\n")
        file.write(f"tailing_errors,{','.join([str(peak[2]) for peak in curves])}\n")
        for index, x in enumerate(xrange):
            row_str = [str(x)]
            for peak in curves:
                row_str.append(str(peak[-1][index]))
            file.write(','.join(row_str)+'\n')
