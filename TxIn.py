class TxIn:
    def __init__(self, txOutId, txOutIndex, sign):
        # previous tx out ID
        self.TxOutId = txOutId
        # previous tx out index
        self.TxOutIndex = txOutIndex
        # previous tx signature
        self.signature = sign

    def genTxInString(self):
        return str(self.TxOutId) + str(self.TxOutIndex)
