import os
import numpy as np
import matplotlib.pyplot as plt

root = os.getcwd()
put_data_here = os.path.join(root, 'Put_Data_Here')
main_dir = os.path.join(put_data_here, 'Solute_Concentrations_mk3')
bg_dir = os.path.join(main_dir, 'Background')

ri_file = os.path.join(bg_dir, 'RI_Measuements.txt')
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
    riu_dict.update({name: float(riu[index])})

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
        'x2' : [],
        'xy' : []}

for label, coord in riu_peak_dict.items():
    data['x'].append(coord[0])
    data['y'].append(coord[1])
    data['label'].append(label)
    data['x2'].append(coord[0] ** 2)
    data['xy'].append(coord[0] * coord[1])

print(data)
