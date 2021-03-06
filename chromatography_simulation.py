import random
import string
import argparse

from settings import PARAMETERS_PATH
from simulation_helper_functions import load_data, generate_curves, plot_and_save_curves, save_simulated_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', help='foo help')
    parser.add_argument('--parameters', help='path to peak parameters')
    args = parser.parse_args()
    filename = args.filename if args.filename is not None else ''.join(random.choice(string.ascii_lowercase) for x in range(8))
    parameters = args.parameters if args.parameters is not None else PARAMETERS_PATH

    data = load_data(parameters)
    xrange, peak_curves = generate_curves(data)
    plot_and_save_curves(xrange, data, peak_curves, filename)
    save_simulated_data(xrange, data, peak_curves, filename)
