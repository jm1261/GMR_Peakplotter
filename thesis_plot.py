import os
import numpy as np
import matplotlib.pyplot as plt

refractive_index = {
    'DI' : 1.3329,
    '1mM_NaCl' : 1.3329,
    '1M_NaCl' : 1.3437,
    '2M_NaCl' : 1.3536,
    '4M_NaCl' : 1.3693,
    '1mM_Salt' : 1.3329,
    '1M_Salt' : 1.3437,
    '2M_Salt' : 1.3536,
    '4M_Salt' : 1.3693,
    'Crystal_Salt' : 1.54,
    '1mM_Glucose' : 1.3329,
    '1M_Glucose' : 1.3590,
    '2M_Glucose' : 1.3804,
    '4M_Glucose' : 1.3983,
    'Crystal_Glucose' : 1.5,
    '1mM_LiCl' : 1.3328,
    '1M_LiCl' : 1.3413,
    '2M_LiCl' : 1.3510,
    '4M_LiCl' : 1.3624,
    '1mM_KCl' : 1.3329,
    '1M_KCl' : 1.3430,
    '2M_KCl' : 1.3515,
    '4M_KCl' : 1.3675,
}

root = os.getcwd()

conc = '1M'
solute = 'NaCl'
temp1 = '50degrees'
temp2 = 'Heat_150319'
temp3 = ''

title = '1M NaCl'
out_name = '1M_NaCl.png'

solute_path1 = os.path.join(root, 'Solute_Concentrations_mk6')
#solute_path2 = os.path.join(root, 'Solute_Concentrations_mk1')
solute_path3 = os.path.join(root, 'Solute_Concentrations_mk2')

file_path1 = os.path.join(solute_path1, 'Results', f'{conc}_{solute}_{temp1}_Peaks.csv')
#file_path2 = os.path.join(solute_path2, 'Results', f'{conc}_{solute}_{temp2}_Peaks.csv')
file_path3 = os.path.join(solute_path3, 'Results', f'{conc}_{solute}_Peaks.csv')

time1, peak1, peak_shift1 = np.genfromtxt(file_path1, delimiter=',', unpack=True)
#time2, peak2, peak_shift2 = np.genfromtxt(file_path2, delimiter=',', unpack=True)
time3, peak3, peak_shift3 = np.genfromtxt(file_path3, delimiter=',', unpack=True)

time1 /= 60
#time2 /= 60
time3 /= 60

sensitivity = 133
## 131.49669 +/- 7 ##
yint = 156
## 156.03389 ##

fig, ax = plt.subplots(1, 1, figsize=[10,7])
ax.plot(time1, peak_shift1-1.4, 'r.', markersize=4, label=f'{conc} {solute} {temp1}')
#ax.plot(time2, peak_shift2+1.3, 'b.', markersize=4, label=f'{conc} {solute}')
ax.plot(time3, peak_shift3+0.5, 'g.', markersize=4, label=f'{conc} {solute} {temp3}')

ax.set_ylim(20, 27)
#ax.set_xlim(-5, 200)

ax.grid(True)
ax.legend(frameon=True, loc=0, ncol=1, prop={'size':14})
ax.set_xlabel('Time [min]', fontsize=14)
ax.set_ylabel('Peak Shift [nm]', fontsize=14)
ax.set_title(title, fontsize=18)
ax.tick_params(axis='both', which='major', labelsize=14)

ax.axhline(y=((sensitivity*refractive_index['DI'])-yint),
           linewidth=2,
           color='C1',
           linestyle=':')
ax.text(x=-2,
        y=((sensitivity*refractive_index[f'1mM_{solute}'])-yint),
        s=f'DI',
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.5),
        horizontalalignment='center',
        verticalalignment='center',
        fontsize=12)

ax.axhline(y=((sensitivity*refractive_index[f'1M_{solute}'])-yint),
           linewidth=2,
           color='C2',
           linestyle=':')
ax.text(x=-2,
        y=((sensitivity*refractive_index[f'1M_{solute}'])-yint),
        s=f'1M_{solute}',
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.5),
        horizontalalignment='center',
        verticalalignment='center',
        fontsize=12)

ax.axhline(y=((sensitivity*refractive_index[f'2M_{solute}'])-yint),
           linewidth=2,
           color='C3',
           linestyle=':')
ax.text(x=-2,
        y=((sensitivity*refractive_index[f'2M_{solute}'])-yint),
        s=f'2M_{solute}',
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.5),
        horizontalalignment='center',
        verticalalignment='center',
        fontsize=12)

ax.axhline(y=((sensitivity*refractive_index[f'4M_{solute}'])-yint),
           linewidth=2,
           color='C4',
           linestyle=':')
ax.text(x=-2,
        y=((sensitivity*refractive_index[f'4M_{solute}'])-yint),
        s=f'4M_{solute}',
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.5),
        horizontalalignment='center',
        verticalalignment='center',
        fontsize=12)

# ax.axhline(y=((sensitivity*refractive_index[f'Crystal_{solute}'])-yint),
#            linewidth=2,
#            color='C5',
#            linestyle=':')
# ax.text(x=-2,
#         y=((sensitivity*refractive_index[f'Crystal_{solute}'])-yint),
#         s=f'Crystal_{solute}',
#         bbox=dict(facecolor='white', edgecolor='none', alpha=0.5),
#         horizontalalignment='center',
#         verticalalignment='center',
#         fontsize=12)

fig.tight_layout()
out_path = os.path.join(root, 'Thesis_Figures', out_name)
plt.savefig(out_path)
plt.show()
fig.clf()
plt.close(fig)
