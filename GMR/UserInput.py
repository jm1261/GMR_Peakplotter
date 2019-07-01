import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import time
import GMR.InputOutput as io


def user_in(choice_dict):
    '''
    Requests input from the user, returns user's choice (as int)
    Returned choice to be used as key to access choice dictionary.
    Args:
        user_choice: <dict> python dictionary keys simple ints, values
                     choice to be made
    Returns:
        int(choice): <int> user choice relating to the choice dictionary
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


def ROI(file_path):
    '''
    Utilises interactive matplotlib plots to allow the user to select a
    region of interest (ROI) on a graph, in this case spectrum. Uses the
    rectangle selector widget found within matplotlib to allow the user
    to draw a rectangular box around the area of interest. Can be changed,
    but currently only cares about the initial and final x coordinates
    in the selected region.
    Args:
        file_path: <string> path to file under investigation
    Returns:
        x1: <float> initial x coordinate
        x2: <float> final x coordinate
    Can Return:
        y1: <float> initial y coordinate
        y2: <float> final y coordinate
    '''
    print('\nPlease select a region of interest'
          '\nWhen you are done, close the graph'
          '\nDefault region of interest set to last selected'
          '\nor full data set if none selected at all.')
    time.sleep(2)

    wavelength, intensity = np.genfromtxt(file_path,
                                          delimiter=',',
                                          unpack=True)
    file_name = io.get_filename(file_path=file_path)

    fig, ax = plt.subplots(1, 1, figsize=[10,7])
    ax.plot(wavelength, intensity, 'b', lw=2, label=file_name)
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
