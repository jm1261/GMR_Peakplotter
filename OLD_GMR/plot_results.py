import os
import matplotlib.pyplot as plt
import numpy as np
from shutil import copy
import OLD_GMR.org_functions as of
import OLD_GMR.background_calibration as bc
import OLD_GMR.time_correct as tc
import OLD_GMR.peak_finder as pf
import OLD_GMR.plot_results as pr


def plot_peaks(file,
               bg_dir,
               file_params,
               sensor,
               main_dir,
               show=False,
               save=False):
    '''
    Loads in the results file previously saved as time, peak, peak shift and
    the background calibration file with the file name, peak and peak shift.
    Using an array (bg_file_string) to find the relevant reference files
    within the background calibration file, it plots the peak change as a
    function of time, and adds the peak or peak shift wavelengths of the
    references as horizontal lines with the file name as text.
    Args:
        file: <string> file path to results csv
        bg_dir: <string> directory path to background calibration directory
        dir_params: <array> SoluteFinder function to determine solute and
                    concentration
        sensor: <string> set within the code to the biosensor used
        show: <bool> show plot
        save: <bool> saves plot to results directory
    '''
    file_string = '_'.join(file_params[0:2])
    out_dir = os.path.join(main_dir, 'Results')
    of.check_dir_exists(out_dir)

    bg_file_string = ['1M_Salt_Background',
                      file_string + '_Background',
                      '1M_Salt_Paper_Background',
                      file_string + '_Paper_Background',
                      sensor + '_Background']

    bg_file = os.path.join(bg_dir, 'Background_Peaks.csv')
    name_string, bg_peak, bg_peak_shift = np.genfromtxt(bg_file,
                                                        delimiter=',',
                                                        usecols=(0, 1, 2),
                                                        dtype=(str),
                                                        unpack=True)

    time, peak, peak_shift = np.genfromtxt(file,
                                           delimiter=',',
                                           unpack=True)
    time *= 1/60
    file_name = bc.get_filename(file)

    fig, ax = plt.subplots(1, 1, figsize=[10,7])

    ax.plot(time, peak, 'b.', label=' '.join(file_name.split('_')[0:2]))
    ax.grid(True)
    ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})

    for index, name in enumerate(name_string):
        if name in bg_file_string:
            ax.axhline(y=float(bg_peak[index]),
                       linewidth=2,
                       color='C' + str(index % 9),
                       linestyle=':')

            ax.text(x=2 * index,
                    y=(float(bg_peak[index])),
                    s=' '.join(name.split('_')[0:-1]),
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.5),
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=8)

    ax.set_xlabel('Time [min]', fontsize=14)
    ax.set_ylabel('Peak [nm]', fontsize=14)
    ax.set_title(' '.join(file_name.split('_')[0:2]), fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=14)

    fig.tight_layout()

    if show:
        plt.show()

    if save:
        plt.savefig(file_name + '.png')
        copy(file_name + '.png', out_dir)
        os.remove(file_name + '.png')

    fig.clf()
    plt.close(fig)


def plot_peak_shift(file,
                    bg_dir,
                    file_params,
                    sensor,
                    main_dir,
                    show=False,
                    save=False):
    '''
    Loads in the results file previously saved as time, peak, peak shift and
    the background calibration file with the file name, peak and peak shift.
    Using an array (bg_file_string) to find the relevant reference files
    within the background calibration file, it plots the peak shift as a
    function of time, and adds the peak or peak shift wavelengths of the
    references as horizontal lines with the file name as text.
    Args:
        file: <string> file path to results csv
        bg_dir: <string> directory path to background calibration directory
        dir_params: <array> SoluteFinder function to determine solute and
                    concentration
        sensor: <string> set within the code to the biosensor used
        show: <bool> show plot
        save: <bool> saves plot to results directory
    '''
    file_string = '_'.join(file_params[0:2])
    out_dir = os.path.join(main_dir, 'Results')
    of.check_dir_exists(out_dir)

    bg_file_string = ['1M_Salt_Background.csv',
                      file_string + '_Background.csv',
                      '1M_Salt_Paper_Background.csv',
                      file_string + '_Paper_Background.csv',
                      sensor + '_Background.csv']

    bg_file_string = ['1M_Salt_Background',
                      file_string + '_Background',
                      '1M_Salt_Paper_Background',
                      file_string + '_Paper_Background',
                      sensor + '_Background']

    bg_file = os.path.join(bg_dir, 'Background_Peaks.csv')
    name_string, bg_peak, bg_peak_shift = np.genfromtxt(bg_file,
                                                        delimiter=',',
                                                        usecols=(0, 1, 2),
                                                        dtype=(str),
                                                        unpack=True)

    time, peak, peak_shift = np.genfromtxt(file,
                                           delimiter=',',
                                           unpack=True)
    time *= 1/60
    file_name = bc.get_filename(file)

    fig, ax = plt.subplots(1, 1, figsize=[10,7])

    ax.plot(time, peak_shift, 'r.', label=' '.join(file_name.split('_')[0:2]))
    ax.grid(True)
    ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})

    for index, name in enumerate(name_string):
        if name in bg_file_string:
            ax.axhline(y=float(bg_peak_shift[index]),
                       linewidth=2,
                       color='C' + str(index % 9),
                       linestyle=':')

            ax.text(x=2 * index,
                    y=(float(bg_peak_shift[index])),
                    s=' '.join(name.split('_')[0:-1]),
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.5),
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=8)

    ax.set_xlabel('Time [min]', fontsize=14)
    ax.set_ylabel('Peak Shift [nm]', fontsize=14)
    ax.set_title(' '.join(file_name.split('_')[0:2]), fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=14)

    fig.tight_layout()

    if show:
        plt.show()

    if save:
        plt.savefig(file_name + '_Shift.png')
        copy(file_name + '_Shift.png', out_dir)
        os.remove(file_name + '_Shift.png')

    fig.clf()
    plt.close(fig)
