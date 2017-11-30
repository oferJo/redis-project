import json
import threading
import socket

my_ip = '127.0.0.1'
listening_ip = '0.0.0.0'
server_port = 3030


class TCPServer(object):
    def __init__(self, my_ip, listening_ip, server_port):
        self.my_ip = my_ip
        self.listening_ip = listening_ip
        self.server_port = server_port
        self.server_address = (self.listening_ip, self.server_port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        self.server.bind(self.server_address)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.listen(5)

    def accept_single_connection(self):
        client_socket, client_address = self.server.accept()
        self.handle_client(client_socket, client_address)

    def handle_client(self, client_socket, client_address):
        # TODO implement after commands class is done
        command = self.receive_json_commands(client_socket)

    def receive_json_commands(self, client):
        json_command = client.recv(4096)
        command = json.loads(json_command)
        return command
