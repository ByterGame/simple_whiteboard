import socket
import threading

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect(('127.0.0.1', 12345))
connect = True


def clean_file(file_name):
    with open(file_name, 'w') as cf:
        pass


def Wait_massage():
    global connect
    while connect:
        data = client_sock.recv(1024)
        if data:
            if data.decode() == "close_socket":
                connect = False
                client_sock.close()
                clean_file("import_massage")
                break
            else:
                with open('import_massage', 'a') as file_write:
                    file_write.write(data.decode() + '\n')


t2 = threading.Thread(target=Wait_massage)
t2.start()

while connect:
    with open('export_massage', 'r+') as file:
        line = file.readline()
        while line:
            if line == "close_socket":
                client_sock.sendall(line.encode())
                client_connect = False
                clean_file("export_massage")
                t2.join()
                Wait_massage()
                break
            else:
                client_sock.sendall(line.encode())
                line = file.readline()
        file.truncate(0)
