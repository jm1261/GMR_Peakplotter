import GMR.InputOutput as io
import numpy as np
import os


def solute_finder(dir_path):
    '''
    Splits a directory name into separate components (eg.. '1M_Salt_Heat' to
    '1M','Salt','Heat'), returns an array containing the individual components.
    Args:
        dir_name: <string> path to directory
    Returns:
        dir_params: <array> array containing the individual directory strings
                    after splitting at the pre-path and '_'
    '''
    dir_name_string = os.path.split(dir_path)[-1]
    dir_params = dir_name_string.split('_')
    return dir_params


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


def trim_spec(file_path,
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


def gradient(x, y, xy, x2):
    '''
    Calculate a gradient using numpy mean to calculate the mean of an x array,
    y array, an x * y array, and an x **2 array.
    Args:
        x: <array> x array
        y: <array> y array
        xy: <array> x*y array
        x2: <array> x**2 array
    Returns:
        m: <int/float> gradient value
    '''
    m = (((np.mean(x) * np.mean(y)) - np.mean(xy)) /
        ((np.mean(x) ** 2) - np.mean(x2)))
    return m


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
              pwr_spec,
              osa):
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
    '''
    file_string = '.csv'
    print(f'\n{dir_params}')
    data_files = io.extract_files(dir_path=in_dir,
                                  file_string=file_string)

    for index, selected_file in enumerate(data_files):
        file = os.path.join(in_dir, selected_file)
        wavelength, intensity, file_name = trim_spec(file_path=file,
                                                     pwr_spec=pwr_spec,
                                                     xi=x1,
                                                     xf=x2,
                                                     osa=osa)

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
        io.check_dir_exists(out_dir)

        joined = []
        joined.append(file_string)
        joined.append(str(total_seconds))
        new_file_name = '_'.join(joined)

        io.array_out(array_name=data,
                     file_name=new_file_name,
                     dir_path=out_dir)

        io.update_progress(index / len(data_files))


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
    #file_string = 'IgG'
    print(' ')
    print(dir_params)
    data_files = io.extract_files(dir_path=in_dir,
                                  file_string=file_string)

    zero_file_name = data_files[0]
    zero_time_stamp = (zero_file_name.split('_')[::-1])[0]

    for index, selected_file in enumerate(data_files):
        file = os.path.join(in_dir, selected_file)
        data = np.load(file)

        file_name = io.get_filename(file)
        split_file = file_name.split('_')[::-1]
        time_correction = int(float(split_file[0])
                          - float(zero_time_stamp[0:-4]))

        out_dir_name = '_'.join(dir_params[0:-1]) + '_TimeCorrected'
        out_dir = os.path.join(main_dir, out_dir_name)
        io.check_dir_exists(out_dir)

        joined = []
        joined.append('_'.join(dir_params[0:2]))
        joined.append(str(time_correction))
        new_file_name = '_'.join(joined)

        io.array_out(array_name=data,
                     file_name=new_file_name,
                     dir_path=out_dir)

        io.update_progress(index / len(data_files))
