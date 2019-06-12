import os
import sys
import numpy as np
from shutil import copy


def config_dir_path():
    '''
    Asigns a directory path for all data, allowing for user input without
    altering the script.
    The current working directory (which is where the code is activatd from)
    will then contain all data to be analysed. A folder (directory) is created
    named 'Put_Data_Here'.
    The function then waits for the user to place a data folder (from GMR setup)
    in to the new folder, eg...('050319') which contains '1M_Salt',...etc.
    Args:
        The function requires no arguments but will not work unless data is
        placed into the new directory and awaits a user input (pressing enter)
    '''
    root = os.getcwd()
    main_dir = os.path.join(root, 'Put_Data_Here')
    if os.path.isdir(main_dir) is False:
        os.mkdir(main_dir)
    while len(os.listdir(main_dir)) == 0:
        print('Place test data into "Put_Data_Here" folder with this code.')
        print('This is the same folder created on GMR X.')
        print('Once complete please hit enter on your keyboard.')
        print(' ')
        input('Press enter to continue...')
    else:
        print('Data present in "Put_Data_Here", ensure it is correct')
        print('Ensure in the code that the "sensor" parameter is correct')
        print(' ')
        input('Press enter to continue...')
    print(' ')
    print('Data set(s) to be examined:')
    print(os.listdir(main_dir))
    return main_dir


def file_sort(dir_name):
    '''
    Numerically sort a directory containing a combination of string file names
    and numerical file names
    Args:
        dir_name, string with directory path
    '''
    return sorted(os.listdir(dir_name))


def extract_files(dir_name, file_string):
    '''
    Stack file names in a directory into an array. Returns data files array.
    Args:
        dir_name, string with directory path
        file_string, string within dired file names
    '''
    dir_list = file_sort(dir_name)
    return [a for a in dir_list if file_string in a]


def check_dir_exists(dir_name):
    '''
    Check to see if a directory path exists, and if not create one
    Args:
        dir_name, string directory path
    '''
    if os.path.isdir(dir_name) is False:
        os.mkdir(dir_name)


def array_save(array_name, file_name, dir_name):
    '''
    Save array as file name in a given directory
    Args:
        array_name: <array> python array to save
        file_name: <string> file name to save out
        dir_name: <string> directory name to copy saved array to
    '''
    check_dir_exists(dir_name)

    file_name = f'{file_name}.npy'
    file_path = os.path.join(dir_name, file_name)

    np.save(file_path, array_name)


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




if __name__ == '__main__':

    main_dir = config_dir_path()
    data_dir = os.listdir(main_dir)

    for dir in data_dir:
        img_dir = os.path.join(main_dir, dir)
        print(img_dir)
        print(os.listdir(img_dir))
