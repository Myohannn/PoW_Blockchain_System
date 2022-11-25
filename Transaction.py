import hashlib
from datetime import datetime


class Transaction:
    def __init__(self, TxInList, TxOutList):
        # tx id
        self.TxId = self.genTxId(TxInList, TxOutList)
        # tx in
        self.TxInList = TxInList
        # tx out
        self.TxOutList = TxOutList

    def genTxId(self, txIns, txOuts):
        txInString = ''
        txOutString = ''

        if txIns != None:
            for txin in txIns:
                txInString += txin.genTxInString()

        if txOuts != None:
            for txout in txOuts:
                txOutString += txout.genTxOutString()

        txString = txInString + txOutString + self.getTimestamp()
        sha256 = hashlib.sha256()
        sha256.update(txString.encode('UTF-8'))
        return sha256.hexdigest()[0:8]

    def setTxID(self, txid):
        self.TxId = txid

    def genTxString(self):
        txInString = ''
        txOutString = ''

        for txIn in self.TxInList:
            txInString += txIn.genTxInString()

        for txOut in self.TxOutList:
            txInString += txOut.genTxOutString()

        return self.TxId + txInString + txOutString

    def getTimestamp(self):
        timestamp = datetime.now().timestamp()
        date_time = datetime.fromtimestamp(timestamp)
        str_date_time = date_time.strftime("%Y%m%d%H%M%S%s")
        return str_date_time
