import socket as sc
import argparse
import threading
import multiprocessing
import time
import utils




interval    = 3
ports       = [8000 + x for x in range(5)]
N           = len(ports)
file        = open('test.mp4', 'rb')
lock = threading.Lock()



def setup():

    global interval
    global N
    global file
    global ports
    global clients

    try: 
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', required= True, type= int, help= 'Time interval between status reporting (seconds)')
        parser.add_argument('-n', required= True, type= int, help= 'Total number of servers')
        parser.add_argument('-f', required= True, type= str, help= 'File address')
        parser.add_argument('-p', required= True, type= str, help= 'List of port numbers (n port numbers)',nargs='+')

        args = parser.parse_args()

        interval    = args.i
        N           = args.n
        file        = open(args.f, 'rb')
        ports       = args.p

        if n != len(ports): raise Exception('Error: length of -p should equal -n')

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

    for socket, port in zip(sockets, ports):
        socket.bind((host_ip, port))
        socket.listen()

    processes = [
        multiprocessing.Process(target= listen, args= [socket])
        for socket in sockets
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
                #sockets[i].close()

            else:
                sockets[i] = sc.socket()
                pass



def listen(socket):

    try:
        while True:
        
            client, address = socket.accept()

            threading.Thread(target= send, args= [client], daemon= True).start()

    except Exception as e: print(e)

def send(client):
    
    while True:

        start = int.from_bytes(client.recv(8), 'big')
        chunk = int.from_bytes(client.recv(8), 'big')

        with lock:
            file.seek(start)
            data = file.read(chunk)

        if not (client.send(data)): break








if __name__ == '__main__':

    #setup()
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
            quit()