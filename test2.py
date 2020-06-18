import socket as sc
import time

host_ip = sc.gethostname()
port = 8000
msg = b'hello'

socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
socket.bind((host_ip, port))
socket.listen()
map = {}

client, address = socket.accept() 
map[client] = 'lol'
print('accepted')

for _ in range(5):

    sc.socket.send(client, msg)
    #print(client)
    #print(socket)
    #print('sent')
    print(map)
    time.sleep(1)
    del map[client]

client.close()
socket.close()