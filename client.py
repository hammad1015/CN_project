import socket as sc
import argparse
import select
import time

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
        parser.add_argument('-a', required= True, type= str, help= 'Server IP adresses' , nargs= '+')
        parser.add_argument('-p', required= True, type= str, help= 'Server port numbers', nargs= '+')

        parser.add_argument('-r', help= 'Resume existing progress', action= 'store_true')

        args = parser.parse_args()

        
        interval    = args.i
        file        = open(args.o, 'w')
        addresses   = args.n
        ports       = args.p
        resume      = args.r

        if len(a) != len(p): raise Exception('Error: length of -a should equal length of -p')

    except Exception as e: print(e); quit() 

def init_sockets():

    global sockets

    sockets = []
    for IP_port in zip(addresses, ports):
        
        socket = sc.socket()
        socket.connect(IP_port)
        sockets.append(socket)


if __name__ == '__main__':

    #setup()
    ports   = [10000, 10010, 10020, 10030]
    addresses   = [sc.gethostname()]*len(ports)


    init_sockets()
    while True:
        
        readable, writable, exceptional = select.select(sockets, [], sockets)

        for socket in readable:
            
            #time.sleep(0.1)
            msg = socket.recv(2)
            if not msg: continue
            print(msg)

        #if not msg: break

    print('done')
