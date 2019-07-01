import numpy as np
from numpy.random import rand
import scipy.optimize as opt
import GMR.InputOutput as io
import matplotlib.pyplot as plt
import os


def A_fano(E, Ef, r, q, A, offset):
    '''
    Absorption measurement fano function.
    Args:
        E: x values
        Ef: peak value
        r: peak width
        q: shape parameter
        A: absorption
        offset: DC offset
    '''
    eps = 2 * (E - Ef) / r
    f = ((eps + q) ** 2) / ((eps ** 2) + 1)
    y = (A * (1 - f)) + offset
    return y


def T_fano(E, Ef, r, q, T, offset):
    '''
    Tranmission measurement fano function.
    Args:
        E: x values
        Ef: peak value
        r: peak width
        q: shape parameter
        T: transmission
        offset: DC offset
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


def A_f_lsq(params, x, y_meas):
    '''
    Absorption least squared fano function
    '''
    y_fano = A_fano(x, *params)
    res_sq = y_fano - y_meas
    return res_sq


def find_peak(wavelength,
              intensity,
              file_name=None,
              root=None,
              save=False):
    '''
    Find peaks function, utilising a fano fit (transmission in this case)
    and a least squares function (again in transmission) to find the best
    set of parameters to fit a fano curve.
    The function finds a random set of guesses between -500 and 500, and
    does this 50 times. It then calculates the optimal parameters based
    on the least squares function, using a cost method. The best parameters
    are where the cost function is lowest.
    Args:
        wavelength: <array> x array
        intensity: <array> y array
    Returns:
        peak: <int/float> y-peak x_coordinate
    '''
    guesses = [2000 * (rand(5) - 0.5) for i in range(50)]
    results = [opt.least_squares(T_f_lsq,
                                 g,
                                 args=(wavelength, intensity))
               for g in guesses]

    r_params = [r.x for r in results]
    r_cost = [r.cost for r in results]

    del results

    best_index = np.argmin(r_cost)
    best_params = r_params[best_index]

    peak = float(wavelength[np.argmax(T_fano(wavelength, *best_params))])

    if save:
        fit_fig, fit_ax = plt.subplots()
        fit_ax.plot(wavelength,
                    intensity,
                    label='Raw Data')
        fit_ax.plot(wavelength,
                    T_fano(wavelength, *best_params),
                    label='Curve fit')
        fit_ax.legend()
        out_path = os.path.join(root, 'Fit_Graphs')
        io.check_dir_exists(out_path)
        plt.savefig(os.path.join(out_path, f'{file_name}_fit.png'))
        fit_fig.clf()
        plt.close(fit_fig)

    return peak


def peak_shift(file,
              zero_file):
    '''
    Reads in the wavelength, intensity and file name parameters from
    an in-file and the sensor file. Then uses the FindPeaks function to
    determine the x coordinates of a resonant peak within both files. Using
    this it calculates a peak shift. Outputs the time, peak and peak shift
    values.
    Args:
        file: <string> file path to image
        zero_file: <string> file path to sensor background image
    Returns:
        time_stamp: <string> end of file name which gives time step at which
                    measurement occurred
        peak: <int/float> y-peak x-coordinate
        peak_shift: <int/float> y-peak x-coordinate as a shift from zero peak
    '''
    wavelength, intensity, file_name = io.array_in(file_path=file)
    wav_naught, int_naught, zero_name = io.array_in(file_path=zero_file)

    file_peak = find_peak(wavelength=wavelength,
                          intensity=intensity)
    zero_peak = find_peak(wavelength=wav_naught,
                          intensity=int_naught)
    time_stamp = (file_name.split('_')[::-1])[0]

    if len(file_peak) == 0:
        peak = None
        peak_shift = None
    else:
        peak = float(file_peak)
        peak_shift = float(file_peak) - float(zero_peak)

    return time_stamp, peak, peak_shift
