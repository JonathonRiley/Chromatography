import random
import string
import argparse
import numpy as np

from settings import RESOLUTION_PATH
from resolution_helper_functions import (load_peak_parameters, build_xrange, calc_tailing_factors, calc_resolution,
                                         save_data, make_plot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', help='output filename')
    parser.add_argument('--parameters', help='path to peak parameters')
    args = parser.parse_args()
    filename = args.filename if args.filename is not None else ''.join(random.choice(string.ascii_lowercase) for x in range(8))
    parameters_path = args.parameters if args.parameters is not None else RESOLUTION_PATH

    peak_parameters = load_peak_parameters(parameters_path)
    xrange = build_xrange(peak_parameters)
    lambdas = list(np.linspace(0.5,0.98,25)) + list(np.linspace(1,50,246))
    peak1_lambdas, peak1_tailings, peak2_tailings = calc_tailing_factors(peak_parameters, lambdas, xrange)
    resolutions, curves = calc_resolution(xrange, peak_parameters, peak1_lambdas)
    save_data(xrange, curves, peak1_tailings, resolutions, filename)
    make_plot(peak1_tailings, resolutions, filename)