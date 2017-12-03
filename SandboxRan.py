import threading
import time


class TTL(object):
    def __init__(self):
        self.timestamp = []
        self.MaxTime = 2

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
            db.delete_record(self.timestamp[-1][1])
            self.timestamp.pop()
            if self.timestamp:
                dif = time.time() - self.timestamp[-1][0]
            else:
                break

    def continuous_ttl_check(self):
        while True:
            self.check_entries()
            time.sleep(0.1)


class DataBase(object):
    def __init__(self):
        self.db = {}

    def add_record(self, record):
        self.db[record[0]] = record[1]

    def delete_record(self, key):
        del self.db[key]


def mythread():
    # insert two records:
    rcrd = ('1', 'A')
    db.add_record(rcrd)
    ts.add_entry(rcrd[0])
    print(db.db)
    print(ts.timestamp)
    time.sleep(2.5)
    print(db.db)
    print(ts.timestamp)
    rcrd = ('2', 'B')
    db.add_record(rcrd)
    ts.add_entry(rcrd[0])
    print(db.db)
    print(ts.timestamp)
    time.sleep(1.5)
    rcrd = ('2', 'C')
    db.add_record(rcrd)
    ts.add_entry(rcrd[0])
    print(db.db)
    print(ts.timestamp)
    time.sleep(1)
    print(db.db)
    print(ts.timestamp)
    time.sleep(1.5)
    print(db.db)
    print(ts.timestamp)


# define objects:
ts = TTL()
db = DataBase()
cont_ttl = threading.Thread(target=ts.continuous_ttl_check)
cont_ttl.setDaemon(True)
cont_ttl.start()

mythd = threading.Thread(target=mythread)
mythd.start()





