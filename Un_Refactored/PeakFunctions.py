import os
from scipy.signal import find_peaks
import GMR.InputOutput as io
import GMR.DataPreparation as dp
import numpy as np
from numpy.random import rand
import scipy.optimize as opt
import matplotlib.pyplot as plt


def A_fano(E, Ef, r, q, A, offset):
    '''
    '''
    eps = 2 * (E - Ef) / r
    f = ((eps + q) ** 2) / ((eps ** 2) + 1)
    y = A * (1 - f) + offset
    return y


def T_fano(E, Ef, r, q, T, offset):
    '''
    '''
    eps = 2 * (E - Ef) / r
    f = ((eps + q) ** 2) / ((eps ** 2) + 1)
    y = T * f + offset
    return y


def f_lsq(params, x, y_meas):
    '''
    '''
    y_fano = T_fano(x, *params)
    #y_fano = A_fano(x, *params)

    res_sq = y_fano - y_meas
    return res_sq


def peaks(x, y, distance, width, xmin, xmax):
    '''
    Utilises the scipy module find_peaks with the possibility to feed in
    specific user-defined parameters such as distance between peaks, width
    of the peaks, the minimum x and maximum x value the user expects the
    peak to be.
    Args:
        x: <array> containing x-axis values such as wavelength
        y: <array> containing y-axis values such as intensity, these are
           the values you expect to find a peak in
        distance: <int> minimum distance between peaks
        width: <int> minimum width of peaks
        xmin: <int> minimum value you expect a peak to occur within the
              x value array, defaults to minimum value within x
        xmax: <int> maximum value you expect a peak to occur within the
              x value array, defaults to maxmimum value within x
    '''
    height = sum(y) / len(y)
    peaks = find_peaks(x=y, height=height, distance=distance, width=width)
    peak_coords = peaks[0]
    X_array = []
    for a in peak_coords:
        x_coord = float(x[a])
        if xmin <= x_coord <= xmax:
            X_array.append(x_coord)
    return X_array


def bg_peaks(file_path, zero_path):
    '''
    Uses ReadInValues function and FindPeaks function to find the peak
    wavelength of each background image, and find the peak wavelength
    shift of each background image compared to the sensor peak (zero
    file). Returns three values, the file_name, the background peak and
    the peak shift value.
    Args:
        file: <string> file path to background image
        zero_file: <string> file path to sensor background image
    '''
    wavelength, intensity, file_name = io.csv_in(file_path=file_path)
    wav_naught, int_naught, file_name = io.csv_in(file_path=zero_path)

#    zero_peak = peaks(x=wav_naught,
#                      y=int_naught,
#                      distance=300,
#                      width=20,
#                      xmin=740,
#                      xmax=800)
#
#    bg_peak = peaks(x=wavelength,
#                    y=intensity,
#                    distance=300,
#                    width=20,
#                    xmin=740,
#                    xmax=800)


    file_guesses = [1000 * (rand(5) - 0.5) for i in range(50)]
    file_results = [opt.least_squares(f_lsq, g, args=(wavelength, intensity))
                    for g in file_guesses]
    file_r_params = [r.x for r in file_results]
    file_r_cost = [r.cost for r in file_results]
    del file_results
    file_best_index = np.argmin(file_r_cost)
    file_best_params = file_r_params[file_best_index]
    #bg_peak = max(T_fano(wavelength, *file_best_params))

    fit_fig, fit_ax = plt.subplots()
    fit_ax.plot(wavelength, intensity, label='Raw Data')
    fit_ax.plot(wavelength, T_fano(wavelength, *file_best_params), label='Curve fit')
    fit_ax.legend()
    plt.show()
    fit_fig.clf()
    plt.close(fit_fig)

    zero_guesses = [1000 * (rand(5) - 0.5) for i in range(50)]
    zero_results = [opt.least_squares(f_lsq, g, args=(wav_naught, int_naught))
                    for g in zero_guesses]
    zero_r_params = [r.x for r in zero_results]
    zero_r_cost = [r.cost for r in zero_results]
    del zero_results
    zero_best_index = np.argmin(zero_r_cost)
    zero_best_params = zero_r_params[zero_best_index]
    #zero_peak = max(T_fano(wav_naught, *zero_best_params))

    #peak_shift = float(bg_peak[0]) - float(zero_peak[0])

    return file_name, bg_peak[0], peak_shift


def peak_shift(file, zero_file):
    '''
    Reads in the wavelength, intensity and file name parameters from
    an in-file and the sensor file. Then uses the FindPeaks function to
    determine the x coordinates of a resonant peak within both files. Using
    this it calculates a peak shift. Outputs the time, peak and peak shift
    values.
    Args:
        file: <string> file path to image
        zero_file: <string> file path to sensor background image
    '''
    wavelength, intensity, file_name = io.array_in(file=file)
    wav_zero, int_zero, zero_file_name = io.array_in(file=zero_file)

    file_peak = peaks(x=wavelength,
                      y=intensity,
                      distance=300,
                      width=20,
                      xmin=730,
                      xmax=810)

    zero_peak = peaks(x=wav_zero,
                      y=int_zero,
                      distance=300,
                      width=20,
                      xmin=740,
                      xmax=800)

    time_stamp = (file_name.split('_')[::-1])[0]

    if len(file_peak) == 0:
        peak = None
        peak_shift = None
    else:
        peak = float(file_peak[0])
        peak_shift = float(file_peak[0]) -float(zero_peak[0])

    return time_stamp, peak, peak_shift
