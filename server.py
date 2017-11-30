import json
import socket


database = {}
COMMANDS = {}
# TODO: check if socket is universal or tcp specific

class TCPServer(object):
    def __init__(self, my_ip, listening_ip, server_port):
        self.my_ip = my_ip
        self.listening_ip = listening_ip
        self.server_port = server_port
        self.server_address = (self.listening_ip, self.server_port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()
        self.accept_single_connection()

    def connect(self):
        self.server.bind((self.listening_ip, self.server_port))
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.listen(5)

    def accept_single_connection(self):
        client_socket, client_address = self.server.accept()
        self.handle_client(client_socket, client_address)
        self.server.close()

    def handle_client(self, client_socket, client_address):
        # TODO implement after commands class is done
        command = self.receive_json_commands(client_socket)
        while command[0] != "close":
            log("Received command: {}".format(command[0]))
            reply = execute_command(command)
            self.send_json_reply(client_socket, reply)
            log("Waiting for command from client")
            command = self.receive_json_commands(client_socket)

        log("received close command from client, close connection")
        reply = execute_command(command)
        self.send_json_reply(client_socket, reply)
        client_socket.close()

    def receive_json_commands(self, client):
        json_command = client.recv(4096)
        print json_command
        command = json.loads(json_command)
        return command

    def send_json_reply(self, client, reply):
        json_reply = json.dumps(reply)
        client.sendall(json_reply)


def log(text):
    print(text)


def execute_command(command):
    if command[0] in COMMANDS:
        reply = COMMANDS[command[0]](command[1])
        return reply
    reply = ("message", "Unsupported command")
    return reply


def set_data(entry):
    database.update(entry)
    reply = ("message", "Your data has been stored at key: {}".format(database.keys()))
    return reply
COMMANDS["set"] = set_data


def get_data(key):
    reply = ("data", database[key])
    return reply
COMMANDS["get"] = get_data


def close_connection():
    reply = ("close", "Your connection has been closed")
    return reply
COMMANDS["close"] = close_connection


server = TCPServer('127.0.0.1', '0.0.0.0', 3031)
