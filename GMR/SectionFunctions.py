import os
import GMR.UserInput as ui
import GMR.InputOutput as io
import GMR.DataPreparation as dp
import GMR.PeakFunctions as pf
import matplotlib.pyplot as plt
import csv
import shutil
import numpy as np


def data_collection(root):
    '''
    '''
    osa = {}
    osa_dict = {
        'True' : 0,
        'False' : 1,
    }
    for selected_dir in os.listdir(root):
        main_dir = os.path.join(root, selected_dir)
        string = (f'\nLooking at: {selected_dir}'
                   '\nIf osa used, select true')
        osa_choice = ui.user_in(choice_dict=osa_dict, string=string)
        data_collect = [name for name, number in osa_dict.items()
                        if number == osa_choice][0]
        osa.update({f'{selected_dir}' : str(data_collect)})
    return osa


def region_of_interest(root,
                       bg_string,
                       sensor,
                       osa_choice):
    '''
    '''
    trim_spec = {}
    for selected_dir in os.listdir(root):
        main_dir = os.path.join(root, selected_dir)
        print(f'\nLooking at: {selected_dir}'
               '\nSelecting region of interest')
        osa = osa_choice[f'{selected_dir}']
        bg_dir = os.path.join(main_dir, 'Background')
        roi_file = os.path.join(bg_dir, f'{sensor}_{bg_string}')

        x1, y1, x2, y2 = ui.ROI(file_path=roi_file,
                                graph_title=f'{selected_dir}',
                                osa=osa)

        trim_spec.update({f'{selected_dir}' : (round(int(x1)),
                                               round(int(x2)))})

    return trim_spec


def background_peaks(main_dir,
                     bg_string,
                     sensor,
                     x1,
                     x2,
                     osa):
    '''
    '''
    bg_dir = os.path.join(main_dir, 'Background')
    bg_datafiles = io.extract_files(dir_path=bg_dir,
                                    file_string=bg_string)

    pwr_spec = os.path.join(bg_dir, f'Halogen_{bg_string}')
    zero_file = os.path.join(bg_dir, f'{sensor}_{bg_string}')

    zero_wl, zero_int, zero_name = dp.trim_spec(file_path=zero_file,
                                                pwr_spec=pwr_spec,
                                                xi=x1,
                                                xf=x2,
                                                osa=osa)

    guesses_file = os.path.join(bg_dir, bg_datafiles[0])
    guess_wl, guess_int, _, =  dp.trim_spec(file_path=guesses_file,
                                            pwr_spec=pwr_spec,
                                            xi=x1,
                                            xf=x2,
                                            osa=osa)

    best_guesses = pf.best_params(x=guess_wl, y=guess_int)
    _, zero_peak = pf.find_fano(x=zero_wl, y=zero_int,
                                best_params=best_guesses)

    for index, selected_file in enumerate(bg_datafiles):
        file = os.path.join(bg_dir, selected_file)

        if 'Halogen' in file:
            pass
        else:
            wl, int, file_name = dp.trim_spec(file_path=file,
                                              pwr_spec=pwr_spec,
                                              xi=x1,
                                              xf=x2,
                                              osa=osa)
            popt, peak_wavelength = pf.find_fano(x=wl, y=int,
                                                 best_params=best_guesses)

            fig, ax = plt.subplots(1, 1, figsize=[10,7])
            ax.plot(wl, int, 'r', lw=2, label=file_name)
            ax.plot(zero_wl, zero_int, 'b', lw=2, label=zero_name)
            ax.plot(wl, pf.T_fano(wl, *popt), 'k', lw=2, label='Fano Fit')
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
        io.update_progress(index / len(bg_datafiles))
    shutil.copy('Background_Peaks.csv', bg_dir)
    os.remove('Background_Peaks.csv')


