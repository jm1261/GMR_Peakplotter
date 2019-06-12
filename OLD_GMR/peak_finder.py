import os
import numpy as np
import matplotlib.pyplot as plt
from shutil import copy
import csv
import OLD_GMR.org_functions as of
import OLD_GMR.background_calibration as bc
import OLD_GMR.time_correct as tc
import OLD_GMR.peak_finder as pf
import OLD_GMR.plot_results as pr


def read_in_params(file):
    '''
    Load in a numpy array file, returns the wavelength, intensity and file
    name.
    Args:
        file: <string> file path
    '''
    data = np.load(file)
    file_name = bc.get_filename(file)

    wavelength = data[:,0]
    intensity = data[:,1]

    return wavelength, intensity, file_name


def plot_spectrum(file, dir_params, main_dir, show=False, save=True):
    '''
    Uses the ReadInParams function to get wavelength, intensity and
    file name parameters from a given file. Uses SoluteFinder to determine
    which solute and what concentration is being analysed and plots the
    spectrum. Can show or save out the figure into a given directory.
    Args:
        file: <string> file path
        dir_params: <array> Output of the SoluteFinder function to determine
                    solute and concentration parameters.
        show: <bool> shows the plot if True
        save: <bool> saves the plot if True
    '''
    wavelength, intensity, file_name = read_in_params(file=file)

    fig, ax = plt.subplots(1, 1, figsize=[10,7])

    ax.plot(wavelength, intensity, 'b', lw=2, label=file_name)
    ax.grid(True)
    ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})

    ax.set_xlabel('Wavelength [nm]', fontsize=14)
    ax.set_ylabel('Intensity [au]', fontsize=14)
    ax.set_title(file_name, fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=14)

    fig.tight_layout()

    if show:
        plt.show()

    if save:
        out_dir_name = '_'.join(dir_params[0:-1]) + '_Graphs'
        out_dir = os.path.join(main_dir, out_dir_name)
        of.check_dir_exists(out_dir)
        out_path = os.path.join(out_dir, file_name + '.png')

        plt.savefig(out_path)

    fig.clf()
    plt.close(fig)


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
    wavelength, intensity, file_name = read_in_params(file=file)
    wav_zero, int_zero, zero_file_name = bc.read_in_values(file=zero_file)

    file_peak = bc.peaks(x=wavelength,
                         y=intensity,
                         distance=300,
                         width=20,
                         xmin=730,
                         xmax=810)

    zero_peak = bc.peaks(x=wav_zero,
                         y=int_zero,
                         distance=300,
                         width=20,
                         xmin=740,
                         xmax=800)

    time_stamp = (file_name.split('_')[::-1])[0]

    peak = float(file_peak[0])
    peak_shift = float(file_peak[0]) -float(zero_peak[0])

    os.remove(file)

    return time_stamp, peak, peak_shift
