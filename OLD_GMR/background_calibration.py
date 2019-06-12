import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from shutil import copy
import csv


def get_filename(file_path):
    '''
    Takes a file name path and splits on '/' to obtain only the file name.
    Splits the file name from extension and returns just the user asigned
    file name as a string.
    Args:
        file_name: <string> path to file
    '''

    return os.path.splitext(os.path.basename(file_path))[0]


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


def read_in_values(file):
    '''
    Reads in a 2 column csv file (wavelength (nm), intensity) and unpacks
    the file into two arrays, wavelength and intensity.
    Args:
        file: <string> file path
    '''
    global wavelength, intensity
    wavelength, intensity = np.genfromtxt(file,
                                          delimiter=',',
                                          unpack=True)
    file_name = get_filename(file)
    return wavelength, intensity, file_name


def bg_plot(file, zero_file, out_dir, show=False, save=False):
    '''
    Utilises ReadInValues function to read in two sets of data. First it
    reads in the sensor file (zero_file) and then the shift file you want to
    plot. The function then uses matplotlib.pyplot libraries to plot the
    background file against the zero file to observe a peak shift. The
    function can then show or save the file.
    Args:
        file: <string> file path to background images
        zero_file: <string> file path to sensor background image
        show: <bool> determines if plot is shown
        save: <bool> determines if plot is saved out to background_dir
        bg_dir: <string> directory path to background 'calibrations'
    '''
    wav_naught, int_naught, zero_file_name = read_in_values(zero_file)
    wavelength, intensity, file_name = read_in_values(file)

    fig, ax = plt.subplots(1, 1, figsize=[10,7])

    ax.plot(wavelength, intensity, 'red', lw=2, label=file_name)
    ax.plot(wav_naught, int_naught, 'blue', lw=2, label=zero_file_name)

    ax.grid(True)
    ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})

    ax.set_xlabel('Wavelength [nm]', fontsize=14)
    ax.set_ylabel('Intensity', fontsize=14)
    ax.set_title(file_name, fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=14)

    fig.tight_layout()

    if save:
        graph_out_path = os.path.join(out_dir,
                                      file_name + '.png')
        plt.savefig(graph_out_path)

    if show:
        plt.show()

    fig.clf()
    plt.close(fig)


def bg_peaks(file, zero_file):
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
    wav_naught, int_naught, zero_file_name = read_in_values(zero_file)
    wavelength, intensity, file_name = read_in_values(file)

    zero_peak = peaks(x=wav_naught,
                      y=int_naught,
                      distance=300,
                      width=20,
                      xmin=740,
                      xmax=800)

    bg_peak = peaks(x=wavelength,
                    y=intensity,
                    distance=300,
                    width=20,
                    xmin=740,
                    xmax=800)

    peak_shift = float(bg_peak[0]) - float(zero_peak[0])

    return file_name, bg_peak[0], peak_shift
