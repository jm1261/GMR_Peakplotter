import os
import numpy as np
import OLD_GMR.org_functions as of
import OLD_GMR.background_calibration as bc


def solute_finder(dir_name):
    '''
    Splits a directory name into separate components (eg.. '1M_Salt_Heat' to
    '1M','Salt','Heat'), returns an array containing the individual components.
    Args:
        dir_name: <string> path to directory
    '''
    dir_name_string = os.path.split(dir_name)[-1]
    dir_params = dir_name_string.split('_')
    return dir_params


def convert_to_seconds(hours, minutes, seconds, milliseconds):
    '''
    Converts values given in hours, minutes, seconds and milliseconds into a
    total time given in seconds. Function converts all values to int, so a
    string can be passed in in args.
    Args:
        hours: <string> value given as number of hours
        minutes: <string> value given as number of minutes
        seconds: <string> value given as number of seconds
        milliseconds: <string> value given as number of milliseconds
    '''
    ms_to_seconds = float(milliseconds) / 1000
    minutes_to_seconds = int(minutes) * 60
    hrs_to_seconds = int(hours) * 60 * 60

    total_seconds = (int(hrs_to_seconds)
                     + int(minutes_to_seconds)
                     + int(seconds)
                     + float(ms_to_seconds))
    return float(total_seconds)


def time_sort(in_dir_name, dir_params, main_dir):
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
    file_string = '_'.join(dir_params)
    print(f'\n{dir_params}')
    data_files = of.extract_files(dir_name=in_dir_name,
                                  file_string=file_string)

    for index, selected_file in enumerate(data_files):
        file = os.path.join(in_dir_name, selected_file)
        wavelength, intensity, file_name = bc.read_in_values(file)

        data = np.vstack((wavelength, intensity)).T

        split_file = file_name.split('_')[::-1]
        hrs_split = split_file[0].split('h')
        mins_split = hrs_split[1].split('m')
        secs_split = mins_split[1].split('s')

        total_seconds = convert_to_seconds(hours=hrs_split[0],
                                           minutes=mins_split[0],
                                           seconds=secs_split[0],
                                           milliseconds=secs_split[1])

        out_dir_name = '_'.join(dir_params) + '_TimeAdjusted'
        out_dir = os.path.join(main_dir, out_dir_name)
        of.check_dir_exists(out_dir)

        joined = []
        joined.append(file_string)
        joined.append(str(total_seconds))
        new_file_name = '_'.join(joined)

        of.array_save(array_name=data,
                      file_name=new_file_name,
                      dir_name=out_dir)

        of.update_progress(index / len(data_files))


def time_correct(in_dir_name, dir_params, main_dir):
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
    file_string = '_'.join(dir_params[0:2])
    print(' ')
    print(dir_params)
    data_files = of.extract_files(dir_name=in_dir_name,
                                  file_string=file_string)

    zero_file_name = data_files[0]
    zero_time_stamp = (zero_file_name.split('_')[::-1])[0]

    for index, selected_file in enumerate(data_files):
        file = os.path.join(in_dir_name, selected_file)
        data = np.load(file)

        file_name = bc.get_filename(file)
        split_file = file_name.split('_')[::-1]
        time_correction = int(float(split_file[0])
                          - float(zero_time_stamp[0:-4]))

        out_dir_name = '_'.join(dir_params[0:-1]) + '_TimeCorrected'
        out_dir = os.path.join(main_dir, out_dir_name)
        of.check_dir_exists(out_dir)

        joined = []
        joined.append(file_string)
        joined.append(str(time_correction))
        new_file_name = '_'.join(joined)

        of.array_save(array_name=data,
                      file_name=new_file_name,
                      dir_name=out_dir)

        os.remove(file)

        of.update_progress(index / len(data_files))
