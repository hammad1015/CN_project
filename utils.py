import sys
import os
import platform
import random

server = 'abcd'
client = 'wxyz'

clear_map = {
    'linux'     : 'clear',
    'darwin'    : 'clear',
    'Windows'   : 'cls'
}

platform = sys.platform

def clear_console():
    
    if platform in clear_map:
        os.system(clear_map[platform])
