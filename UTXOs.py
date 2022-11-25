class UTXOs:

    def __init__(self, utxos):
        # format: key: txOutputID[txOutIndex] | value: TxOut

        self.utxos = utxos

    def genUTXOsString(self):
        result = ""
        for k,v in self.utxos.items():
            result += k + "\n" + v.genTxOutString() + "\n"

        return result

