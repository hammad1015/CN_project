import socket as sc
import argparse
import threading
import time
import utils
import random
print(50*'***', '\n')


interval= 2
ports   = [8000 + x for x in range(5)]
N       = len(ports)
file    = open('test.txt', 'rb')
size    = file.seek(0, 2)

host_ip = sc.gethostname()
PKT_SIZE = 1



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


def report():

    s = '\n'
    for E, i in indices.items():

        status = 'alive'    if threads[i].is_alive() else 'dead'
        action = 'shutdown' if threads[i].is_alive() else 'Start'

        s += f'Server {i}: Port: {ports[i]} Status: {status}, To {action} Server {i} Enter: {E} \n'

    utils.clear_console()
    print(s, end= '\n\n>>')


def listen(socket, port):

    global host_ip

    socket.bind((host_ip, port))
    socket.listen()

    while True:
        
        client, address = socket.accept()
        
        i, n = tuple(client.recv(50))

        thread = threading.Thread(target= send, args= [client, i, n], daemon= True).start()





def send(client, i, n):


    start  = (size//n) * i
    finish = (size//n) * (i+1)

    for pointer in range(start, finish, PKT_SIZE):

        with threading.Lock(): 
            file.seek(pointer)
            data = file.read(PKT_SIZE)
        
        print(data)
        
        pointer += PKT_SIZE
        if not data: break
        time.sleep(1)
        client.send(data)
        #print(data)







if __name__ == '__main__':


    #setup()


    threads = [
        threading.Thread(target= listen, args= [sc.socket(), port], daemon= True)
        for port in ports
    ]

    indices = {
        f'E{i+1}': i
        for i in range(N)
    }

    for thread in threads: thread.start()

    while True:

        report()
        time.sleep(interval)