import time
import utils
import server
import select
import argparse
import threading
import socket as sc


interval    = server.interval
file        = open('recieved.mp4', 'wb')
address     = sc.gethostname()
ports       = server.ports

lock = threading.Lock()    

PKT_SIZE = 2**11
n       = len(ports)
PING = (1).to_bytes(8, 'big')


def setup():

    global interval
    global file
    global addresses
    global ports
    global resume

    try: 
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', required= True, type= int, help= 'Time interval between status reporting (seconds)')
        parser.add_argument('-o', required= True, type= str, help= 'Output address')
        parser.add_argument('-a', required= True, type= str, help= 'Server IP adress')
        parser.add_argument('-p', required= True, type= int, help= 'Server port numbers', nargs= '+')

        parser.add_argument('-r', help= 'Resume existing progress', action= 'store_true')

        args = parser.parse_args()

        
        interval    = args.i
        file        = open(args.o, 'w')
        address     = args.a
        ports       = args.p
        resume      = args.r

    except Exception as e: print(e); quit() 

def init_connections():

    global sockets
    global fileSize
    global ranges
    global progress
    global speed
    global total

    main = sc.socket()
    main.connect((address, 9999))
    fileSize = int.from_bytes(main.recv(8), 'big')
    main.close()

    ranges = [(0, fileSize)]
    sockets = []
    for port in ports:

        try:
            socket = sc.socket()
            socket.connect((address, port))
            socket.setblocking(0)
            sockets.append(socket)

        except Exception: pass
    
    progress = {
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
        s = '\n'
        for i, socket in enumerate(progress):

            down = progress[socket]
            full = total[socket]
            sped = speed[socket]

            s += f'Server {i}: {down}/{full},\t downloaad speed {sped:.2f} \n'
        
        s += f'Total: {sum(progress.values())}/{fileSize}'
        utils.clear_console()
        print(s)
        time.sleep(1)

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

        time.sleep(0.1)
        msg = True
        while msg:

            t = time.perf_counter()
            time.sleep(0.005)
            msg   = socket.recv(PKT_SIZE)
            data += msg

            progress[socket] += len(msg)
            speed[socket] = t
        
        # only executed when pipeline breaks
        sockets.remove(socket)
        ranges.append(
            (start + len(data), start + chunk)
        )
        
    except BlockingIOError: pass
    except Exception as e: print(type(e))
        
    with lock:

        file.seek(start)
        file.write(data)
        file.flush()








if __name__ == '__main__':

    #setup()
    init_connections()

    threading.Thread(target= report, daemon= True).start()

    while ranges:

        set_pointers(*ranges.pop(0))

        threads = [
            threading.Thread(target= recieve, args= [socket, start])
            for socket, start in zip(sockets, starts)
        ]

        for thread in threads: thread.start()
        for thread in threads: thread.join()



    for socket in sockets: socket.close()
    file.flush()
    file.close()
