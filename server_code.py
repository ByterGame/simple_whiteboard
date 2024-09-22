import socket
import threading

serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
serv_sock.bind(('', 12345))
serv_sock.listen(10)


client_sock, client_addr = serv_sock.accept()
client_connect = True


def Wait_massage():
    global client_connect
    while client_connect:
        data = client_sock.recv(1024)
        if data:
            if data.decode() == "close_socket":
                client_sock.close()
                client_connect = False
                break
            print(data.decode())


t2 = threading.Thread(target=Wait_massage)
t2.start()

while client_connect:
    with open('server_massage', 'r') as file_read:
        lines = file_read.readlines()
        for line in lines:
            if line != '':
                if line == "close_socket":
                    client_sock.sendall(line.encode())
                    client_connect = False
                    t2.join()
                    Wait_massage()
                    break
                else:
                    client_sock.sendall(line.encode())
