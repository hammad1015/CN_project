import socket as sc
import select

host_ip = sc.gethostname()
port = 8000

socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
socket.connect((host_ip, port))

inputs = [socket]
outputs = []

msg = True
while msg:

    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    
    for socket in readable:
        msg = socket.recv(100)
        print(msg)

    for socket in exceptional:
        print('exceptional')