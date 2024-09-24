import socket
import threading
import sys


class Server:
    def clean_file(self, file_name):
        open(file_name, 'w').close()

    def wait_message(self):
        while self.connect:
            data = self.client_sock.recv(1024)
            if data:
                if data.decode() == "close_socket":
                    self.connect = False
                    self.client_sock.close()
                    self.clean_file("import_message")
                    break
                else:
                    with open('import_message', 'a') as file_write:
                        file_write.write(data.decode() + '\n')

    def __init__(self):
        print(2)
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
        self.serv_sock.bind(('', 55550))
        self.serv_sock.listen(10)
        self.client_sock, client_addr = self.serv_sock.accept()
        print('connect')
        self.connect = True
        threading.Thread(target=self.wait_message, daemon=True).start()
        self.sand_message()

    def sand_message(self):
        while self.connect:
            with open('export_message', 'r+') as file:
                line = file.readline()
                while line:
                    if sys.getsizeof(line.encode()) == 64:
                        if line == "close_socket":
                            self.client_sock.sendall(line.encode())
                            self.connect = False
                            self.clean_file("export_message")
                            self.client_sock.close()
                            break
                        else:
                            self.client_sock.send(line.encode())
                            line = file.readline()
                    else:
                        break
                file.truncate(0)
        self.clean_file("export_message")
        self.clean_file("import_message")