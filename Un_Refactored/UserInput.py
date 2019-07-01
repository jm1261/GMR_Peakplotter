import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import time
import GMR.InputOutput as io


def interp_spec_trim(file_path,
                     start,
                     end,
                     step):
    '''
    Allows the user to modify the data range processed through this code.
    With a given region of interest (ROI) the fucntion cuts out the
    unwanted data from each csv file before passing it along.
    Args:
        file: <string> file path to csv spectrum
        start: <float/int> start point (wavelength) of ROI
        end: <float/int> end point (wavlength) of ROI
        step: <float/int> step size (wavelength) of ROI
    Returns:
        wavelength: <array> wavelength range
        intensity: <array> intensity values at wavelengths
        file_name: <string> file name without extension
    '''
    wav, int, file_name = io.csv_in(file)
    wavelength = np.arange(start,
                           end,
                           step)
    intensity = np.interp(x=wavelength,
                          xp=wav,
                          fp=int)
    return wavelength, intensity, file_name


def on_select(eclick, erelease):
    '''
    eclick and erelease are the press and release events
    '''
    global x1, y1, x2, y2
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
    print(" The button you used were: %s %s" % (eclick.button, erelease.button))
    return x1, y1, x2, y2


def toggle_selector(event):
    print(' Key pressed.')
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print(' RectangleSelector deactivated.')
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print(' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)


def ROI(x, y, file_name):
    '''
    '''
    print('\nPlease select a region of interest'
          '\nWhen you are done, close the graph'
          '\nDefault region of interest set to last selected'
          '\nor full data set if none selected at all.')
    time.sleep(2)

    fig, ax = plt.subplots(1, 1, figsize=[10,7])
    ax.plot(x, y, 'b', lw=2, label=file_name)
    ax.grid(True)
    ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})

    print('\n click --> release')

    #drawtype is 'box'/'line'/'none'
    #buttons are 1, 3 (don't use middle button)
    toggle_selector.RS = RectangleSelector(ax,
                                           on_select,
                                           drawtype='box',
                                           useblit=True,
                                           button=[1, 3],
                                           minspanx=5,
                                           minspany=5,
                                           spancoords='pixels',
                                           interactive=True)

    plt.connect('key_press_event', toggle_selector)
    plt.show()

    return x1, x2


def user_in(choice_dict):
    '''
    Requests input from the user, returns user's choice (as int)
    Returned choice to be used as key to access choice dictionary.
    Args:
        user_choice: <dict> python dictionary keys simple ints, values
                     choice to be made
    '''
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Please choose from the following options, type corresponding'
              'number and press "Enter".')
        for k, v in choice_dict.items():
            print(f'{k} : {v}')
        choice = input('Your choice? ')

        if choice not in str(choice_dict):
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Please enter a valid choice')
            input('Press any key to continue...')
            continue

        break

    return int(choice)
