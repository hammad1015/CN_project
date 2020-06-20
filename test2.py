import socket as sc
import time

host_ip = sc.gethostname()
ports   = [8000 + x for x in range(5)]

file = open('test.txt', 'rb')

def listen(socket, port):

    global host_ip

    socket.bind((host_ip, port))
    socket.listen()

    while True:
        
        client, address = socket.accept()

        threading.Thread(target= send, args= [client], daemon= True).start()


threads = [
    threading.Thread(target= listen, args= [sc.socket, port], daemon= True)
    for port in ports
]



while data := file.read(1):

    sc.socket.send(client, data)
    print('sent')
    time.sleep(1)


client.close()
socket.close()