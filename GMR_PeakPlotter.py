import os
import GMR.Organise as org
import GMR.BackgroundCalibration as bc
import GMR.InputOutput as io
import GMR.DataProcessing as dp

## Firstly we configure the directory path. In the directory in which this   ##
## code sits, the following function creates a new directory called          ##
## "Put_Data_Here". Please copy any data directory (folder containing all    ##
## the spectra you have collected) into the "Put_Data_Here" directory.       ##
## We call the "Put_Data_Here" directroy our 'root'.                         ##
root = org.config_dir_path()

## The first time you run this code (or if the "Put_Data_Here" directory is  ##
## not present) you will see a message that reads:                           ##
## "Place data into "Put_Data_Here" folder with this code"                   ##
## "Once complete, restart the code"                                         ##
## Follow the instructions and restart the code to process collected data    ##

## Keep in mind that only data collected using either splicco or osa can be ##
## processed at one time. This code does not work for cross-software data   ##
## data collection.                                                         ##
global thorlabs_osa
thorlabs_osa = True

## Now we need to trim the spectrums down to a region of interest that we   ##
## care about. This will help with processing speeds as we don't have to    ##
## carry forward any unwanted data. This functions does not alter raw data. ##
trim_spec = io.region_of_interest(root=root,
                                  osa=thorlabs_osa)

## Now lets look at the background data, this should be spectrums for the   ##
## sensor, or perhaps a known refractive index analyte. These spectrums     ##
## must be stored in a directory called 'Background', and must be either in ##
## the root, or a main directory path. If such a directory exists, there    ##
## must also be a light source file to which the others can be normalised.  ##
## This is currently set to 'Halogen.csv'                                   ##
## The user is presented with a choice, which enables them to skip this     ##
## background step.                                                         ##
for selected_dir in os.listdir(root):
    background_choice = bc.background_choice()
    if background_choice == 'True':
        sensor_choice = bc.sensor_choice()
        x1, x2 = trim_spec[f'{selected_dir}']
        bc.background_peaks(main_dir=root,
                            bg_string='_Background.csv',
                            sensor=sensor_choice,
                            x1=x1,
                            x2=x2,
                            osa=thorlabs_osa)
    else:
        pass

## Now we can adjust the time stamps on each of the data sets so that the   ##
## file names contain the time step (in seconds). This makes life easier    ##
## going forward, as we don't have to manually add our time step every time ##
## we run a different experiment.                                           ##
for selected_dir in os.listdir(root):
    power_spectrum = os.path.join(root,
                                  'Background',
                                  'Halogen_Background.csv')
    if 'Background' in selected_dir:
        pass
    elif 'Graphs' in selected_dir:
        pass
    elif 'Results' in selected_dir:
        pass
    elif 'TimeCorrected' in selected_dir:
        pass
    elif 'TimeAdjusted' in selected_dir:
        pass
    else:
        x1, x2 = trim_spec[f'{selected_dir}']
        #dp.time_correct_files(main_dir=root,
        #                      solute_dir=selected_dir,
        #                      x1=x1,
        #                      x2=x2,
        #                      osa=thorlabs_osa,
        #                      pwr_spec=power_spectrum)
        dp.find_peaks(main_dir=root,
                      solute_dir=selected_dir)
