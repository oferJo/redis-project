import socket
import threading
import json
import sys


# Constants
my_ip = '127.0.0.1'
listening_ip = '0.0.0.0'
server_port = 3030
server_addr = (listening_ip, server_port)

OK = 'OK'
GOODBYE = 'GOODBYE'
ALL = '*'
NAME_TAKEN = 'Name is already taken!'
ERROR = 'ERROR'
UNKNOWN_COMMAND = 'Unknown command'

Clients = {}


def log(text):
    print >>sys.stderr, text


# Handling Clients
def receive_name(client):
    return client.recv(4096)


def receive_commands(client):
    commands_json_encoded = client.recv(4096)
    return json.loads(commands_json_encoded)


def handle_client_connection(client_socket, client_address):
    name = receive_name(client_socket)

    if name in Clients:
        client_socket.sendall(NAME_TAKEN)
        log('Client {}:{} chose taken name: {}'.format(client_address[0], client_address[1], name))
        return
    client_socket.sendall(OK)

    # mark name as taken
    Clients[name] = {}
    log('Client {}:{} has name: {}'.format(client_address[0], client_address[1], name))

    commands = receive_commands(client_socket)
    Clients[name]['commands'] = commands
    log('Client {} has commands: {}'.format(name, ','.join(commands)))

    Clients[name]['next_command'] = None

    while Clients[name]['next_command'] != GOODBYE:
        next_command = Clients[name]['next_command']

        if next_command is None:
            continue

        if next_command != GOODBYE:
            log("Sending command {} to {}".format(next_command, name))
            client_socket.sendall(Clients[name]['next_command'])

            command_json_encoded = client_socket.recv(4096)
            log("Receive {} from {}".format(command_json_encoded, name))
            data = json.loads(command_json_encoded)

            Clients[name]['next_command'] = None

    log('Sending Goodbye to {}'.format(name))
    client_socket.sendall(GOODBYE)
    client_socket.close()
    Clients.pop(name)


# The Server
keep_accepting_connections = True


def accept_connections(server):
    while keep_accepting_connections:
        client_sock, client_address = server.accept()
        log('Accepted connection from {}:{}'.format(*client_address))

        if client_address[0] == my_ip:
            log("Connection from {}. Keep accepting connections?: {}".format(my_ip, keep_accepting_connections))
            if not keep_accepting_connections:
                break

        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock, client_address)
        )
        client_handler.start()
    server.close()


def close_accepting_thread(accepting_thread):
    # change global keep_accepting_connections variable
    global keep_accepting_connections
    keep_accepting_connections = False

    if accepting_thread.is_alive:
        # create a local connection to the listening socket, to trigger accept function
        s = socket.socket()
        s.connect((my_ip, server_port))
        s.close()


def main():
    # create a tcp socket (SOCK_STREAM) over ip protocol (AF_INET)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # assign to server port to listen for incoming connections on that port
    server.bind((listening_ip, server_port))

    # avoid TIME_WAIT after closing
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # backlog connections
    server.listen(5)
    log('Server is on and listening on {}:{}'.format(*server_addr))

    # start accepting connections
    accepting_thread = threading.Thread(
            target=accept_connections,
            args=(server,)
        )
    accepting_thread.start()

    while True:
        print "Available clients:"
        for i, client in enumerate(Clients.keys()):
            print '{}. {}'.format(i, client)

        client_num = raw_input("Select client number, 'x' for exit, anything else to refresh")

        if client_num.lower() == 'x':
            break

        if not client_num.isdigit():
            continue

        client_num = int(client_num)
        if client_num < 0 or client_num >= len(Clients.keys()):
            continue

        client_name = Clients.keys()[client_num]
        client = Clients[client_name]

        print "Available command for {}:".format(client_name)
        for i, command in enumerate(client['commands']):
            print '{}. {}'.format(i, command)
        command_num = raw_input("Select command number, 'x' for exit, 'g' for goodbye, anything else to refresh")

        if command_num.lower() == 'x':
            break

        if command_num.lower() == 'g':
            command = GOODBYE
            log('assign command {} to {}'.format(command, client_name))
            client['next_command'] = command
            continue

        if not command_num.isdigit():
            continue

        command_num = int(command_num)
        if command_num < 0 or command_num >= len(client['commands']):
            continue

        command = client['commands'][command_num]
        log('assign command {} to {}'.format(command, client_name))
        client['next_command'] = command

    log('Stop listening for new connections')
    close_accepting_thread(accepting_thread)

    for client_name in Clients.keys():
        Clients[client_name]['next_command'] = GOODBYE

    log('Waiting for client to disconnect')
    while Clients:
        pass

    # waiting for accepting thread to close
    accepting_thread.join()

    log('All clients disconnected. Goodbye!')


if __name__ == '__main__':
    main()
