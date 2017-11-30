import socket
import json


# Constants
server_ip = '127.0.0.1'
server_port = 3031
server_addr = (server_ip, server_port)

# The Client
def log(text):
    print text

def user_input():
    inpt = raw_input("What would you like to do? \nInsert (set / get / showAll / exit)\n")
    data = ""
    if inpt == 'set':
        key = raw_input('Enter key:')
        value = raw_input('Enter value:')
        record = {key: value}
        data = ('set', record)
    if inpt == 'get':
        key = raw_input('Enter Key:')
        data = ('get', key)
    if inpt == 'showAll':
        key = raw_input('Enter Key:')
        data = ('showall', key)
    if inpt == 'exit':
        data = False
    return data


def process_server_feedback(reply):
    if reply(0) == 'message':
        log(reply[1])
    if reply(0) == 'get' or 'showall':
        log(reply[1])


def main():
    # create a tcp socket (SOCK_STREAM) over ip protocol (AF_INET)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to the server
    log('Trying connecting to {}:{}'.format(*server_addr))
    client.connect(server_addr)
    log('Connected!')

    # start communicating with the server
    data = user_input()
    while data:
        print data
        json_encoded = json.dumps(data)
        print json_encoded
        # log('Send %s request' % inpt)
        client.sendall(json_encoded)
        log("Waiting for reply from server")
        reply = client.recv(4096)
        print reply
        reply = json.loads(reply)
        process_server_feedback(reply)
        data = user_input()
    log("Close connection")
    client.close()
    log("Connection closed")


if __name__ == '__main__':
    main()
