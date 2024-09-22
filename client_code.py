import socket
import threading

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect(('127.0.0.1', 12345))
connect = True


def wait_massage():
    global connect
    while connect:
        data = client_sock.recv(1024)
        if data:
            if data.decode() == "close_socket":
                connect = False
                client_sock.close()
                break
            print(data.decode())


t2 = threading.Thread(target=wait_massage)
t2.start()

while connect:
    with open('client_massage', 'r') as file_read:
        lines = file_read.readlines()
        for line in lines:
            if line != '':
                if line == "close_socket":
                    client_sock.sendall(line.encode())
                    connect = False
                    t2.join()
                    wait_massage()
                    break
                else:
                    client_sock.sendall(line.encode())
