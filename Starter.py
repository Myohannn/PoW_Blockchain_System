from bc_define import *
from bc_server import *
from bc_client import *
from GUI import *

import sys
import threading
import time


class Starter:
    def __init__(self, minerIndex):
        # current miner
        self.minerIndex = minerIndex
        self.miner = None

    def run(self):
        # start server side
        # create threads
        thread1 = myThread1(1, "Server", self.minerIndex)
        thread1.start()
        time.sleep(2)

        # start client side
        self.miner = bc_Miner(self.minerIndex)
        self.miner.run()
        thread2 = myThread2(2, "Client", 2, self.miner)
        thread2.start()

        # start GUI
        runGUI(miner0).run()


class myThread1(threading.Thread):
    def __init__(self, threadID, name, port_index):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.port_index = port_index

    def run(self):
        # get server port
        port_list = []
        f = open("portList.txt")
        line = f.readline()
        while line:
            port_list.append(line.replace('\n', ''))
            line = f.readline()
        f.close()

        # update server side miner_index
        local_port = port_list[self.port_index]
        serve(local_port)


class myThread2(threading.Thread):
    def __init__(self, threadID, name, counter, miner):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.miner = miner

    def run(self):
        self.miner.mining()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        miner_index = int(sys.argv[1])
    else:
        miner_index = 0
    # print(miner_index)
    if not isinstance(miner_index, int):
        print("Invalid Miner Index")
    else:
        if 5 > miner_index >= 0:
            miner0 = Starter(miner_index)
            miner0.run()
        else:
            print("Miner Index out of range")
