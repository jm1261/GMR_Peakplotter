import os
import matplotlib.pyplot as plt
import numpy as np
from shutil import copy
from scipy.signal import find_peaks
import csv

import OLD_GMR.org_functions as of
import OLD_GMR.background_calibration as bc
import OLD_GMR.time_correct as tc
import OLD_GMR.peak_finder as pf
import OLD_GMR.plot_results as pr


sensor = 'Nanohole_Array'
main_dir = of.config_dir_path()
date_directories = os.listdir(main_dir)

for date_dir in date_directories:
    selected_dir = os.path.join(main_dir,
                                date_dir)
    exp_directories = os.listdir(selected_dir)

    bg_dir = os.path.join(selected_dir, 'Background')
    bg_datafiles = of.extract_files(dir_name=bg_dir,
                                    file_string='_Background.csv')
    print('\nBackground Calibration')

    for index, selected_file in enumerate(bg_datafiles):
        file = os.path.join(bg_dir, selected_file)
        zero_file = os.path.join(bg_dir, f'{sensor}_Background.csv')
        bc.bg_plot(file=file,
                   zero_file=zero_file,
                   out_dir=bg_dir,
                   save=True)
        file_name, bg_peak, peak_shift = bc.bg_peaks(file, zero_file)

        with open('Background_Peaks.csv', 'a', newline='') as outfile:
            writer = csv.writer(outfile, delimiter=',')
            writer.writerow([file_name] + [bg_peak] + [peak_shift])

        of.update_progress(index / len(bg_datafiles))

    copy('Background_Peaks.csv', bg_dir)
    os.remove('Background_Peaks.csv')

    for exp_dir in exp_directories:
        solute_dir = os.path.join(selected_dir, exp_dir)

        if 'Background' in exp_dir:
            print(f'\n{solute_dir} skipped')
        elif 'TimeAdjusted' in exp_dir:
            print(f'\n{solute_dir} skipped')
        elif 'TimeCorrected' in exp_dir:
            print(f'\n{solute_dir} skipped')
        elif 'Results' in exp_dir:
            print(f'\n{solute_dir} skipped')

        else:
            print('\nCorrecting Time Stamp')
            dir_params = tc.solute_finder(solute_dir)
            tc.time_sort(in_dir_name=solute_dir,
                         dir_params=dir_params,
                         main_dir=selected_dir)
            dir_params = tc.solute_finder(f'{solute_dir}_TimeAdjusted')
            tc.time_correct(in_dir_name=f'{solute_dir}_TimeAdjusted',
                            dir_params=dir_params,
                            main_dir=selected_dir)
            os.rmdir(f'{solute_dir}_TimeAdjusted')

            time_c_dir = f'{solute_dir}_TimeCorrected'
            print('\nFinding Peaks')

            dir_params = tc.solute_finder(time_c_dir)
            print(' ')
            print(dir_params)

            results_dir = os.path.join(selected_dir, 'Results')
            of.check_dir_exists(results_dir)

            data_files = of.extract_files(dir_name=time_c_dir,
                                          file_string='_'.join(dir_params[0:2]))

            outfile_name = file_name='_'.join(dir_params[0:-1]) + '_Peaks.csv'
            with open(outfile_name, 'a', newline='') as outfile:
                writer = csv.writer(outfile, delimiter=',')
                writer.writerow(['Wavelength [nm]']
                                 + ['Peak [nm]']
                                 + ['Peak Shift [nm]'])

                for index, selected_file in enumerate(data_files):
                    file = os.path.join(time_c_dir, selected_file)
                    zero_file_name = f'{sensor}_Background.csv'
                    zero_file = os.path.join(bg_dir, zero_file_name)

                    pf.plot_spectrum(file=file,
                                     dir_params=dir_params,
                                     main_dir=selected_dir,
                                     save=False)

                    time_stamp, peak, peak_shift = pf.peak_shift(file,
                                                                 zero_file)
                    writer.writerow([time_stamp] + [peak] + [peak_shift])

                    of.update_progress(index / len(data_files))

            copy(outfile_name, results_dir)
            os.remove(outfile_name)
            os.rmdir(f'{solute_dir}_TimeCorrected')

            dir_params = tc.solute_finder(solute_dir)

            data_files = of.extract_files(dir_name=results_dir,
                                          file_string='_'.join(dir_params[0:-1]))
            print('\nFiles to be processed: ' + str(data_files))

            for index, selected_file in enumerate(data_files):
                file = os.path.join(results_dir, selected_file)
                pr.plot_peaks(file=file,
                              bg_dir=bg_dir,
                              file_params=dir_params,
                              main_dir=selected_dir,
                              sensor=sensor,
                              save=True)
                pr.plot_peak_shift(file=file,
                                   bg_dir=bg_dir,
                                   file_params=dir_params,
                                   main_dir=selected_dir,
                                   sensor=sensor,
                                   save=True)

                of.update_progress(index / len(data_files))
