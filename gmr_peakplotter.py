import os
import GMR.InputOutput as io
import GMR.UserInput as ui
import GMR.DataPreparation as dp
import matplotlib.pyplot as plt
import GMR.PeakFunctions as pf
import csv
import shutil


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


## Select region of interest for background calibrations ##
trim_spec = {}
bg_string = 'Background.csv'
for selected_date in os.listdir(root):
    date_dir = os.path.join(root, selected_date)
    print(f'\nLooking at: {selected_date}'
           '\nBackground Region of Interest')

    bg_dir = os.path.join(root, selected_date, 'Background')
    roi_file = os.path.join(bg_dir, f'{sensor[0]}_{bg_string}')
    x1, x2 = ui.ROI(file_path=roi_file)
    trim_spec.update({f'{date_dir}' : (x1, x2)})


## Correct background measurements and find peaks for reference ##
for selected_date in os.listdir(root):
    date_dir = os.path.join(root, selected_date)
    print(f'\nLooking at: {selected_date}'
           '\nBackground Calibration')

    bg_dir = os.path.join(date_dir, 'Background')
    bg_datafiles = io.extract_files(dir_path=bg_dir,
                                    file_string=bg_string)

    x1 = round(int(trim_spec[f'{date_dir}'][0]))
    x2 = round(int(trim_spec[f'{date_dir}'][1]))

    for index, selected_file in enumerate(bg_datafiles):
        file = os.path.join(bg_dir, selected_file)
        pwr_spec = os.path.join(bg_dir, f'Halogen_{bg_string}')
        zero_file = os.path.join(bg_dir, f'{sensor[0]}_{bg_string}')

        if 'Halogen' in file:
            continue
        else:
            wl, int, file_name = dp.interp_spec(file_path=file,
                                                pwr_spec=pwr_spec,
                                                x1=x1,
                                                x2=x2)
            zero_wl, zero_int, zero_name = dp.interp_spec(file_path=zero_file,
                                                          pwr_spec=pwr_spec,
                                                          x1=x1,
                                                          x2=x2)
            halo_wl, halo_int, halo_name = io.csv_in(file_path=pwr_spec)

            fig, ax = plt.subplots(1, 1, figsize=[10,7])
            ax.plot(wl, int, 'r', lw=2, label=file_name)
            ax.plot(zero_wl, zero_int, 'b', lw=2, label=zero_name)
            ax.plot(halo_wl, halo_int, 'k', lw=2, label=halo_name)
            ax.grid(True)
            ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})
            ax.set_xlabel('Wavelength [nm]', fontsize=14)
            ax.set_ylabel('Intensity', fontsize=14)
            ax.set_title(file_name, fontsize=18)
            ax.set_xlim(x1, x2)
            ax.tick_params(axis='both', which='major', labelsize=14)
            fig.tight_layout()
            plt.savefig(os.path.join(bg_dir, f'{file_name}.png'))
            fig.clf()
            plt.close(fig)

            file_peak = pf.find_peak(wavelength=wl,
                                     intensity=int)
            zero_peak = pf.find_peak(wavelength=zero_wl,
                                     intensity=zero_int)

            peak_shift = float(file_peak) - float(zero_peak)

            with open('Background_Peaks.csv', 'a', newline='') as outfile:
                writer = csv.writer(outfile, delimiter=',')
                writer.writerow([file_name] +
                                [file_peak] +
                                [peak_shift])

        io.update_progress(index / len(bg_datafiles))
    shutil.copy('Background_Peaks.csv', bg_dir)
    os.remove('Background_Peaks.csv')


