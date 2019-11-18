import os
import numpy as np
import GMR.InputOutput as io
from numpy.random import rand
import scipy.optimize as opt
import GMR.Organise as org
import shutil
import csv


def normalise_csv(file_path,
                  pwr_spec,
                  osa):
    '''
    Normalises a csv spectrum to a given light source power spectrum. Uses
    csv_in function to load a csv spectrum as normal, then divides the
    measured intensity by the light source intensity.
    Args:
        file_path: <string> path to file
        pwr_spec: <string> path to light source spectrum
        osa: <bool> if true selects the csv_in parameters for loading
                      a spectrum taken with Thorlabs OSA
    Returns:
        wavelength: <1D array> containing the measured wavelength values
        norm_int: <1D array> containing corrected intensity values
        file_name: <string> file name without path or extension
    '''
    wavelength, intensity, file_name = io.csv_in(file_path=file_path,
                                                 osa=osa)
    pwr_wav, pwr_int, pwr_file_name = io.csv_in(file_path=pwr_spec,
                                                osa=osa)
    norm_int = intensity / pwr_int
    return wavelength, norm_int, file_name


def trim_spec_norm(file_path,
                   pwr_spec,
                   xi,
                   xf,
                   osa):
    '''
    Interpolates a normalised spectrum over a given x range. Loads in a csv
    using csv_in function, normalises to a light source power spectrum using
    normalise_csv. Then creates a wavelength range using np.arange with the
    given ROI start and end points, and then uses scipy interpolate 2d to
    smooth out the normalised intensity values.
    Args:
        file_path: <string> path to file
        pwr_spec: <string> path to light source spectrum
        xi: <float/int> initial wavelength value from ROI
        xf: <float/int> final wavelength value from ROI
        osa: <bool> if true selects the csv_in parameters for loading
                      a spectrum taken with Thorlabs OSA
    Returns
        wavelength: <array> created wavelength range within ROI
        intensity: <array> corresponding interpolate intensity values
        file_name: <string> file name without path or extension
    '''
    wavs, norm_int, file_name = normalise_csv(file_path=file_path,
                                              pwr_spec=pwr_spec,
                                              osa=osa)
    wavelength = np.arange(xi, xf + 1, 1)
    intensity = np.interp(x=wavelength,
                          fp=norm_int,
                          xp=wavs)
    return wavelength, intensity, file_name


def trim_spec(file_path,
              xi,
              xf,
              osa):
    '''
    Interpolates a normalised spectrum over a given x range. Loads in a csv
    using csv_in function, normalises to a light source power spectrum using
    normalise_csv. Then creates a wavelength range using np.arange with the
    given ROI start and end points, and then uses scipy interpolate 2d to
    smooth out the normalised intensity values.
    Args:
        file_path: <string> path to file
        pwr_spec: <string> path to light source spectrum
        xi: <float/int> initial wavelength value from ROI
        xf: <float/int> final wavelength value from ROI
        osa: <bool> if true selects the csv_in parameters for loading
                      a spectrum taken with Thorlabs OSA
    Returns
        wavelength: <array> created wavelength range within ROI
        intensity: <array> corresponding interpolate intensity values
        file_name: <string> file name without path or extension
    '''
    wavs, norm_int, file_name = io.csv_in(file_path=file_path,
                                          osa=osa)
    wavelength = np.arange(xi, xf + 1, 1)
    intensity = np.interp(x=wavelength,
                          fp=norm_int,
                          xp=wavs)
    return wavelength, intensity, file_name


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


def convert_to_seconds(date,
                       hours,
                       minutes,
                       seconds,
                       milliseconds):
    '''
    Converts values given in hours, minutes, seconds and milliseconds into a
    total time given in seconds. Function converts all values to int, so a
    string can be passed in in args.
    Args:
        hours: <string> value given as number of hours
        minutes: <string> value given as number of minutes
        seconds: <string> value given as number of seconds
        milliseconds: <string> value given as number of milliseconds
    Returns:
        total_seconds: <float> time stamp converted to seconds
    '''
    ms_to_seconds = float(milliseconds) / 1000
    minutes_to_seconds = int(minutes) * 60
    hrs_to_seconds = int(hours) * 60 * 60
    date_to_seconds = int(date) * 24 * 60 * 60

    total_seconds = (int(date_to_seconds)
                     + int(hrs_to_seconds)
                     + int(minutes_to_seconds)
                     + int(seconds)
                     + float(ms_to_seconds))
    return float(total_seconds)


