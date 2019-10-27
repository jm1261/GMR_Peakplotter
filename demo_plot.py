import os
import numpy as np
import matplotlib.pyplot as plt


sensor = 'Nanohole_Array'
root = os.getcwd()
target_file = os.path.join(root,
                           'Put_Data_Here',
                           'IgG',
                           'Results',
                           'IgG_Binding_Peaks.csv')
bg_file = os.path.join(root,
                       'Put_Data_Here',
                       'IgG',
                       'Background',
                       'Background_Peaks.csv')


time, peak, peak_shift = np.genfromtxt(target_file,
                                       delimiter=',',
                                       unpack=True)
time /= 60

#names, bg_peak, bg_peak_shift = np.genfromtxt(bg_file,
#                                              delimiter='\t',
#                                              dtype=(str),
#                                              unpack=True)

file_name = os.path.splitext(os.path.basename(target_file))[0]
label_name = file_name.split('_')[0:2]

#bg_file_string = ['1M_Salt_Background',
#                  '_'.join(label_name) + '_Background',
#                  '1M_Salt_Paper_Background',
#                  '_'.join(label_name) + '_Background',
#                  f'{sensor}_Background',
#                  'DI_Background',
#                  'IPA_Background']
#print(bg_file_string)

fig, ax = plt.subplots(1, 1, figsize=[10,7])
ax.plot(time, peak_shift, 'r.', label=' '.join(label_name))
ax.grid(True)
ax.legend(frameon=True, loc=0, ncol=1, prop={'size':12})

#for index, name in enumerate(names):
#    if name in bg_file_string:
#        ax.axhline(y=float(bg_peak_shift[index]),
#                   linewidth=2,
#                   color='b',
#                   linestyle=':')
#
#        ax.text(x=2 * index,
#                y=(float(bg_peak_shift[index])),
#                s=' '.join(name.split('_')[0:-1]),
#                bbox=dict(facecolor='white',
#                          edgecolor='none',
#                          alpha=0.5),
#                horizontalalignment='center',
#                verticalalignment='center',
#                fontsize=8)
#
#ax.set_xlim(0, 14)
ax.set_ylim(22, 23)

ax.set_xlabel('Time [min]', fontsize=14)
ax.set_ylabel('Peak Shift [nm]', fontsize=14)
ax.set_title(' '.join(file_name.split('_')[0:3]), fontsize=18)
ax.tick_params(axis='both', which='major', labelsize=14)
fig.tight_layout()

out_path = f'{target_file[0:-4]}_Zoomed.png'
plt.savefig(out_path)

plt.show()
fig.clf()
plt.close(fig)
