import json
from tkinter import *
from Starter import *


class MainPage(object):
    def __init__(self, master=None):
        self.root = master
        self.root.geometry('%dx%d' % (800, 800))
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)  # 创建Frame
        self.page.pack()

        Button(self.page, text='Send Transaction', font=10, width=15, height=3, command=self.goSendTXPage).pack(
            fill=X,
            pady=60,
            padx=10)
        Button(self.page, text='Show UTXOs', font=30, width=15, height=3, command=self.goShowUTXOsPage).pack(fill=X,
                                                                                                             pady=40,
                                                                                                             padx=10)
        Button(self.page, text='Show Block Info', font=30, width=15, height=3, command=self.goShowBlockPage).pack(
            fill=X,
            pady=40,
            padx=10)

    def goSendTXPage(self):
        self.page.destroy()
        sendTXPage(self.root)
        self.root.title('Send Transaction')

    def goShowUTXOsPage(self):
        self.page.destroy()
        showUTXOsPage(self.root)
        self.root.title('Show UTXOs')

    def goShowBlockPage(self):
        self.page.destroy()
        showBlockPage(self.root)
        self.root.title('Show Block Info')


class sendTXPage(object):
    def __init__(self, master=None):
        self.root = master
        # self.root.geometry('%dx%d' % (500, 500))
        self.txOutID = StringVar()
        self.txOutIndex = StringVar()
        self.address = StringVar()
        self.amount = StringVar()
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack()

        Label(self.page).grid(row=0, stick=W)
        Label(self.page, text='Transaction Output ID: ').grid(row=1, stick=W, pady=10, column=0)
        Entry(self.page, textvariable=self.txOutID).grid(row=2, stick=W, pady=10, ipadx=20)
        Label(self.page, text='Transaction Output Index: ').grid(row=3, stick=W, pady=10, column=0)
        Entry(self.page, textvariable=self.txOutIndex).grid(row=4, stick=W, pady=10, ipadx=20)
        Label(self.page, text='Receiver Address: ').grid(row=5, stick=W, pady=10, column=0)
        Entry(self.page, textvariable=self.address).grid(row=6, stick=W, pady=10, ipadx=20)
        Label(self.page, text='Amount: ').grid(row=7, stick=W, pady=10, column=0)
        Entry(self.page, textvariable=self.amount).grid(row=8, stick=W, pady=10, ipadx=20)
        Button(self.page, text='Send', command=self.sendTX).grid(row=9, stick=W, pady=10)
        # Button(self.page, text='Clean Text', command=self.clean).grid(row=6, stick=W, pady=10)
        Button(self.page, text='Back', command=self.goMainPage).grid(row=10, stick=W, pady=10)

    def sendTX(self):
        txOutID = self.txOutID.get()
        txOutIndex = self.txOutIndex.get()
        address = self.address.get()
        amount = self.amount.get()

        # send trasnaction TODO

    def goMainPage(self):
        self.page.destroy()
        MainPage(self.root)
        self.root.title(f"Miner {starter1.minerIndex}")


class showUTXOsPage(object):
    def __init__(self, master=None):
        self.root = master
        # self.root.geometry('%dx%d' % (500, 500))
        self.UTXOs = StringVar()
        self.createPage()
        self.ListBox = None

    def createPage(self):
        self.page = Frame(self.root)

        Label(self.page).grid(row=0, stick=W)

        Label(self.page, text='UTXOs: ').grid(row=5, stick=W, pady=10)

        s = Scrollbar(self.page, orient=VERTICAL)
        s2 = Scrollbar(self.page, orient=HORIZONTAL)
        self.ListBox = Listbox(self.page, width=50, yscrollcommand=s.set, xscrollcommand=s2.set)

        s.config(command=self.ListBox.yview())
        s2.config(command=self.ListBox.xview())

        self.ListBox.grid(row=6, stick=W,
                          pady=10,
                          ipadx=50,
                          ipady=200)

        global starter1

        result = starter1.miner.getUTXOs()

        keys = result.utxos.key
        amounts = result.utxos.amount
        owner = result.utxos.owner

        for i in range(len(keys)):
            desplay_result = keys[i] + f" Amount: {amounts[i]} Owner: {owner[i]}"

            self.ListBox.insert(END, desplay_result)
            self.ListBox.insert(END, "\n")

        Button(self.page, text='Back', command=self.goMainPage).grid(row=7, stick=W, pady=10)
        self.page.pack()

    def getUTXOs(self):
        # getUTXOs() TODO
        global starter1
        # genUTXOs(starter1.bc_Miner.minerIndex)

        result = starter1.miner.getUTXOs()

        keys = result.utxos.key
        amounts = result.utxos.amount
        owner = result.utxos.owner

        desplay_result = ""
        for i in range(len(keys)):
            desplay_result += keys[i] + f"\nAmount: {amounts[i]}\nOwner: {owner[i]} \n\n"

    def goMainPage(self):
        self.page.destroy()
        MainPage(self.root)
        self.root.title(f"Miner {starter1.minerIndex}")


class showBlockPage(object):
    def __init__(self, master=None):
        self.root = master
        # self.root.geometry('%dx%d' % (500, 500))
        self.blockIndex = StringVar()
        self.blockInfo = StringVar()
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack()
        # self.page

        Label(self.page).grid(row=0, stick=W)
        Label(self.page, text='Block Index: ').grid(row=1, stick=W, pady=10, column=0)
        Entry(self.page, textvariable=self.blockIndex).grid(row=2, stick=W, pady=10, ipadx=20)
        Label(self.page, text='Block Info: ').grid(row=3, stick=W, pady=10)
        Label(self.page, bg="white", textvariable=self.blockInfo, anchor=NW, justify='left', width=21).grid(row=4,
                                                                                                            stick=W,
                                                                                                            pady=10,
                                                                                                            ipadx=200,
                                                                                                            ipady=100)
        Button(self.page, text='Get Block', command=self.getBlock).grid(row=5, stick=W, pady=10)
        Button(self.page, text='Back', command=self.goMainPage).grid(row=7, stick=W, pady=10)

    def getBlock(self):
        index = self.blockIndex.get()

        # get Block Info TODO
        block = starter1.miner.getBlockInfo(int(index)).newBlock

        for tx in block.transactionList:

            for txOut in tx.TxOutList:
                hash = hashlib.sha256((txOut.address).encode("utf-8")).hexdigest()
                hash_result = hashlib.sha256(hash.encode("utf-8")).hexdigest()
                txOut.address = hash_result

        self.blockInfo.set(block)

    def goMainPage(self):
        self.page.destroy()
        MainPage(self.root)
        self.root.title(f"Miner {starter1.minerIndex}")


# from document_retriever.retriever import TfidfDocRanker
# from document_reader.reader import Predictor
# from qaSystem import QaSystem

# retriever = None
# reader = None
starter1 = None


class runGUI:
    def __init__(self, starter):
        global starter1
        starter1 = starter
        # self.stater = stater

    def run(self):
        print("GUI go")

        root = Tk()
        root.title(f"Miner {starter1.minerIndex}")
        MainPage(root)
        root.mainloop()


if __name__ == "__main__":
    runGUI(0).run()
