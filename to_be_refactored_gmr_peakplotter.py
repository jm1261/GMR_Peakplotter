import os
import numpy as np
import matplotlib.pyplot as plt
import csv
import shutil
import GMR.InputOutput as io
import GMR.DataPreparation as dp
import GMR.PeakFunctions as pf
import GMR.UserInput as ui


## Configure current working directory ##
root = io.config_dir_path()


## Choose the photonic crystal ##
sensor_dict = {
    'Nanohole_Array' : 0,
    'GMR' : 1,
}
sensor_choice = ui.user_in(choice_dict=sensor_dict)
sensor = [name for name, number in sensor_dict.items()
          if number == sensor_choice]


step_size_dict = {
    '1' : 0,
    '0.1' : 1,
    '0.01' : 2,
    '0.001' : 3,
}
## Select region of interest for first spectrum in each experiment directory ##
trim_spec_dict = {}
for selected_date in os.listdir(root):
    date_dir = os.path.join(root, selected_date)
    solute_dir = os.path.join(date_dir, os.listdir(date_dir)[0])
    roi_file = os.path.join(solute_dir, os.listdir(solute_dir)[0])

    wavelength, intensity, file_name = io.csv_in(file_path=roi_file)
    x1, x2 = ui.ROI(x=wavelength,
                    y=intensity,
                    file_name=file_name)
    print(x1, x2)
    step_size_choice = ui.user_in(choice_dict=step_size_dict)
    step_size = [size for size, number in step_size_dict.items()
                 if number == step_size_choice]
    trim_spec_dict.update( { f'{date_dir}' : (x1, x2, step_size[0]) } )


## Background calibration, find the peak shifts for solutes ##
bg_string = 'Background.csv'
for selected_date in os.listdir(root):
    date_dir = os.path.join(root, selected_date)
    print(f'Looking at: {selected_date}'
          '\nBackground Calibration')

    bg_dir = os.path.join(date_dir, 'Background')
    bg_datafiles = io.extract_files(dir_path=bg_dir,
                                    file_string=bg_string)

    for index, selected_file in enumerate(bg_datafiles):
        file = os.path.join(bg_dir, selected_file)
        zero_file = os.path.join(bg_dir, f'{sensor[0]}_{bg_string}')

        wavelength, intensity, file_name = io.csv_in(file_path=file)
        wav_naught, int_naught, zero_name = io.csv_in(file_path=zero_file)

        fig, ax = plt.subplots(1, 1, figsize=[10,7])
        ax.plot(wavelength, intensity, 'r', lw=2, label=file_name)
        ax.plot(wav_naught, int_naught, 'b', lw=2, label=zero_name)
        ax.grid(True)
        ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})
        ax.set_xlabel('Wavelength [nm]', fontsize=14)
        ax.set_ylabel('Intensity', fontsize=14)
        ax.set_title(file_name, fontsize=18)
        ax.tick_params(axis='both', which='major', labelsize=14)
        fig.tight_layout()
        plt.savefig(os.path.join(bg_dir, f'{file_name}.png'))
        fig.clf()
        plt.close(fig)

        file_name, bg_peak, peak_shift = pf.bg_peaks(file_path=file,
                                                     zero_path=zero_file)

        with open('Background_Peaks.csv', 'a', newline='') as outfile:
            writer = csv.writer(outfile, delimiter='\t')
            writer.writerow([file_name] +
                            [bg_peak] +
                            [peak_shift])

        io.update_progress( index / len(bg_datafiles) )
    shutil.copy('Background_Peaks.csv', bg_dir)
    os.remove('Background_Peaks.csv')


## Trim spectrum down to region of interest, and correct time stamp ##
#for selected_date in os.listdir(root):
#    date_dir = os.path.join(root, selected_date)
#
#    for selected_dir in os.listdir(date_dir):
#        solute_dir = os.path.join(date_dir, selected_dir)
#
#        if 'Background' in solute_dir:
#            continue
#        elif 'Graphs' in solute_dir:
#            continue
#        elif 'Results' in solute_dir:
#            continue
#        elif 'TimeCorrected' in solute_dir:
#            continue
#        elif 'TimeAdjusted' in solute_dir:
#            continue
#
#        print(f'Looking at: {solute_dir}'
#              '\nTime Stamp Correcting')
#
#        dir_params = dp.solute_finder(dir_path=date_dir)
#        dp.time_sort(in_dir=solute_dir,
#                     dir_params=dir_params,
#                     main_dir=date_dir,
#                     x1=trim_spec_dict[f'{date_dir}'][0],
#                     x2=trim_spec_dict[f'{date_dir}'][1],
#                     step=trim_spec_dict[f'{date_dir}'][2])
#        dir_params = dp.solute_finder(f'{solute_dir}_TimeAdjusted')
#        dp.time_correct(in_dir=f'{solute_dir}_TimeAdjusted',
#                        dir_params=dir_params,
#                        main_dir=date_dir)
#        shutil.rmtree(f'{solute_dir}_TimeAdjusted')
