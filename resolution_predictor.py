import random
import string
import argparse
from scipy import optimize

from settings import
from helper_functions import multi_expo_gauss_curve
from fitter_helper_functions import (load_fit_guess, load_chromatography_data, extract_background,
                                     process_guess_and_bounds, calc_individual_peaks, plot_and_save_curves,
                                     save_simulated_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', help='output filename')
    parser.add_argument('--parameters', help='path to peak parameters')
    args = parser.parse_args()
    filename = args.filename if args.filename is not None else ''.join(random.choice(string.lowercase) for x in range(8))
    parameters = args.parameters if args.parameters is not None else PARAMETERS_PATH

    guesses, bounds = process_guess_and_bounds(guess_path)

    data = load_chromatography_data(data_path)
    background = extract_background([val for index, val in enumerate(guesses) if index%4==0], data)

    params, err = optimize.curve_fit(multi_expo_gauss_curve,
                                     [x for x, _ in data],
                                     [y-background for _, y in data],
                                     p0=guesses,
                                     bounds=bounds)
    curves, translated_params = calc_individual_peaks(data, params, background)
    height = sorted([val for index, val in enumerate(params) if index%4 ==0])[1]/3
    plot_and_save_curves(filename, data, background, params, height)
    save_simulated_data(filename, data, background, translated_params, curves)
