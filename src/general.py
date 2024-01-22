import os
import shutil

def copy(path1, path2, file_1, file_2 = None):
    
    if file_2 is None:
        file_2 = file_1
    
    shutil.copy(os.path.join(path1, file_1), os.path.join(path2, file_2))

    return

