import os
import numpy as np
import sys


def config_dir_path():
    '''
    Asigns directory path for all data, allowing user input without
    code file path alterations.
    The current working directory (cwd) will then contain all data to
    be analysed. A directory is created name "Put_Data_Here".
    The function waits for user to place data in the folder e.g.
    "hs_img_000", "power_spectrum.csv", "experimental_settings.txt"
    from GMR X.
    Once data is present, the function returns the "Put_Data_Here"
    directory as the main directory and then directory paths can be
    asigned.
    Args:
        The function requires no arguments but will not work unless data
        is present in the new (created) directory and awaits user input.
    Returns:
        a current working directory
    '''
    root = os.getcwd()
    main_dir = os.path.join(root, 'Put_Data_Here')
    check_dir_exists(main_dir)

    while len(os.listdir(main_dir)) == 0:
        print('Place data into "Put_Data_Here" folder with this code')
        print('Once complete, restart code')
        os.sys.exit(0)

    else:
        print('Data present in "Put_Data_Here", ensure it is correct\n')
        input('Press enter to continue...\n')

    print('Data set(s) to be examined:')
    print(os.listdir(main_dir))
    print('\n')
    return main_dir


def file_sort(dir_path):
    '''
    Numerically sort a directory containing a combination of string file names
    and numerical file names
    Args:
        dir_path: <string> directory path
    Returns:
        sorted_array: <array> contents of dir_path sorted numerically
    '''
    return sorted(os.listdir(dir_path))


def extract_files(dir_path, file_string):
    '''
    Stack file names in a directory into an array. Returns data files array.
    Args:
        dir_path: <string> directory path
        file_string: <string> within desired file names
    Returns:
        array: <array> containing sorted and selected file name strings
    '''
    dir_list = file_sort(dir_path)
    return [a for a in dir_list if file_string in a]


def check_dir_exists(dir_path):
    '''
    Check to see if a directory path exists, and if not create one
    Args:
        dir_path: <string> directory path
    '''
    if os.path.isdir(dir_path) is False:
        os.mkdir(dir_path)


def get_filename(file_path):
    '''
    Takes a file name path and splits on '/' to obtain only the file name.
    Splits the file name from extension and returns just the user asigned
    file name as a string.
    Args:
        file_name: <string> path to file
    Returns:
        file_name: <string> file name string without path or extension
    '''
    return os.path.splitext(os.path.basename(file_path))[0]


def csv_in(file_path,
           osa=False):
    '''
    Reads in a 2 column csv file (wavelength (nm), intensity) and unpacks
    the file into two arrays, wavelength and intensity.
    Args:
        file_path: <string> file path
        osa: <bool> if true selects the csv_in parameters for loading
                      a spectrum taken with Thorlabs OSA
    Returns:
        wavelength: <array> measured wavelength values
        intensity: <array> measured intensity values
        file_name: <string> file name string without path or extension
    '''
    file_name = get_filename(file_path)

    if osa:
        wavelength, intensity = np.genfromtxt(file_path,
                                              delimiter=',',
                                              unpack=True,
                                              skip_header=33,
                                              skip_footer=1)
    else:
        wavelength, intensity = np.genfromtxt(file_path,
                                              delimiter=',',
                                              unpack=True)


    return wavelength, intensity, file_name


def update_progress(progress):
    '''
    Function to display to terminal or update a progress bar according to
    value passed.
    Args:
        progress: <float> between 0 and 1. Any int will be converted
                  to a float. Values less than 0 represent a 'Halt'.
                  Values greater than or equal to 1 represent 100%
    '''
    barLength = 50  # Modify this to change the length of the progress bar
    status = " "

    if isinstance(progress, int):
        progress = float(progress)

    if not isinstance(progress, float):
        progress = 0
        status = 'Error: progress input must be float\r\n'

    if progress < 0:
        progress = 0
        status = 'Halt...\r\n'

    if progress >= 1:
        progress = 1
        status = 'Done...\r\n'

    block = int(round(barLength * progress))
    progress_str = '#' * block + '-' * (barLength - block)
    text = '\rPercent: [{0}] {1:.0f}% {2}'.format(progress_str,
                                                  progress * 100,
                                                  status)
    sys.stdout.write(text)
    sys.stdout.flush()


def check_dir_exists(dir_path):
    '''
    Check to see if a directory path exists, and if not create one
    Args:
        dir_path: <string> directory path
    '''
    if os.path.isdir(dir_path) is False:
        os.mkdir(dir_path)


def array_out(array_name,
              file_name,
              dir_path):
    '''
    Save array as file name in a given directory
    Args:
        array_name: <array> python array to save
        file_name: <string> file name to save out
        dir_name: <string> directory name to copy saved array to
    '''
    check_dir_exists(dir_path)

    file_name = f'{file_name}.npy'
    file_path = os.path.join(dir_path, file_name)

    np.save(file_path, array_name)


def array_in(file_path):
    '''
    Load in a numpy array file, returns the wavelength, intensity and file
    name.
    Args:
        file: <string> file path
    Returns:
        wavelength: <array> wavelength values
        intensity: <array> measured intensity values
        file_name: <string> file name without path or extensions
    '''
    data = np.load(file_path)
    file_name = get_filename(file_path)

    wavelength = data[:,0]
    intensity = data[:,1]

    return wavelength, intensity, file_name
