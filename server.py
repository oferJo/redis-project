import json
import socket
import time


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
        log("Waiting for command from client")
        command = self.receive_json_commands(client_socket)
        log("Received raw command: {}".format(command))
        while command[0] != "exit":
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
        if json_command != "exit":
            command = json.loads(json_command)
            return command
        else:
            return json_command

    def send_json_reply(self, client, reply):
        json_reply = json.dumps(reply)
        client.sendall(json_reply)


class TTL(object):
    def __init__(self):
        self.timestamp = []
        self.MaxTime = 2

    def add_entry(self, key):
        self.timestamp.append((time.time(), key))

    def check_entries(self):
        dif = time.time() - self.timestemp[-1][0]
        while dif <= self.MaxTime:
            del database[self.timestemp[-1][1]]
            self.timestemp = self.timestep[:-1]
            dif = time.time() - self.timestemp[-1][0]


def log(text):
    print(text)


def execute_command(command):
    if command[0] in COMMANDS:
        reply = COMMANDS[command[0]](command[1])
    else:
        reply = ("message", "Unsupported command")

    return reply


def set_data(entry):
    database.update(entry)
    reply = ("message", "Your data has been stored at key: {}".format(entry.keys()[0]))
    return reply
COMMANDS["set"] = set_data


def get_data(key):
    if key in database:
        reply = ("data", database[key])
    else:
        reply = ("message", 'No such key')
    return reply
COMMANDS["get"] = get_data


def close_connection(key):
    reply = ("close", "Your connection has been closed")
    return reply
COMMANDS["exit"] = close_connection


def showall_data(partial_key):
    values = []
    for key, value in database.items():
        if partial_key in key:
            values.append(value)

    reply = ("data", values)
    return reply
COMMANDS["showall"] = showall_data


server = TCPServer('127.0.0.1', '0.0.0.0', 3031)
