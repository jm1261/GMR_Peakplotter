import os
import time
import GMR.InputOutput as io
import GMR.DataPreparation as dprep
import GMR.DataProcessing as dproc
import GMR.UserInput as ui

sensor = 'Nanohole_Array' ## Set this to the photonic crystal used ##

root = io.config_dir_path()

for date_dir in os.listdir(root):
    selected_date = os.path.join(root, date_dir)

    for exp_dir in os.listdir(selected_date):
        solute_dir = os.path.join(selected_date, exp_dir)

        for files in os.listdir(solute_dir):
            file = os.path.join(solute_dir, files)
            x1, y1, x2, y2 = ui.ROI(file)
            wavelength, intensity, file_name = ui.trim_spec(file=file,
                                                            start=round(x1),
                                                            end=round(x2),
                                                            step=0.0001)
            print(wavelength, intensity)