def time_sort(in_dir,
              dir_params,
              main_dir,
              x1,
              x2,
              osa,
              pwr_spec):
    '''
    Spectrums/Images captured using splicco's automatic data capture/timed
    sequential function are automatically given a user defined file name and
    a time and date stamp of the moment a measurement was taken (file created).
    This function converts the time stamp given into a value in seconds by
    splitting the file name into sections, reversing the order and splitting
    the time stamp at 'h' 'm' and 's' then converting to seconds.
    The function then adds all the values together to give a total time in
    seconds, concatenates this with the original file name, and saves the
    original data out with a new file name as a numpy array.
    Args:
        in_dir_name: <string> directory name containing spectrum files
        dir_params: <array> directories are given a name equivalent to the
                    individual file names, the dir_params function splits
                    the directory name into an array that can be used to find
                    the correct spectrum files.
        main_dir: <string> current working directory
        x1, x2: <float/int> start and end points for trim spectrum
        osa: <bool> if true, input files were captured with thorlabs osa
    '''
    file_string = '.csv'
    print(f'\n{dir_params}')
    data_files = org.extract_files(dir_path=in_dir,
                                   file_string=file_string)

    for index, selected_file in enumerate(data_files):
        file = os.path.join(in_dir, selected_file)
        wavelength, intensity, file_name = trim_spec_norm(file_path=file,
                                                          xi=x1,
                                                          xf=x2,
                                                          osa=osa,
                                                          pwr_spec=pwr_spec)

        data = np.vstack((wavelength, intensity)).T

        if osa:
            split_file = file_name.split('_')[::-1]

            total_seconds = convert_to_seconds(date=split_file[4],
                                               hours=split_file[3],
                                               minutes=split_file[2],
                                               seconds=split_file[1],
                                               milliseconds=split_file[0])
        else:
            split_file = file_name.split('_')[::-1]
            date_split = split_file[1]
            hrs_split = split_file[0].split('h')
            mins_split = hrs_split[1].split('m')
            secs_split = mins_split[1].split('s')

            total_seconds = convert_to_seconds(date=date_split,
                                               hours=hrs_split[0],
                                               minutes=mins_split[0],
                                               seconds=secs_split[0],
                                               milliseconds=secs_split[1])

        out_dir_name = '_'.join(dir_params) + '_TimeAdjusted'
        out_dir = os.path.join(main_dir, out_dir_name)
        org.check_dir_exists(dir_path=out_dir)

        joined = []
        joined.append(file_name.split('_')[0])
        joined.append(str(total_seconds))
        new_file_name = '_'.join(joined)

        io.array_out(array_name=data,
                     file_name=new_file_name,
                     dir_path=out_dir)

        org.update_progress(index / len(data_files))


def time_correct(in_dir,
                 dir_params,
                 main_dir):
    '''
    Spectrums/Images time adjusted in TimeSort function above are loaded in
    and the data is maintained. The file name is split and the first file
    captured is set to 0, the following files within the directory are given
    a time stamp respective to the zero file (a time step). This is useful
    for later processing.
    Args:
        in_dir_name: <string> directory name containind time adjusted
                     spectrum files
        dir_params: <array> directories are given a name equivalent to the
                    individual file names, the dir_params function splits
                    the directory name into an array that can be used to find
                    the correct spectrum files.
        main_dir: <string> current working directory
    '''
    file_string = '.npy'
    print(f'\n{dir_params}')

    data_files = org.extract_files(dir_path=in_dir,
                                   file_string=file_string)

    zero_file_name = data_files[0]
    zero_time_stamp = (zero_file_name.split('_')[::-1])[0]

    for index, selected_file in enumerate(data_files):
        file = os.path.join(in_dir, selected_file)
        data = np.load(file)

        file_name = org.get_filename(file)
        split_file = file_name.split('_')[::-1]
        time_correction = int(float(split_file[0])
                          - float(zero_time_stamp[0:-4]))

        out_dir_name = '_'.join(dir_params[0:-1]) + '_TimeCorrected'
        out_dir = os.path.join(main_dir, out_dir_name)
        org.check_dir_exists(out_dir)

        joined = []
        joined.append('_'.join(dir_params[0:2]))
        joined.append(str(time_correction))
        new_file_name = '_'.join(joined)

        io.array_out(array_name=data,
                     file_name=new_file_name,
                     dir_path=out_dir)

        org.update_progress(index / len(data_files))


