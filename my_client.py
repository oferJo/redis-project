import socket
import json


# Constants
my_name = 'Ofer'

server_ip = '127.0.0.1'
server_port = 3030
server_addr = (server_ip, server_port)

OK = 'OK'
GOODBYE = 'GOODBYE'
ALL = '*'
ERROR = 'ERROR'
UNKNOWN_COMMAND = 'Unknown command'
COMMANDS = {}

# Commands
def uname():
    import platform
    system, node, release, version, machine, processor = platform.uname()
    return {'system': system,
            'node': node,
            'release': release,
            'version': version,
            'machine': machine,
            'processor': processor}
COMMANDS['OS_NAME'] = uname


def whoami():
    import getpass
    username = getpass.getuser()
    return {'username': username}
COMMANDS['USERS'] = whoami


def whos_logged_in():
    import subprocess
    users_raw = subprocess.check_output("who")
    users = users_raw.split('\n')[:-1]
    return users


def whats_running():
    import subprocess
    processes_raw = subprocess.check_output("ps")
    processes = processes_raw.split('\n')[1:-1]
    for idx, process in enumerate(processes):
        temp = process.split()
        temp[1] = temp[3]
        temp = temp[:-2]
        temp = ' '.join(temp)
        processes[idx] = temp

    return processes


# The Client
def log(text):
    print text


def main():
    # create a tcp socket (SOCK_STREAM) over ip protocol (AF_INET)
    # A pair (host, port) is used for the AF_INET address family, where host is a string representing either a hostname
    # in Internet domain notation like 'daring.cwi.nl' or an IPv4 address, and port is an integer.
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to sever
    # the asterisk * before a tuple, enters all it's elements as single entries
    # similarly, ** before a dictionary enters the 'key:value's as single entries
    log("Trying to connect to {}:{}".format(*server_addr))
    client.connect(server_addr)
    log("Connected")

    # send my name
    data = json.dumps({'name': my_name})
    log("Sending {} to server".format(data))
    client.sendall(data)

    # wait for response
    # recv(bufsize) buffer size should be a power of 2, the max amount of data received
    response = client.recv(4096)
    if response != OK:
        log("Received error: {}".format(response))
        return
    log("Received {}".format(OK))

    # send my commands
    json_encoded = json.dumps(COMMANDS.keys())
    log("Sending {} to server".format(json_encoded))
    client.sendall(json_encoded)

    # start receiving commands from server
    log("Waiting for commands from server")
    command = client.recv(4096)
    while command != GOODBYE:
        log("Got command: {}".format(command))

        if command in COMMANDS:
            data = {command: COMMANDS[command]()}
        elif command == ALL:
            data = {command_my: COMMANDS[command]() for command_my in COMMANDS}
        else:
            data = {ERROR: UNKNOWN_COMMAND}

        json_encoded = json.dumps(data)
        log('Send response: {}'.format(json_encoded))
        client.sendall(json_encoded)

        log("Waiting for commands from server")
        command = client.recv(4096)

    log("Received goodbye from server, close connection")
    client.close()

if __name__ == '__main__':
    main()
