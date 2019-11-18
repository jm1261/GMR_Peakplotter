import os
import numpy as np
import GMR.Organise as org
import GMR.UserInput as ui


def csv_in(file_path,
           osa):
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
    file_name = org.get_filename(file_path)

    if osa:
        try:
            wavelength, intensity = np.genfromtxt(file_path,
                                                  delimiter=',',
                                                  unpack=True,
                                                  skip_header=33,
                                                  skip_footer=1)
        except:
            wavelength, intensity = np.genfromtxt(file_path,
                                                  delimiter=';',
                                                  unpack=True,
                                                  skip_header=33,
                                                  skip_footer=1)
    else:
        try:
            wavelength, intensity = np.genfromtxt(file_path,
                                                  delimiter=',',
                                                  unpack=True)
        except:
            wavelength, intensity = np.genfromtxt(file_path,
                                                  delimiter=';',
                                                  unpack=True)

    return wavelength, intensity, file_name


def del_csv_in(file_path,
               delimiter,
               osa):
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
    file_name = org.get_filename(file_path)

    if osa:
        wavelength, intensity = np.genfromtxt(file_path,
                                              delimiter=delimiter,
                                              unpack=True,
                                              skip_header=33,
                                              skip_footer=1)
    else:
        wavelength, intensity = np.genfromtxt(file_path,
                                              delimiter=delimiter,
                                              unpack=True)

    return wavelength, intensity, file_name


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
    org.check_dir_exists(dir_path)

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
    file_name = org.get_filename(file_path)

    wavelength = data[:,0]
    intensity = data[:,1]

    return wavelength, intensity, file_name


def region_of_interest(root,
                       osa):
    '''
    Region of interest utlises the ROI function in UserInput.py to determine
    the desired region of interest per directory and assign the x-coordinates
    to the directory name. It uses the interactive matplotlib rectangle
    selector to allow the user to select the region of a spectrum they care
    about and what analysing. Other data is later removed from analysis.
    Args:
        root: <string> directory path to root (Put_Data_Here)
        osa: <bool> global variable to determine if thorlabs osa was used
    Returns:
        trim_spec: <dictionary> contains directory names and their region of
                   interest x-coordinates
    This function can be changed to include the y coordinates should they be
    of interest.
    '''
    trim_spec = {}
    for selected_dir in os.listdir(root):
        main_dir = os.path.join(root, selected_dir)
        print(f'\nLooking at: {selected_dir}'
               '\nSelecting region of interest')
        roi_file = os.path.join(main_dir, os.listdir(main_dir)[0])
        x1, y1, x2, y2 = ui.ROI(file_path=roi_file,
                                graph_title=f'{selected_dir}',
                                osa=osa)
        trim_spec.update({f'{selected_dir}':(round(int(x1)),round(int(x2)))})
        return trim_spec