def time_correct_files(main_dir,
                       solute_dir,
                       x1,
                       x2,
                       osa,
                       pwr_spec):
    '''
    Combines both time sort and time correct functions.
    Args:
        main_dir: <string> directory path to root or main directory
        solute_dir: <string> directory path to directory containing spectrums
        x1, x2: <float/int> start and end point of region of interest
        osa: <bool> if true, spectrums were captured using thorlabs osa
    '''
    print(f'\nLooking at: {solute_dir}'
           '\nTime stamp correcting')

    dir_params = org.directory_finder(dir_path=solute_dir)
    in_dir = os.path.join(main_dir, solute_dir)
    time_sort(in_dir=in_dir,
              dir_params=dir_params,
              main_dir=main_dir,
              x1=x1,
              x2=x2,
              osa=osa,
              pwr_spec=pwr_spec)
    dir_params = org.directory_finder(f'{solute_dir}_TimeAdjusted')
    in_dir = os.path.join(main_dir, f'{solute_dir}_TimeAdjusted')
    time_correct(in_dir=in_dir,
                 dir_params=dir_params,
                 main_dir=main_dir)
    shutil.rmtree(in_dir)


def find_peaks(main_dir,
               solute_dir):
    '''
    Uses a fano function to find the peak intensity and return the Wavelength
    value corresponding to it. Essentially finds peak y and returns the x.
    The function first looks for the time corrected directory containing the
    trimmed spectrums with time stamp. It then creates a results directory.
    It uses the first file in the time corrected directory to find the best
    fit guesses. Then it uses the find_fano function to find the remaining
    peaks.
    The peaks, and peak shifts (from the first file), are then written into a
    csv file (3 columns) which is moved to the results directory.
    Args:
        main_dir: <string> directory path to root
        solute_dir: <string> directory path to spectrums directory
    '''
    print('\nFinding Peaks')
    time_corrected_dir = os.path.join(main_dir, f'{solute_dir}_TimeCorrected')
    results_dir = os.path.join(main_dir, 'Results')
    org.check_dir_exists(results_dir)

    dir_params = org.directory_finder(dir_path=time_corrected_dir)
    data_files = org.extract_files(dir_path=time_corrected_dir,
                                   file_string='.npy')
    zero_file = os.path.join(time_corrected_dir, data_files[0])

    zero_wl, zero_int, zero_name = io.array_in(file_path=zero_file)
    best_guesses = best_params(x=zero_wl,
                               y=zero_int)
    _, peak_zero = find_fano(x=zero_wl,
                             y=zero_int,
                             best_params=best_guesses)

    outfile_name = (str('_'.join(dir_params)) + '_Peaks.csv')
    with open(outfile_name, 'a', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        writer.writerow(['Time [s]'] +
                        ['Peak [nm]'] +
                        ['Peak Shift [nm]'])

        for index, selected_file in enumerate(data_files):
            file = os.path.join(time_corrected_dir, selected_file)
            wl, int, file_name = io.array_in(file_path=file)
            time_stamp = file_name.split('_')[::-1][0]
            _, peak = find_fano(x=wl,
                                y=int,
                                best_params=best_guesses)
            peak_shift = float(peak) - float(peak_zero)

            writer.writerow([time_stamp] + [peak] + [peak_shift])
            org.update_progress(index / len(data_files))

    shutil.copy(outfile_name, results_dir)
    os.remove(outfile_name)
