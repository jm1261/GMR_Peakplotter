import os
import GMR.InputOutput as io
import GMR.UserInput as ui
import GMR.DataPreparation as dp
import matplotlib.pyplot as plt
import GMR.PeakFunctions as pf
import GMR.SectionFunctions as sf


## Configure current working directory ##
root = io.config_dir_path()

## Choose the photonic crystal ##
sensor_dict = {
    'Nanohole_Array' : 0,
    'GMR' : 1,
}
sensor_choice = ui.user_in(choice_dict=sensor_dict,
                           string='Sensor used')
sensor = [name for name, number in sensor_dict.items()
          if number == sensor_choice][0]

happy_choice_dict = {
    'Yes' : 0,
    'No' : 1,
}

bg_string = 'Background.csv'

happy = 1
## Select whether data taken with osa or splicco ##
happy = 1
while happy == 1:
    osa_choice = sf.data_collection(root=root)
    happy_choice = ui.user_in(choice_dict=happy_choice_dict,
                              string='Happy with choice?')
    happy = [number for name, number in happy_choice_dict.items()
             if number == happy_choice][0]
print(osa_choice)

happy = 1
## Find region of interest for background and peaks ##
while happy == 1:
    trim_spec = sf.region_of_interest(root=root,
                                      bg_string=bg_string,
                                      sensor=sensor,
                                      osa_choice=osa_choice)

    happy_choice = ui.user_in(choice_dict=happy_choice_dict,
                              string='Happy with choice?')
    happy = [number for name, number in happy_choice_dict.items()
             if number == happy_choice][0]
print(trim_spec)

## Correct background measurements and find peaks for reference ##
for selected_dir in os.listdir(root):
    main_dir = os.path.join(root, selected_dir)
    x1, x2 = trim_spec[f'{selected_dir}']
    print(f'\nLooking at: {selected_dir}'
           '\nBackground calibration')
    osa = osa_choice[f'{selected_dir}']

    ## Find the background measurement peaks and create csv with the ##
    ## background peaks and the peak shift to the sensor             ##
    sf.background_peaks(main_dir=main_dir,
                        bg_string=bg_string,
                        sensor=sensor,
                        x1=x1,
                        x2=x2,
                        osa=osa)
    #sf.sensor_sensitivity(main_dir=main_dir,
    #                      sensor=sensor)

## Find peaks in trimmed spectrum ##
for selected_dir in os.listdir(root):
    main_dir = os.path.join(root, selected_dir)
    x1, x2 = trim_spec[f'{selected_dir}']
    print(f'\nLooking at {selected_dir}')

    osa = osa_choice[f'{selected_dir}']

    for selected_dir in os.listdir(main_dir):
        solute_dir = os.path.join(main_dir, selected_dir)
        pwr_spec = os.path.join(main_dir,
                                'Background',
                                f'Halogen_{bg_string}')

        if 'Background' in solute_dir:
            pass
        elif 'Graphs' in solute_dir:
            pass
        elif 'Results' in solute_dir:
            pass
        elif 'TimeCorrected' in solute_dir:
            pass
        elif 'TimeAdjusted' in solute_dir:
            pass

        else:
            sf.time_correct_files(main_dir=main_dir,
                                  solute_dir=solute_dir,
                                  bg_string=bg_string,
                                  x1=x1,
                                  x2=x2,
                                  pwr_spec=pwr_spec,
                                  osa=osa)

            sf.find_peaks(main_dir=main_dir,
                          solute_dir=solute_dir)

## Plot results as peak and peak shift against time ##
for selected_dir in os.listdir(root):
    main_dir = os.path.join(root, selected_dir)
    sf.plot_results(main_dir=main_dir)
