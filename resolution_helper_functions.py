import csv
import numpy as np
import matplotlib.pyplot as plt
from math import ceil


from settings import XSTEP
from helper_functions import multi_expo_gauss_curve, expo_gauss_curve, find_asym


def load_peak_parameters(path):
    with open(f"input/{path}", 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')
        _ = next(csv_reader)
        return [[float(mu),
                 float(sigma),
                 float(response)]
                for mu, sigma, response in csv_reader]


def build_xrange(parameters):
    min_x = min([peak[0] for peak in parameters]) - 10
    max_x = max([peak[0] for peak in parameters]) + 10
    steps = ceil((max_x - min_x)/(XSTEP/10)) + 1
    return np.linspace(min_x, max_x, steps)


def calc_tailing_factors(params, lambdas, xvals):
    mu1 = params[0][0]
    sigma1 = params[0][1]
    response1 = params[0][2]
    mu2 = params[1][0]
    sigma2 = params[1][1]
    response2 = params[1][2]
    peak1_tailings = []
    peak1_lambdas = []
    peak2_tailings = []
    for lamb in lambdas:
        tail1 = find_asym(xvals, expo_gauss_curve(xvals, mu1, sigma1, response1, lamb))
        tail2 = find_asym(xvals, expo_gauss_curve(xvals, mu2, sigma2, response2, lamb))
        if round(tail1,3) not in peak1_tailings:
            peak1_lambdas.append(lamb)
            peak1_tailings.append(round(tail1,3))
            peak2_tailings.append(round(tail2,3))
    return peak1_lambdas, peak1_tailings, peak2_tailings


def parse_params(params, lamb):
    mu1 = params[0][0]
    sigma1 = params[0][1]
    response1 = params[0][2]
    mu2 = params[1][0]
    sigma2 = params[1][1]
    response2 = params[1][2]
    return [mu1, sigma1, response1, lamb, mu2, sigma2, response2, lamb]


def calc_resolution(xrange, params, lambdas_list):
    results = []
    curves = []
    for lamb in lambdas_list:
        params_list = parse_params(params, lamb)
        curve = multi_expo_gauss_curve(xrange, *params_list)
        curves.append(curve)
        deriv = np.gradient(curve)
        changes = [(xrange[index], index) for index in range(1,len(deriv)-1)
                   if (deriv[index]>0>deriv[index+1])
                   or (deriv[index]<0<deriv[index+1])]
        if len(changes) == 3:
            peak1_max = curve[changes[0][1]]
            peak2_max = curve[changes[2][1]]
            valley_min = curve[changes[1][1]]
            results.append(min([peak1_max,peak2_max])-valley_min)
        else:
            results.append(0)
    return results, curves


def save_data(xrange, curves, tailings_list, resolutions, filename):
    with open(f'output/{filename}_curves.csv', 'w') as curves_file:
        curves_file.write(f"t (min),{','.join([str(factor) for factor in tailings_list])}\n")
        for index, xval in enumerate(xrange):
            curves_file.write(f"{xval},{','.join([str(curve[index]) for curve in curves])}\n")
    with open(f'output/{filename}_valleys.csv', 'w') as valleys_file:
        valleys_file.write("tailing factor,valley height\n")
        for tailing, resolution in sorted([item for item in zip(tailings_list,resolutions)],
                                          key=lambda x: x[0]):
            valleys_file.write(f"{tailing},{resolution}\n")


def make_plot(tailing_list, resolutions, filename):
    plt.plot(tailing_list, resolutions)
    plt.xlabel('Tailing Factor')
    plt.ylabel('Valley Height (arb units)')
    plt.title('Valley Height vs Tailing Factor')
    plt.savefig(f'output/{filename}.jpg')
