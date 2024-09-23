import socket
import threading

serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
serv_sock.bind(('', 12345))
serv_sock.listen(10)


client_sock, client_addr = serv_sock.accept()
print('connect')
client_connect = True


def clean_file(file_name):
    with open(file_name, 'w') as cf:
        pass


def Wait_massage():
    global client_connect
    while client_connect:
        data = client_sock.recv(1024)
        if data:
            if data.decode() == "close_socket":
                client_sock.close()
                client_connect = False
                clean_file("import_massage")
                break
            else:
                with open('import_massage', 'a') as file_write:
                    file_write.write(data.decode() + '\n')


t2 = threading.Thread(target=Wait_massage)
t2.start()

while client_connect:
    with open('export_massage', 'r+') as file:
        line = file.readline()
        while line:
            if line == "close_socket":
                client_sock.sendall(line.encode())
                client_connect = False
                clean_file("export_massage")
                file.truncate(0)
                t2.join()
                Wait_massage()
                break
            else:
                client_sock.sendall(line.encode())
                line = file.readline()
        file.truncate(0)
