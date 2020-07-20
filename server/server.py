import time
import utils
import argparse
import threading
import multiprocessing
import socket as sc




interval    = 3
ports       = [8000 + x for x in range(5)]
N           = len(ports)
file        = open('test.mp4', 'rb')
lock = threading.Lock()
'''python server.py -i 3 -n 5 -f test.mp4 -p 8000 8001 8002 8003 8004'''


def setup():

    global interval
    global N
    global file
    global ports
    global clients

    try: 
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', required= True, type= float, help= 'Time interval between status reporting (seconds)')
        parser.add_argument('-n', required= True, type= int,   help= 'Total number of servers')
        parser.add_argument('-f', required= True, type= str,   help= 'File address')
        parser.add_argument('-p', required= True, type= int,   help= 'List of port numbers (n port numbers)',nargs='+')

        args = parser.parse_args()

        interval    = args.i
        N           = args.n
        file        = open(args.f, 'rb')
        ports       = args.p

        if N != len(ports): raise Exception('Error: length of -p should equal -n')

    except Exception as e: print(e); quit() 

def init():

    global sockets
    global indices
    global processes
    global fileSize
    global lock
    global host_ip

    fileSize    = file.seek(0, 2)
    lock        = threading.Lock()
    host_ip     = sc.gethostname()

    sockets = [
        sc.socket()
        for _ in range(N)
    ]

    indices = {
        f'E{i}': i
        for i in range(N)
    }

    processes = [
        multiprocessing.Process(target= listen, args= [socket, port, host_ip])
        for socket, port in zip(sockets, ports)
    ]

    for process in processes: process.start()    

def report():

    while True:

        s = '\n'
        for E, i in indices.items():

            status = 'alive'    if processes[i].is_alive() else 'dead ' 
            action = 'shutdown' if processes[i].is_alive() else 'start   '

            s += f'Server {i}: Port: {ports[i]} Status: {status}, To {action} Server {i} Enter: {E} \n'

        utils.clear_console()
        print(s, end= '\n\n>>')
        time.sleep(interval)

def shut():

    while True:

        command = input()

        if command in indices:
            i = indices[command]

            if processes[i].is_alive():
                processes[i].terminate()
                sockets[i].close()

            else:
                sockets[i] = sc.socket()
                processes[i] = multiprocessing.Process(target= listen, args= [sockets[i], ports[i], host_ip])
                processes[i].start()

def listen(socket, port, ip):

    socket.bind((ip, port))
    socket.listen()

    try:
        while True:
        
            client, address = socket.accept()

            threading.Thread(target= send, args= [client], daemon= True).start()

    except Exception as e:

        socket.close()
        print(e)

def send(client):
    
    while True:

        start = int.from_bytes(client.recv(8), 'big')
        chunk = int.from_bytes(client.recv(8), 'big')

        with lock:
            file.seek(start)
            data = file.read(chunk)

        if not (client.send(data)): break



if __name__ == '__main__':

    setup()
    init()

    threading.Thread(target= report, daemon= True).start()
    threading.Thread(target= shut  , daemon= True).start()


    main = sc.socket()
    main.bind((host_ip, 9999))
    main.listen()

    while True:

        try:
            client, _ = main.accept()
            client.send(fileSize.to_bytes(8, 'big'))
            client.close()

        except KeyboardInterrupt: 

            main.close()
            for process in processes: process.terminate()
            for socket  in sockets  : socket.close()
            quit()