import csv
import numpy as np
import matplotlib.pyplot as plt

from resources.helper_functions import expo_gauss_curve, multi_expo_gauss_curve, find_asym

def load_fit_guess(path):
    with open(f"input/{path}", 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')
        _ = next(csv_reader)
        return [[float(mu),
                 float(sigma),
                 float(response)]
                for mu, sigma, response in csv_reader]

def load_chromatography_data(path):
    with open(f"input/{path}", 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')
        _ = next(csv_reader)
        return [[float(x),
                 float(y)]
                for x, y in csv_reader]

def process_guess_and_bounds(guesses):
    flat_guesses = [val for guess in guesses for val in guess]
    lower_bounds = []
    upper_bounds = []
    for index in range(0,len(flat_guesses),4):
        lower_bounds.append(flat_guesses[index]-1)
        upper_bounds.append(flat_guesses[index]+1)
        lower_bounds.append(0)
        upper_bounds.append(flat_guesses[index+1]*2)
        lower_bounds.append(flat_guesses[index+2]*0.5)
        upper_bounds.append(flat_guesses[index+2]*1.5)
        lower_bounds.append(1)
        upper_bounds.append(20)
    return flat_guesses, (lower_bounds, upper_bounds)


def extract_background(peak_centres, data):
    xvals = [round(x,3) for x, _ in data]
    yvals = [y for _, y in data]
    peak_exclusions = [xvals[xvals.index(round(peak-1.5,3)):xvals.index(round(peak+1.5))] for peak in peak_centres]
    unique_exclusions = set([x for exclusion in peak_exclusions for x in exclusion])
    background_yvals = [yvals[index] for index, x in enumerate(xvals) if x not in unique_exclusions]
    return sum(background_yvals)/len(background_yvals)


def calc_individual_peaks(data, params, background):
    xvals = [x for x, _ in data]
    peak_curves = []
    translated_params = []
    for index in range(0, len(params), 4):
        mu = params[index]
        sigma = params[index+1]
        peak = params[index+2]
        lamb = params[index+3]
        curve = expo_gauss_curve(xvals, mu, sigma, peak, lamb)
        peak_curves.append(curve)
        tailing_factor = find_asym(xvals, curve)
        translated_params.append([mu, sigma, peak, tailing_factor])
    peak_curves.append([background for _ in xvals])
    return peak_curves, translated_params


def plot_and_save_curves(filename, data, background, params, height):
    xvals = [x for x, _ in data]
    plt.plot(xvals, [y for _, y in data])
    plt.plot(xvals, np.asarray(multi_expo_gauss_curve(xvals, *params))+background)
    plt.xlabel('Time (min)')
    plt.ylabel('Response (arb. units)')
    plt.title('Fit Response')
    plt.ylim((0, height*1.1))
    plt.savefig(f"output/{filename}.jpg")


def save_simulated_data(filename, data, background, params, peak_curves):
    with open(f'output/{filename}.txt', 'w') as file:
        file.write(f"parameters,{','.join(['peak'+str(index) for index in range(len(params))])},background,total\n")
        file.write(f"t (min),{','.join([str(peak[0]) for peak in params])}\n")
        file.write(f"s (min),{','.join([str(peak[1]) for peak in params])}\n")
        file.write(f"response (%),{','.join([str(peak[2]) for peak in params])}\n")
        file.write(f"tailing factors,{','.join([str(peak[3]) for peak in params])}\n")
        for index, x in enumerate([x for x, _ in data]):
            row_str = [str(x)]
            sum_val = 0
            for peak in peak_curves:
                row_str.append(str(peak[index]))
                sum_val+=peak[index]
            row_str.append(str(sum_val))
            file.write(','.join(row_str)+'\n')
