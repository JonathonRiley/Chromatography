import random
import string
import argparse
from scipy import optimize

from settings import GUESS_PATH, CHROMATOGRAPHY_PATH
from helper_functions import multi_expo_gauss_curve
from fitter_helper_functions import (load_fit_guess, load_chromatography_data, extract_background,
                                     process_guess_and_bounds, calc_individual_peaks, plot_and_save_curves,
                                     save_simulated_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', help='output filename')
    parser.add_argument('--guess_path', help='path to guesses')
    parser.add_argument('--data_path', help='path to data for fitting')
    args = parser.parse_args()
    filename = args.filename if args.filename is not None else ''.join(random.choice(string.ascii_lowercase) for x in range(8))
    guess_path = args.guess_path if args.guess_path is not None else GUESS_PATH
    data_path = args.data_path if args.data_path is not None else CHROMATOGRAPHY_PATH

    raw_guesses = load_fit_guess(guess_path)
    guesses, bounds = process_guess_and_bounds(raw_guesses)

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
