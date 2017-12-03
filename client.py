import socket
import json

class Log(object):
    #def __init__(self):
    def local(self, text):
        print text
    def server_reply(self, reply):
        if reply(0) == 'message':
            print(reply[1])
        if reply(0) == 'get' or 'showall':
            print(reply[1])
    def print_to_file(self):
        print 'request to print to file, currently doing nothing'


class Client(socket.socket):
    """
    Client class, inherit from socket
    """
    def __init__(self):
        # create a tcp socket (SOCK_STREAM) over ip protocol (AF_INET)
        super(Client, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.log = Log

    def connect(self):
        server_ip = '127.0.0.1'
        server_port = 3030
        server_addr = (server_ip, server_port)
        self.log.local('Trying connecting to {}:{}'.format(*server_addr))
        super(Client, self).connect(server_addr)
        self.log.local('Connected')

    def send(self, data):
        self.log.local('Sending data')
        json_encoded = json.dumps(data)
        super(Client, self).sendall(json_encoded)

    def receive(self):
        self.log.local("Waiting for reply from server")
        reply = super(Client, self).recv(4096)
        self.log.server_reply(json.reads(reply))

    def close_connection(self):
        self.log("Close connection")
        super(Client, self).close()
        self.log("Connection closed")

class UserInput(object):
    def __init__(self):
       self.data = ('init','init')

    def get_data(self):
        inpt = input("What would you like to do? \nInsert (set / get / showall / exit)")
        if inpt == 'set':
            key = input('Enter key:')
            value = input('Enter value:')
            record = {key: value}
            self.data = ('set', record)
        if inpt == 'get':
            key = input('Enter Key:')
            self.data = ('get', key)
        if inpt == 'showall':
            key = input('Enter Key:')
            self.data = ('showall', key)
        if inpt == 'exit':
            self.data = 'exit'
        return self.data


def main():
    inp = UserInput()
    client = Client()
    client.connect()
    while inp.get_data() != 'exit':
        client.send(inp.data)
        client.receive())
    client.close_connection()


if __name__ == '__main__':
    main()
