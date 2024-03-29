import os


def ConfigDirPath():
    '''
    Asigns a directory path for all data, allowing for user input without
    altering the script.
    The current working directory (which is where the code is activatd from)
    will then contain all data to be analysed. A folder (directory) is created
    named 'Put_Data_Here'.
    The function then waits for the user to place a data folder (from GMR setup)
    in to the new folder, eg...('050319') which contains '1M_Salt',...etc.
    Args:
        The function requires no arguments but will not work unless data is
        placed into the new directory and awaits a user input (pressing enter)
    '''
    root = os.getcwd()
    main_dir = os.path.join(root, 'Put_Data_Here')
    if os.path.isdir(main_dir) is False:
        os.mkdir(main_dir)
    while len(os.listdir(main_dir)) == 0:
        print('Place test data into "Put_Data_Here" folder with this code.')
        print('This is the same folder created on GMR X.')
        print('Once complete please hit enter on your keyboard.')
        print(' ')
        input('Press enter to continue...')
    else:
        print('Data present in "Put_Data_Here", ensure it is correct')
        print('Ensure in the code that the "sensor" parameter is correct')
        print(' ')
        input('Press enter to continue...')
    print(' ')
    print('Data set(s) to be examined:')
    print(os.listdir(main_dir))
    return main_dir


if __name__ == '__main__':

    main_dir = ConfigDirPath()
    data_files = os.listdir(main_dir)

    for dir in data_files:
        img_dir = os.path.join(main_dir, dir)
        print(img_dir)
        print(os.listdir(img_dir))
