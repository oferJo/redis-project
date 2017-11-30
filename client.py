import socket
import json

# Constants
server_ip = '127.0.0.1'
server_port = 3030
server_addr = (server_ip, server_port)


# The Client
def log(text):
    print text

class Client(object):
    """
    check
    """
    def __init__(self):
        self = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def user_input():
    inpt = input("What would you like to do? \nInsert (Set / Get / ShowAll / Exit)")
    if inpt == 'set':
        key = input('Enter key:')
        value = input('Enter value:')
        record = {key: value}
        data = ('set', record)
    if inpt == 'get':
        key = input('Enter Key:')
        data = ('get', key)
    if inpt == 'showall':
        key = input('Enter Key:')
        data = ('showall', key)
    if inpt == 'exit':
        data = ''
    log('Send %s request' % inpt)
    return data


def process_server_feedback(reply):
    if reply(0) == 'message':
        log(reply[1])
    if reply(0) == 'get' or 'showall':
        log(reply[1])


def send_receive(data):
    json_encoded = json.dumps(data)
    client.sendall(json_encoded)
    log("Waiting for reply from server")
    reply = client.recv(4096)
    reply = json.reads(reply)
    process_server_feedback(reply)


def main():
    # create a tcp socket (SOCK_STREAM) over ip protocol (AF_INET)
    client = Client

    # connect to the server
    log('Trying connecting to {}:{}'.format(*server_addr))
    client.connect(server_addr)
    log('Connected!')

    # start communicating with the server
    data = user_input()
    while data != 'exit':
        send_receive(data)
        data = user_input()
    log("Close connection")
    client.close()
    log("Connection closed")


if __name__ == '__main__':
    main()
