import numpy as np
from numpy.random import rand
import scipy.optimize as opt


def A_fano(E, Ef, r, q, A, offset):
    '''
    Args:
        E: <array> x values
        Ef: <int/float> peak
        r: <int/float> peak width
        q: <int/float> shape parameter
        A: <int/float> absorption
        offset: <int/float> DC offset
    Returns:
        y: <array> fano curve fit
    '''
    eps = 2 * (E - Ef) / r
    f = ((eps + q) ** 2) / ((eps ** 2) + 1)
    y = (A * (1 - f)) + offset
    return y


def A_f_lsq(params, x, y_meas):
    '''
    Absorption least squared fano function
    '''
    y_fano = A_fano(x, *params)
    res_sq = y_fano - y_meas
    return res_sq


def T_fano(E, Ef, r, q, T, offset):
    '''
    Args:
        E: <array> x values
        Ef: <int/float> peak
        r: <int/float> peak width
        q: <int/float> shape parameter
        T: <int/float> transmission
        offset: <int/float> DC offset
    Returns:
        y: <array> fano curve fit
    '''
    eps = 2 * (E - Ef) / r
    f = ((eps + q) ** 2) / ((eps ** 2) + 1)
    y = (T * f) + offset
    return y


def T_f_lsq(params, x, y_meas):
    '''
    Transmission least squared fano function
    '''
    y_fano = T_fano(x, *params)
    res_sq = y_fano - y_meas
    return res_sq


def best_params(x, y):
    '''
    Best params function uses numpy random guess to choose 50 sets of 5 random
    numbers to fill out the fano parameters, between the range of -10000 and
    10000. It then uses a optimise least squares function to determine the
    values of the parameters with the lowest cost function, finds the best
    index within that array and returns the best possible guessed parameters.
    Args:
        x: <array> x array
        y: <array> y array
    Returns:
        best_params: <array> 5 item array containing best fano parameters
    '''
    guesses = [2000 * (rand(5) - 0.5) for i in range(300)]
    results = [opt.least_squares(T_f_lsq, g, args=(x, y)) for g in guesses]

    r_params = [r.x for r in results]
    r_cost = [r.cost for r in results]

    del results

    best_index = np.argmin(r_cost)
    best_params = r_params[best_index]

    return best_params


def find_fano(x, y,
              best_params):
    '''
    Find peaks function, utilising a fano fit (transmission in this case)
    and a least squares function (again in transmission) to find the best
    set of parameters to fit a fano curve.
    The function finds a random set of guesses between -500 and 500, and
    does this 50 times. It then calculates the optimal parameters based
    on the least squares function, using a cost method. The best parameters
    are where the cost function is lowest.
    Args:
        x: <array> x array
        y: <array> y array
        best_params: <array> optimised random guesses
        peak_wavelength: <int/float> previously guessed peak wavelength
    Returns:
        peak: <int/float> y-peak x_coordinate
    '''
    popt, _ = opt.curve_fit(T_fano, x, y, p0=best_params)
    peak_wavelength = popt[0]
    return popt, peak_wavelength


def find_peaks(x, y):
    '''
    Emergency Interpolate
    '''
    x_range = np.arange(min(x), max(x), 0.001)
    interp_y = np.interp(x=x_range, xp=x, fp=y)
    peak = float(x_range[np.argmax(interp_y)])
    return peak
