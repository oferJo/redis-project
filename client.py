import socket
import json


class Log(object):
    # def __init__(self):
    def local(self, text):
        print text

    def server_reply(self, reply):
        if reply[0] == 'message':
            print(reply[1])
        if reply[0] == "data":
            data_string = reply[1]
            if not isinstance(reply[1], basestring):
                data_string = ", ".join(reply[1])

            print(data_string)

    def print_to_file(self):
        print 'request to print to file, currently doing nothing'


class Client(socket.socket):
    """
    Client class, inherit from socket
    """
    def __init__(self):
        # create a tcp socket (SOCK_STREAM) over ip protocol (AF_INET)
        super(Client, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.log = Log()

    def connect(self):
        server_ip = '127.0.0.1'
        server_port = 3031
        server_addr = (server_ip, server_port)
        self.log.local('Trying connecting to {}:{}'.format(*server_addr))
        super(Client, self).connect((server_ip, server_port))
        super(Client, self).setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.log.local('Connected')

    def send_data(self, data):
        self.log.local('Sending data')
        json_encoded = json.dumps(data)
        super(Client, self).sendall(json_encoded)

    def receive(self):
        self.log.local("Waiting for reply from server")
        reply = super(Client, self).recv(4096)
        self.log.server_reply(json.loads(reply))

    def close_connection(self):
        self.log.local("Close connection")
        super(Client, self).close()
        self.log.local("Connection closed")


class UserInput(object):
    def __init__(self):
       self.data = ('init','init')

    def get_data(self):
        inpt = raw_input("What would you like to do? \nInsert (set / get / showall / exit)\n")
        if inpt == 'set':
            key = raw_input('Enter key:')
            value = raw_input('Enter value:')
            record = {key: value}
            self.data = ('set', record)
        elif inpt == 'get':
            key = raw_input('Enter Key:')
            self.data = ('get', key)
        elif inpt == 'showall':
            key = raw_input('Enter Key:')
            self.data = ('showall', key)
        elif inpt == 'exit':
            self.data = ('exit', -1)
        else:
            self.data = (inpt, -1)

        return self.data


def main():
    inp = UserInput()
    client = Client()
    client.connect()
    while inp.get_data()[0] != 'exit':
        client.send_data(inp.data)
        client.receive()

    client.send_data(inp.data)
    client.receive()
    client.close_connection()


if __name__ == '__main__':
    main()
