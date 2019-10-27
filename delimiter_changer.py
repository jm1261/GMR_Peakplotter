import os
import csv


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


original_dir = os.path.join(os.getcwd(),
                            'Put_Data_Here',
                            'Solute_Concentrations_mk4',
                            '1mM_KCl_40degrees')
new_dir = os.path.join(os.getcwd(),
                       '1mM_KCl_40degrees')
check_dir_exists(new_dir)

datafiles = extract_files(original_dir, '.csv')

for selected_file in datafiles:
    file = os.path.join(original_dir, selected_file)
    file_name = get_filename(file)
    new_file = os.path.join(new_dir, f'{file_name}.csv')

    with open(file, newline='') as infile:
        reader = csv.reader(infile, delimiter=';')
        with open(new_file, mode='w', newline='') as outfile:
            writer = csv.writer(outfile, delimiter=',')
            for row in reader:
                writer.writerow(row)
