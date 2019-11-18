import os
import sys
import csv
import shutil


def check_dir_exists(dir_path):
    '''
    Check to see if a directory path exists, and if not create one
    Args:
        dir_path: <string> directory path
    '''
    if os.path.isdir(dir_path) is False:
        os.mkdir(dir_path)


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


def directory_finder(dir_path):
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


def delimiter_changer(main_dir,
                      osa,
                      delim):
    '''
    This function changes the standard delimiter in thorlabs osa to a comma.
    We do this to fix an issue with the entire software as it was originally
    written to handle comma delimited files. If anything other than a comma is
    used then it can be adjusted in the main code.
    Args:
        main_dir: <string> directory path to the main directory containing
                  spectrum directories
        osa: <bool> if True, thorlabs osa was used to capture the spectrums
        delim: <string> the original file delimiter, thorbals osa use ; defult
    '''
    for index, selected_dir in enumerate(os.listdir(main_dir)):
        if 'Results' in selected_dir:
            pass
        if 'TimeCorrected' in selected_dir:
            pass
        if 'TimeAdjusted' in selected_dir:
            pass
        else:
            original_dir = os.path.join(main_dir, selected_dir)
            new_dir = os.path.join(os.getcwd(), selected_dir)

            data_files = extract_files(dir_path=original_dir,
                                       file_string='.csv')
            test_file = os.path.join(original_dir, data_files[0])

            try:
                wav, int, _ = io.del_csv_in(file_path=test_file,
                                            delimiter=delim,
                                            osa=osa)
                if len(wav) == 0:
                    for selected_file in data_files:
                        check_dir_exists(new_dir)
                        file = os.path.join(original_dir, selected_file)
                        file_name = get_filename(file_path=file)
                        new_file = os.path.join(new_dir, f'{file_name}.csv')

                        with open(file, newline='') as infile:
                            reader = csv.reader(infile, delimiter=';')
                            with open(new_file,mode='w',newline='') as outfile:
                                writer = csv.writer(outfile, delimiter=',')
                                for row in reader:
                                    writer.writerow(row)
                    shutil.rmtree(original_dir)
                    shutil.move(new_dir, main_dir)

                    update_progress(index / len(os.listdir(main_dir)))

                else:
                    pass
            except:
                pass
