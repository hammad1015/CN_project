import os
import platform

platform = platform.system()

clear_map = {
    'Linux'     : 'clear',
    'Darwin'    : 'clear',
    'Windows'   : 'cls'
}


def clear_console():
    
    if platform in clear_map:
        os.system(clear_map[platform])
