import socket as sc
import argparse
import select
import time
import server


interval    = server.interval
#file        = open(args.o, 'w')
address     = server.host_ip
ports       = server.ports
#resume      = args.r
    

PKT_SIZE = server.PKT_SIZE



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
        parser.add_argument('-p', required= True, type= str, help= 'Server port numbers', nargs= '+')

        parser.add_argument('-r', help= 'Resume existing progress', action= 'store_true')

        args = parser.parse_args()

        
        interval    = args.i
        file        = open(args.o, 'w')
        address     = args.a
        ports       = args.p
        resume      = args.r

        if len(a) != len(p): raise Exception('Error: length of -a should equal length of -p')

    except Exception as e: print(e); quit() 

    


if __name__ == '__main__':

    #setup()


    n = len(ports)

    sockets = [
        sc.socket()
        for _ in range(n)
    ]


    for i in range(n): 
        
        sockets[i].connect(
            (address, ports[i])
        )
        data = bytes((i, n))
        sockets[i].send(data)


    while True:
        
        readable, writable, exceptional = select.select(sockets, [], sockets)

        #time.sleep(1)

        for socket in readable:
            
            msg = socket.recv(PKT_SIZE)
            print(msg)

