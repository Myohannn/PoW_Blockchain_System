class TxOut:
    def __init__(self, address, amount):
        # tx out address
        self.address = address
        # tx out amount
        self.amount = amount

    def genTxOutString(self):
        return str(self.address) + str(self.amount)
