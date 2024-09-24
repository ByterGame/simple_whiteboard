import socket
import threading
import sys


class Client:
    def clean_file(self, file_name):
        open(file_name, 'w').close()

    def wait_message(self):
        while self.connect:
            data = self.client_sock.recv(8192)
            if data:
                if data.decode() == "close_socket":
                    self.connect = False
                    self.client_sock.close()
                    self.clean_file("import_message")
                    break
                else:
                    with open('import_message', 'a') as file_write:
                        file_write.write(data.decode() + '\n')

    def __init__(self, server_name):
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((server_name, 55555))
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
                            self.client_sock.sendall(line.encode())
                            line = file.readline()
                    else:
                        break
                file.truncate(0)
        self.clean_file("export_message")
        self.clean_file("import_message")