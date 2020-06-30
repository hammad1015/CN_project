import time
import utils
import server
import select
import argparse
import threading
import socket as sc


interval    = server.interval
file        = open('recieved.txt', 'wb')
address     = server.host_ip
ports       = server.ports

lock = threading.Lock()    

PKT_SIZE = 2**10 #server.PKT_SIZE
logFile = open('clientLog.txt', 'w')
n       = len(ports)


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

def init():

    global sockets
    global ranges
    global fileSize

    main = sc.socket()
    main.connect((address, 9999))
    fileSize = int.from_bytes(main.recv(5), 'big')
    main.close()

    ranges = [(0, fileSize)]

    sockets = [
        sc.socket()
        for _ in range(n)
    ]

    for socket, port in zip(sockets, ports):
        socket.connect((address, port))

    


def recieve(socket, start):

    socket.send(start.to_bytes(5, 'big'))
    socket.send(chunk.to_bytes(5, 'big'))

    data = bytes()
    while True:

        msg = socket.recv(PKT_SIZE)
        data += msg
        #if not msg: break

    print('recieved: ', len(data))
    with lock:

        file.seek(start)
        file.write(data)








if __name__ == '__main__':

    #setup()
    init()

    while ranges:

        i, j = ranges.pop(0)

        chunk = (j - i) // len(sockets) + 1

        threads = [
            threading.Thread(target= recieve, args= [s, i * chunk])
            for i, s in enumerate(sockets)
        ]
        for thread in threads: thread.start()
        for thread in threads: thread.join()


    file.flush()
    file.close()
