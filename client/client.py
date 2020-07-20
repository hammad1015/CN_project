import os
import time
import utils
import argparse
import threading
import socket as sc


interval    = 1
fileName    = 'recieved'
fileType    =  'mp4'
#file        = open(f'{fileName}.{fileType}', 'wb')
address     = sc.gethostname()
ports       = [8000 + x for x in range(5)]
resume      = False 

lock = threading.Lock()    

PKT_SIZE = 2**11


'''python client.py -i 0.1 -o recieved.txt -a 192.168.10.9 -p 8000 8001 8002 8003 8004'''

def setup():

    global interval
    global file
    global addresses
    global ports
    global resume

    try: 
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', required= True, type= float, help= 'Time interval between status reporting (seconds)')
        parser.add_argument('-o', required= True, type= str,   help= 'Output address')
        parser.add_argument('-a', required= True, type= str,   help= 'Server IP adress')
        parser.add_argument('-p', required= True, type= int,   help= 'Server port numbers', nargs= '+')

        parser.add_argument('-r', help= 'Resume existing progress', action= 'store_true')

        args = parser.parse_args()

        
        interval    = args.i
        address     = args.a
        ports       = args.p
        resume      = args.r
        
        fileName,   \
        fileType    = args.o.split('.')

        if resume:
            with open(f'{fileName}.{fileType}', 'rb') as f: data = f.read()
            
            file = open(f'{fileName}.{fileType}', 'wb')
            file.write(data)
            del data

        else:
            file = open(f'{fileName}.{fileType}', 'wb')

    except Exception as e: print(e); quit() 

def init_connections():

    global sockets
    global fileSize
    global ranges
    global down
    global speed
    global total
    global file
    global resume

    main = sc.socket()
    main.connect((address, 9999))
    fileSize = int.from_bytes(main.recv(8), 'big')
    main.close()

    ranges = []
    sockets = []

    if resume:
        
        try:
            with open(f'{fileName}.ptr', 'rb') as f:
            
                while True:

                    r0 = int.from_bytes(f.read(8), 'big')
                    r1 = int.from_bytes(f.read(8), 'big')

                    if not r0: break

                    ranges.append([r0, r1])

        except FileNotFoundError: resume = False

    if not resume:
        ranges.append([0, fileSize])
    
    
    for port in ports:

        try:
            socket = sc.socket()
            socket.connect((address, port))
            socket.setblocking(0)
            sockets.append(socket)

        except Exception: pass
    

    down = {
        socket: 0
        for socket in sockets
    }

    speed = {
        socket: 0
        for socket in sockets
    }

    total = {
        socket: 0
        for socket in sockets
    }

def report():

    while True:
        to_print = '\n'
        for i, socket in enumerate(down):

            d = down[socket]
            t = total[socket]
            s = speed[socket]

            to_print += f'Server {i}: {d:8d} / {t:8d},\t downloaad speed: {s:.2f} kb/s\n'
        
        s = sum(speed.values())
        d = sum(down.values())
        t = sum(total.values())

        to_print += f'\nTotal: {d} / {t}, Download speed: {s:.2f} kb/s'
        
        utils.clear_console()
        print(to_print)
        time.sleep(interval)

def set_pointers(a, b):

    global chunk
    global starts

    n = len(sockets)

    chunk  = (b - a) // n + 1
    starts = [
        a + i*chunk
        for i in range(n)
    ]

    for socket in sockets: total[socket] += chunk

def recieve(socket, start):

    data = bytes()

    try:

        socket.send(start.to_bytes(8, 'big'))
        socket.send(chunk.to_bytes(8, 'big'))

    except Exception:
        
        sockets.remove(socket)
        socket.close()
        ranges.append(
            [start, start + chunk]
        )
        return


    try:
        time.sleep(0.1)
        msg = True
        while msg:

            t = time.perf_counter()
            time.sleep(0.005)
            msg   = socket.recv(PKT_SIZE)
            data += msg

            down[socket] += len(msg)
            speed[socket] = len(data) / t / 1024
        
        # only executed when pipeline breaks
        sockets.remove(socket)
        socket.close()
        speed[socket] = 0
        total[socket] = down[socket]
        ranges.append(
            [start + len(data), start + chunk]
        )
        
    except BlockingIOError: pass
        
    with lock:

        file.seek(start)
        file.write(data)
        file.flush()








if __name__ == '__main__':

    setup()
    init_connections()

    threading.Thread(target= report, daemon= True).start()

    while ranges and sockets:

        set_pointers(*ranges.pop(0))

        threads = [
            threading.Thread(target= recieve, args= [socket, start])
            for socket, start in zip(sockets, starts)
        ]

        for thread in threads: thread.start()
        for thread in threads: thread.join()


    if not sockets:

        pointers = [
            pointer.to_bytes(8, 'big')
            for pair    in ranges
            for pointer in pair
        ]

        with open(f'{fileName}.ptr', 'wb') as f: 
            for p in pointers: f.write(p)

    else:
        try: os.remove(f'{fileName}.ptr')
        except Exception: pass

    for socket in sockets: socket.close()
    file.close()
