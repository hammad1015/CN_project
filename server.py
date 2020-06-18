import socket as sc
import argparse
import threading
import time
import utils
print(50*'***', '\n')

def setup():

    global interval
    global n
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
        n           = args.n
        file        = open(args.f, 'r')
        ports       = args.p

        if n != len(ports): raise Exception('Error: length of -p should equal -n')

    except Exception as e: print(e); quit() 


def init_sockets():

    global host_ip
    global sockets

    host_ip = sc.gethostname()
    
    sockets = []
    for port in ports:

        socket = sc.socket()
        socket.bind((host_ip, port))
        socket.listen()
        sockets.append(socket)


def init_threads():

    global threads

    threads = []
    for socket in sockets:
        thread = threading.Thread(target= connect, args= [socket], daemon= True)

        thread_map[socket] = thread


    global thread_map

    thread_map = {
        socket: threading.Thread(target= connect, args= [socket], daemon= True)
        for socket in sockets
    }
    #thread = 
    #thread.daemon = True
    #threads.append(thread)

def connect(socket):

    global threads

    client, address = socket.accept()
    #print(4*'\t', 'connected')

    thread = threading.Thread(target= connect, args= [socket])
    thread.daemon = True
    threads.append(thread)

    thread = threading.Thread(target= send, args= [client])
    thread.daemon = True
    threads.append(thread)
    client_map[client] = thread




def send(client, address):

    data = file.read(pkt_size).encode('utf-8')
    #print(4*'\t', 'sending')
    #global data

    while True and data: 
        #d = data.pop().encode('utf-8')
        data = get_data() #file.read(pkt_size).encode('utf-8')
        print(data)
        client.send(data)


def report():

    while True:
        time.sleep(2)
        s = ''
        for i, p in enumerate(ports):

            #i += 1
            s += f'Server {i}: Port: {p} Status: <dead/alive>, To Shutdown Server {i} Enter: E{i}\n'

        utils.clear_console()
        print(s)




if __name__ == '__main__':


    #setup()
    interval= 0.2
    ports   = [10000, 10010, 10020, 10030]
    n       = len(ports)
    file    = open('test.txt', 'r')
    clients = []
    pkt_size = 8
    data = '0 1 2 3 4 5 6 7 8 9'.split()

    def foo():
        while True:
            print(input())

    init_sockets()                                                      # initialized and bound sockets
    init_threads()                                                      # initialized threads listiening for connections
    threading.Thread(target= report, daemon= True).start()              # started thread for reporting metrics
    threading.Thread(target= foo, daemon= True).start()

    while True:
        if threads: threads.pop(0).start()













    

    close_sockets()