def sensor_sensitivity(main_dir,
                       sensor):
    '''
    '''
    bg_dir = os.path.join(main_dir, 'Background')
    ri_file = os.path.join(bg_dir, 'RI_Measurements.txt')
    bg_peaks = os.path.join(bg_dir, 'Background_Peaks.csv')

    names, riu, volume = np.genfromtxt(ri_file,
                                       delimiter=',',
                                       unpack=True,
                                       dtype=(str),
                                       skip_header=1)

    bg_name, peak, peak_shift = np.genfromtxt(bg_peaks,
                                              delimiter=',',
                                              unpack=True,
                                              dtype=(str),
                                              skip_header=1)
    bg_names = []
    for name in bg_name:
        bg_names.append('_'.join(name.split('_')[0:-2]))
    riu_dict = {}
    for index, name in enumerate(names):
        riu_dict.update({name : float(riu[index])})
    bg_peak_dict = {}
    for index, name in enumerate(bg_name):
        bg_peak_dict.update({name : [float(peak[index]),
                                     float(peak_shift[index])]})
    riu_peak_dict = {}
    for name in names:
        if name in bg_name:
            riu_peak_dict.update({name : [riu_dict[name],
                                          bg_peak_dict[name][1]]})

    data = {'x' : [],
            'y' : [],
            'label' : [],
            'x2': [],
            'xy': []}
    for label, coord in riu_peak_dict.items():
        data['x'].append(coord[0])
        data['y'].append(coord[1])
        data['label'].append(label)
        data['x2'].append(coord[0] ** 2)
        data['xy'].append(coord[0] * coord[1])

    fig, ax = plt.subplots(1, 1, figsize=[10,7])
    ax.scatter(data['x'], data['y'], marker='.', color='b')
    ax.set_xlabel('Refractive Index [riu]', fontsize=14)
    ax.set_ylabel('Peak Shift [nm]', fontsize=14)
    ax.set_title(f'{sensor}', fontsize=18)
    if len(riu_peak_dict) == 1:
        m = 0
    else:
        m = dp.gradient(x=data['x'],
                        y=data['y'],
                        xy=data['xy'],
                        x2=data['x2'])
        plt.annotate(f'nm/riu = {m}', xy=(10, 10), xycoords='figure pixels')
    for label, x, y in zip(data['label'], data['x'], data['y']):
        plt.annotate(label, xy=(x, y), fontsize=6)
    out_path = os.path.join(bg_dir, f'{sensor}_sensitivy.png')
    plt.savefig(out_path)
    fig.clf()
    plt.close(fig)


def time_correct_files(main_dir,
                       solute_dir,
                       bg_string,
                       x1,
                       x2,
                       pwr_spec,
                       osa=False):
    '''
    '''
    print(f'\nLooking at: {solute_dir}'
           '\nTime stamp correcting')

    dir_params = dp.solute_finder(solute_dir)
    dp.time_sort(in_dir=solute_dir,
                 dir_params=dir_params,
                 main_dir=main_dir,
                 x1=x1,
                 x2=x2,
                 pwr_spec=pwr_spec,
                 osa=osa)

    dir_params=dp.solute_finder(f'{solute_dir}_TimeAdjusted')
    dp.time_correct(in_dir=f'{solute_dir}_TimeAdjusted',
                    dir_params=dir_params,
                    main_dir=main_dir)

    shutil.rmtree(f'{solute_dir}_TimeAdjusted')


def find_peaks(main_dir,
               solute_dir):
    '''
    '''
    print('\nFinding Peaks')
    time_c_dir = f'{solute_dir}_TimeCorrected'
    results_dir = os.path.join(main_dir, 'Results')
    io.check_dir_exists(results_dir)

    dir_params = dp.solute_finder(time_c_dir)
    data_files = io.extract_files(dir_path=time_c_dir,
                                  file_string='.npy')
    zero_file = os.path.join(time_c_dir, data_files[0])

    zero_wl, zero_int, zero_name = io.array_in(file_path=zero_file)
    best_guesses = pf.best_params(x=zero_wl, y=zero_int)
    _, peak_zero = pf.find_fano(x=zero_wl, y=zero_int,
                                best_params=best_guesses)

    outfile_name = (str('_'.join(dir_params[0:-1])) + '_Peaks.csv')
    with open(outfile_name, 'a', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        writer.writerow(['Time [s]'] +
                        ['Peak [nm]'] +
                        ['Peak Shift [nm]'])

        for index, selected_file in enumerate(data_files):
            file = os.path.join(time_c_dir, selected_file)
            wl, int, file_name = io.array_in(file_path=file)
            time_stamp = file_name.split('_')[::-1][0]
            #if max(int) <= 0.6:
            #    peak = Nan
            #    peak_zero = Nan
            #else:
                #best_guesses[0] = max(int)
            _, peak = pf.find_fano(x=wl, y=int,
                                   best_params=best_guesses)
                #peak = pf.find_peaks(x=wl, y=int)
            peak_shift = float(peak) - float(peak_zero)

            writer.writerow([time_stamp] + [peak] + [peak_shift])
            io.update_progress(index / len(data_files))

    shutil.copy(outfile_name, results_dir)
    os.remove(outfile_name)


def plot_results(main_dir):
    '''
    '''
    results_dir = os.path.join(main_dir, 'Results')

    data_files = io.extract_files(dir_path=results_dir,
                                  file_string='_Peaks.csv')

    for index, selected_file in enumerate(data_files):
        file = os.path.join(results_dir, selected_file)
        file_name = io.get_filename(file)

        time, peak, peak_shift = np.genfromtxt(file,
                                               delimiter=',',
                                               unpack=True)

        time *= 1/60

        fig, ax = plt.subplots(1, 1, figsize=[10,7])
        ax.plot(time, peak, 'b.', label=' '.join(file_name.split('_')
                                                 [0:2]))
        ax.grid(True)
        ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})
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
