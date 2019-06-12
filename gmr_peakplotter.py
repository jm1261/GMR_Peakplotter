import os
import numpy as np
import matplotlib.pyplot as plt
import csv
import shutil

import GMR.InputOutput as io
import GMR.DataPreparation as dprep
import GMR.DataProcessing as dproc

sensor = 'Nanohole_Array' ## Set this to the photonic crystal used ##

root = io.config_dir_path()

for date_dir in os.listdir(root):
    selected_date = os.path.join(root,
                                 date_dir)
    print(f'Looking at: {date_dir}')

    print('Background Calibration')
    bg_dir = os.path.join(selected_date,
                          'Background')
    bg_datafiles = io.extract_files(dir_name=bg_dir,
                                    file_string='_Background.csv')

    for index, selected_file in enumerate(bg_datafiles):
        file = os.path.join(bg_dir,
                            selected_file)
        zero_file = os.path.join(bg_dir,
                                 f'{sensor}_Background.csv')

        wavelength, intensity, file_name = io.csv_in(file)
        wav_naught, int_naught, zero_name = io.csv_in(zero_file)

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

        graph_out_path = os.path.join(bg_dir,
                                      f'{file_name}.png')
        plt.savefig(graph_out_path)
        fig.clf()
        plt.close(fig)

        file_name, bg_peak, peak_shift = dproc.bg_peaks(file=file,
                                                        zero_file=zero_file)

        with open('Background_Peaks.csv', 'a', newline='') as outfile:
            writer = csv.writer(outfile, delimiter='\t')
            writer.writerow([file_name]
                            + [bg_peak]
                            + [peak_shift])

        io.update_progress(index / len(bg_datafiles))

    shutil.copy('Background_Peaks.csv', bg_dir)
    os.remove('Background_Peaks.csv')

    print(f'\nFiles to be processed: {os.listdir(selected_date)}')

    for exp_dir in os.listdir(selected_date):
        solute_dir = os.path.join(selected_date,
                                  exp_dir)

        if 'Background' in exp_dir:
            print(f'\n{solute_dir} skipped')
        elif 'Graphs' in exp_dir:
            print(f'\n{solute_dir} skipped')
        elif 'Results' in exp_dir:
            print(f'\n{solute_dir} skipped')
        elif 'TimeCorrected' in exp_dir:
            print(f'\n{solute_dir} skipped')
        elif 'TimeAdjusted' in exp_dir:
            print(f'\n{solute_dir} skipped')

        else:
            print('\nCorrecting Time Stamp')
            dir_params = dprep.solute_finder(solute_dir)
            dprep.time_sort(in_dir_name=solute_dir,
                            dir_params=dir_params,
                            main_dir=selected_date)
            dir_params = dprep.solute_finder(f'{solute_dir}_TimeAdjusted')
            dprep.time_correct(in_dir_name=f'{solute_dir}_TimeAdjusted',
                               dir_params=dir_params,
                               main_dir=selected_date)
            shutil.rmtree(f'{solute_dir}_TimeAdjusted')

            print('\nFinding Peaks')
            timec_dir = f'{solute_dir}_TimeCorrected'
            results_dir = os.path.join(selected_date,
                                       'Results')
            io.check_dir_exists(results_dir)

            dir_params = dprep.solute_finder(timec_dir)
            data_files = io.extract_files(dir_name=timec_dir,
                                          file_string='_'.join(dir_params
                                                               [0:2]))

            zero_file = os.path.join(timec_dir,
                                     data_files[0])

            outfile_name = (str('_'.join(dir_params[0:-1]))
                           + '_Peaks.csv')
            with open(outfile_name, 'a', newline='') as outfile:
                writer = csv.writer(outfile, delimiter=',')
                writer.writerow(['Wavelength [nm]']
                                + ['Peak [nm]']
                                + ['Peak Shift [nm]'])

                for index, selected_file in enumerate(data_files):
                    file = os.path.join(timec_dir,
                                        selected_file)
                    #zero_file = os.path.join(bg_dir,
                    #                         f'{sensor}_Background.csv')

#                    wavelength, intensity, file_name = io.array_in(file)
#
#                    fig, ax = plt.subplots(1, 1, figsize=[10,7])
#                    ax.plot(wavelength, intensity, 'b', lw=2, label=file_name)
#                    ax.grid(True)
#                    ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})
#                    ax.set_xlabel('Wavelength [nm]', fontsize=14)
#                    ax.set_ylabel('Intensity [au]', fontsize=14)
#                    ax.set_title(file_name, fontsize=18)
#                    ax.tick_params(axis='both', which='major', labelsize=14)
#                    fig.tight_layout()
#                    ## Uncomment for saving out spectrums ##
#                    out_dir_name = '_'.join(dir_params[0:-1]) + '_Graphs'
#                    out_dir = os.path.join(selected_date,
#                                           out_dir_name)
#                    io.check_dir_exists(out_dir)
#                    out_path = os.path.join(out_dir,
#                                            f'{file_name}.png')
#                    plt.savefig(out_path)
#                    fig.clf()
#                    plt.close(fig)

                    time_stamp, peak, peak_shift = dproc.peak_shift(file,
                                                                    zero_file)
                    writer.writerow([time_stamp] + [peak] + [peak_shift])
                    io.update_progress(index / len(data_files))

            shutil.copy(outfile_name, results_dir)
            os.remove(outfile_name)

            dir_params = dprep.solute_finder(solute_dir)
            data_files = io.extract_files(dir_name=results_dir,
                                          file_string='_'.join(dir_params)
                                                      + '_Peaks.csv')

            print(f'\nFiles to be processed: {data_files}')

            for index, selected_file in enumerate(data_files):
                file = os.path.join(results_dir,
                                    selected_file)
                file_name = io.get_filename(file)

                bg_file_string = ['1M_Salt_Background',
                                  '_'.join(dir_params[0:2]) + '_Background',
                                  '1M_Salt_Paper_Background',
                                  '_'.join(dir_params[0:2]) + '_Background',
                                  f'{sensor}_Background',
                                  'DI_Background',
                                  'IPA_Background']

                bg_file = os.path.join(bg_dir,
                                       'Background_Peaks.csv')
                names, bg_peak, bg_peak_shift = np.genfromtxt(bg_file,
                                                              delimiter='\t',
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
                out_path = os.path.join(results_dir,
                                        out_name)
                plt.savefig(out_path)
                fig.clf()
                plt.close()

                fig, ax = plt.subplots(1, 1, figsize=[10,7])
                ax.plot(time, peak_shift, 'r.',
                        label=' '.join(file_name.split('_')[0:2]))
                ax.grid(True)
                ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})
                for index, name in enumerate(names):
                    if name in bg_file_string:
                        ax.axhline(y=float(bg_peak_shift[index]),
                                   linewidth=2,
                                   color='C' + str(index % 9),
                                   linestyle=':')

                        ax.text(x=2 * index,
                                y=(float(bg_peak_shift[index])),
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
                out_path = os.path.join(results_dir,
                                        out_name)
                plt.savefig(out_path)
                fig.clf()
                plt.close()
