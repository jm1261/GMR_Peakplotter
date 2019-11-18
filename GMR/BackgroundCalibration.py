import os
import GMR.UserInput as ui
import GMR.InputOutput as io
import GMR.DataProcessing as dp
import GMR.Organise as org
import matplotlib.pyplot as plt
import csv
import shutil


def sensor_choice():
    '''
    This function allows the user to specify the used sensor during data
    collection. Specifically this is aimed at background measurements that may
    require plotting and normalising to. Options can be added to the sensor
    list (sensor_dict) that suit your data better.
    Args:
        None
    Returns:
        sensor: <string> name of the used sensor
    The returned string should be as named in the user's background files.
    '''
    sensor_dict = {
    'Nanohole_Array' : 0,
    'GMR' : 1,
    }
    sensor_choice = ui.user_in(choice_dict=sensor_dict,
                               string='Sensor used')
    sensor = [name for name, number in sensor_dict.items()
              if number == sensor_choice][0]
    return sensor


def background_peaks(main_dir,
                     bg_string,
                     sensor,
                     x1,
                     x2,
                     osa):
    '''
    Background peaks searches through the background directory for a specific
    measurement batch and selects a region of interest. It then normalises
    the background measurements to the light source (Halogen) and finds the
    resonant wavelength using a fano function. Once it has found the peaks
    it finds the peak shift and peak value and writes them into a csv with the
    name of the file. The file is then moved into the background directory.
    Args:
        main_dir: <string> path to main directory in which the background
                  directory is stored
        bg_string: <string> file string used to determine which files need to
                   be processed
        sensor: <string> name of the photonic crystal file
        x1, x2: <int/float> begging and end wavelength values for region of
                interest
        osa: <bool> if True, osa was used to capture spectrums
    Returns:
        None
    '''
    bg_dir = os.path.join(main_dir, 'Background')
    bg_datafiles = org.extract_files(dir_path=bg_dir,
                                     file_string='_Background.csv')

    power_spectrum = os.path.join(bg_dir, 'Halogen_Background.csv')
    zero_file = os.path.join(bg_dir, f'{sensor}_Background.csv')

    zero_wl, zero_int, zero_name = dp.trim_spec_norm(file_path=zero_file,
                                                     pwr_spec=power_spectrum,
                                                     xi=x1,
                                                     xf=x2,
                                                     osa=osa)

    guesses_file = os.path.join(bg_dir, bg_datafiles[0])
    guesses_wl, guesses_int, _ = dp.trim_spec_norm(file_path=zero_file,
                                                   pwr_spec=power_spectrum,
                                                   xi=x1,
                                                   xf=x2,
                                                   osa=osa)

    best_guesses = dp.best_params(x=guesses_wl, y=guesses_int)
    _, zero_peak = dp.find_fano(x=zero_wl, y=zero_int,
                                best_params=best_guesses)

    for index, selected_file in enumerate(bg_datafiles):
        file = os.path.join(bg_dir, selected_file)

        if 'Halogen' in file:
            pass
        else:
            wl, int, file_name = dp.trim_spec_norm(file_path=file,
                                                   pwr_spec=power_spectrum,
                                                   xi=x1,
                                                   xf=x2,
                                                   osa=osa)
            popt, peak_wavelength = dp.find_fano(x=wl, y=int,
                                                 best_params=best_guesses)

            fig, ax = plt.subplots(1, 1, figsize=[10,7])
            ax.plot(wl, int, 'r', lw=2, label=file_name)
            ax.plot(zero_wl, zero_int, 'b', lw=2, label=zero_name)
            ax.plot(wl, dp.T_fano(wl, *popt), 'k', lw=2, label='Fano Fit')
            ax.grid(True)
            ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})
            ax.set_xlabel('Wavelength [nm]', fontsize=14)
            ax.set_ylabel('Intensity', fontsize=14)
            ax.set_title(file_name, fontsize=18)
            ax.set_xlim(x1, x2)
            ax.tick_params(axis='both', which='major', labelsize=14)
            fig.tight_layout()
            #plt.show()
            plt.savefig(os.path.join(bg_dir, f'{file_name}.png'))
            fig.clf()
            plt.close(fig)

            peak_shift = float(peak_wavelength) - float(zero_peak)

            with open('Background_Peaks.csv', 'a', newline='') as outfile:
                writer = csv.writer(outfile, delimiter=',')
                writer.writerow([file_name] +
                                [peak_wavelength] +
                                [peak_shift])
        org.update_progress(index / len(bg_datafiles))
    shutil.copy('Background_Peaks.csv', bg_dir)
    os.remove('Background_Peaks.csv')


def background_choice():
    '''
    This function allows the user to specificy whether or not they want to
    perform a background calibration. This can only be done if the user
    has a directory called 'Background' within their root or main directory
    path for processing. If there is no background directory then this step
    should be skipped
    '''
    background_dict = {
    'No' : 0,
    'Yes' : 1,
    }
    background_string = ('Do you have a directory called Background within the'
                         ' main directory, or in the root directory, path?')
    background_choice = ui.user_in(choice_dict=background_dict,
                                   string=background_string)
    choice = [name for name, number in background_dict.items()
              if number == background_choice][0]
    if choice == 'No':
        return_choice = 'False'
    else:
        return_choice = 'True'
    return return_choice
