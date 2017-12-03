import json
import socket
import ruamel.yaml as yaml
import warnings
import time
import threading

warnings.simplefilter('ignore', yaml.error.UnsafeLoaderWarning)

COMMANDS = {}

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
    global database

    def __init__(self, configuration_time):
        self.timestamp = []
        self.MaxTime = configuration_time

    def add_entry(self, key):
        # checks and removes previous keys in case of over-writingg a record:
        self.timestamp = [tup for tup in self.timestamp if tup[1] != key]
        # insert the new key at the beginning of the list:
        self.timestamp.insert(0, (time.time(), key))

    def check_entries(self):
        if self.timestamp:
            dif = time.time() - self.timestamp[-1][0]
        else:
            return
        while dif >= self.MaxTime:
            print('Delete')
            delete_record(self.timestamp[-1][1])
            self.timestamp.pop()
            if self.timestamp:
                dif = time.time() - self.timestamp[-1][0]
            else:
                break

    def continuous_ttl_check(self):
        while True:
            self.check_entries()
            time.sleep(1)
            print("check")
            print(self.timestamp)
            print(database)


def delete_record(key):
    del database[key]


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
    ts.add_entry(entry.keys()[0])
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


def start_serv():
    server = TCPServer('127.0.0.1', '0.0.0.0', config_dict["server_port"])


def set_options():
    with open("config.yml", 'r') as config_file:
        config_dict = yaml.load(config_file)

    return config_dict


database = {}
config_dict = set_options()
configuration_time = config_dict["configuration_time"]
ts = TTL(configuration_time)

cont_ttl = threading.Thread(target=ts.continuous_ttl_check)
cont_ttl.setDaemon(True)
cont_ttl.start()

mythd = threading.Thread(target=start_serv)
mythd.start()