## Trim spectrum down to region of interest, and correct time stamp ##
## Find Peaks in trimmed spectrum ##
for selected_date in os.listdir(root):
    date_dir = os.path.join(root, selected_date)

    xi = round(int(trim_spec[f'{date_dir}'][0]))
    xf = round(int(trim_spec[f'{date_dir}'][1]))

    for selected_dir in os.listdir(date_dir):
        solute_dir = os.path.join(date_dir, selected_dir)

        pwr_spec = os.path.join(date_dir,
                                'Background',
                                f'Halogen_{bg_string}')

        if 'Background' in solute_dir:
            continue
        elif 'Graphs' in solute_dir:
            continue
        elif 'Results' in solute_dir:
            continue
        elif 'TimeCorrected' in solute_dir:
            continue
        elif 'TimeAdjusted' in solute_dir:
            continue

        else:
            print(f'Looking at: {solute_dir}'
                   '\nTime stamp correcting')

            dir_params = dp.solute_finder(date_dir)
            dp.time_sort(in_dir=solute_dir,
                         dir_params=dir_params,
                         main_dir=date_dir,
                         x1=xi,
                         x2=xf,
                         pwr_spec=pwr_spec)

            dir_params = dp.solute_finder(f'{solute_dir}_TimeAdjusted')
            dp.time_correct(in_dir=f'{solute_dir}_TimeAdjusted',
                            dir_params=dir_params,
                            main_dir=date_dir)

            shutil.rmtree(f'{solute_dir}_TimeAdjusted')

            print('\nFinding Peaks')
            time_c_dir = f'{solute_dir}_TimeCorrected'
            results_dir = os.path.join(selected_date, 'Results')
            io.check_dir_exists(results_dir)

            dir_params = dp.solute_finder(time_c_dir)
            data_files = io.extract_files(dir_path=time_c_dir,
                                          file_string='_'.join(dir_params[0:2]))
            zero_file = os.path.join(time_c_dir, data_files[0])

            outfile_name = (str('_'.join(dir_params[0:-1])) + '_Peaks.csv')
            with open(outfile_name, 'a', newline='') as outfile:
                writer = csv.writer(outfile, delimiter=',')
                writer.writerow(['Time [s]'] +
                                ['Peak [nm]'] +
                                ['Peak Shift [nm]'])

                for index, selected_file in enumerate(data_files):
                    file = os.path.join(time_c_dir, selected_file)
                    time_stamp, peak, peak_shift = dp.peak_shift(file,
                                                                 zero_file)
                    writer.writerow([time_stamp] + [peak] + [peak_shift])
                    io.update_progress(index / len(data_files))

            shutil.copy(outfile_name, results_dir)
            os.remove(outfile_name)

            dir_params = dp.solute_finder(solute_dir)
            date_files = io.extract_files(dir_path=results_dir,
                                          file_string='_'.join(dir_params)
                                                      + '_Peaks.csv')
            print(f'\nFiles to be processed: {date_files}')

            for index, selected_file in enumerate(date_files):
                file = os.path.join(results_dir, selected_file)
                file_name = io.get_filename(file)

                bg_file_string = ['DI_Background',
                                  f'{sensor}_Background',
                                  '_'.join(dir_params[0:2]) + '_Background',
                                  '1M_' + dir_params[1] + '_Background',
                                  '2M_' + dir_params[1] + '_Background',
                                  '3M_' + dir_params[1] + '_Background',
                                  '4M_' + dir_params[1] + '_Background']

                bg_file = os.path.join(bg_dir, 'Background_Peaks.csv')

                names, bg_peak, bg_shift = np.genfromtxt(bg_file,
                                                         delimiter=',',
                                                         dtype=(str),
                                                         unpack=True)
                time, peak, peak_shift = np.genfromtxt(file,
                                                       delimiter=',',
                                                       unpack=True)
                time *= 1/60

                fig, ax = plt.subplots(1, 1, figsize=[10,7])
                ax.plot(time, peak, 'b.', label=' '.join(file_name.split('_')
                                                         [0:2]))
                ax.grid(True)
                ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})

                for index, name in enumerate(names):
                    if name in bg_file_string:
                        ax.axhline(y=float(bg_peak[index]),
                                   linewidth=2,
                                   color='C' + str(index % 9),
                                   linestyle=':')
                        ax.text(x=2 * index,
                                y=(float(bg_peak[index])),
                                s=' '.join(name.split('_')[0:-1]),
                                bbox=dict(facecolor='white',
                                          edgecolor='none',
                                          alpha=0.5),
                                horizontalalignment='center',
                                verticalalignment='center',
                                fontsize=8)

                ax.set_xlabel('Time [min]', fontsize=14)
                ax.set_ylabel('Peak [nm]', fontsize=14)
                ax.set_title(' '.join(file_name.split('_')[0:2]), fontsize=18)
                ax.tick_params(axis='both', which='major', labelsize=14)
                fig.tight_layout()

                #plt.show()
                out_name = f'{file_name}.png'
                out_path = os.path.join(results_dir, out_name)
                plt.savefig(out_path)
                fig.clf()
                plt.close()

                fig, ax = plt.subplots(1, 1, figsize=[10,7])
                ax.plot(time, peak_shift, 'r.',
                        label=' '.join(file_name.split('_')[0:2]))
                ax.grid(True)
                ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})

                for index, name in enumerate(name):
                    if name in bg_file_string:
                        ax.axhline(y=float(bg_shift[index]),
                                   linewidth=2,
                                   color='C' + str(index % 9),
                                   linestyle=':')
                        ax.text(x=2 * index,
                                y=(float(bg_shift[index])),
                                s=' '.join(name.split('_')[0:-1]),
                                bbox=dict(facecolor='white',
                                          edgecolor='none',
                                          alpha=0.5),
                                horizontalalignment='center',
                                verticalalignment='center',
                                fontsize=8)

                ax.set_xlabel('Time [min]', fontsize=14)
                ax.set_ylabel('Peak Shift [nm]', fontsize=14)
                ax.set_title(' '.join(file_name.split('_')[0:2]), fontsize=18)
                ax.tick_params(axis='both', which='major', labelsize=14)
                fig.tight_layout()

                #plt.show()
                out_name = f'{file_name}_Shift.png'
                out_path = os.path.join(results_dir, out_name)
                plt.savefig(out_path)
                fig.clf()
                plt.close()
