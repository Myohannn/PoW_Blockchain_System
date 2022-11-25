import hashlib
from datetime import datetime

from TxOut import TxOut
from Transaction import Transaction
from Block import Block
from TxIn import TxIn
from UTXOs import UTXOs

import MerkleTree

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec


class Miner:

    def __init__(self, minerIndex):
        # miner info
        self.blockchain = []
        self.localTxList = []
        self.utxos = ''

        self.publicKey = ''
        self.privateKey = ''

        self.publicKeyList = []

        self.diffInterval = 2

        # generate genesisBlock
        self.genGenesisBlock()

    # def assignKeys(self):

    def genGenesisBlock(self):
        # gen genesis block tx out
        genesisTxOutList = []
        genesisTxOutList.append(TxOut("", 1000))
        genesisTxInList = []

        # gen genesis  tx list
        genesisTXList = []
        genesisTX = Transaction(genesisTxInList, genesisTxOutList)
        genesisTX.TxId = "00000000"
        genesisTXList.append(genesisTX)

        # gen genesis block
        genesisBlock = Block(0, 'bf8ffdf71974a51a0862e6d618650bc0', 'bf8ffdf71974a51a0862e6d618650bc0',
                             'bf8ffdf71974a51a0862e6d618650bc0', 20, 123, '123456')
        genesisBlock.setTransactions(genesisTXList)

        # add genesis block to blockchain
        self.blockchain.append(genesisBlock)

    def setCoinBaseTx(self):
        # initiate coinbase tx
        self.localTX = []

        coinbaseTxInList = []
        # coinbaseTxInList.append(TxIn('', 0, ''))
        coinbaseTxOutList = []
        coinbaseTxOutList.append(TxOut('', 50))

        coinbaseTx = Transaction(coinbaseTxInList, coinbaseTxOutList)

        # add coinbase tx to tx list
        self.localTxList.append(coinbaseTx)

    def addNewBlock(self, index, previousHash):
        newBlock = self.genNewBlock(index, previousHash)
        # add miner award
        self.setCoinBaseTx()
        print("new block found! Block index:", index)
        # deep copy tx list
        newBlockTxList = []
        for i in self.localTxList:
            newBlockTxList.append(i)
        newBlock.setTransactions(newBlockTxList)

        return newBlock

    def genNewBlock(self, index, previousHash):
        # initiate block parameters
        nonce = 0
        timestamp = self.getTimestamp()
        difficulty = self.getDifficulty(self.blockchain)

        # start solving puzzle
        while True:
            # print("Trying nonce:",nonce)
            # check whether the miner has synchronized the blockchain
            if index < len(self.blockchain):
                return None

            # gen root hash by transactions
            rootHash = self.genRootHash()

            # calculate hash value
            hashValue = self.calculateHash(index, timestamp, previousHash, rootHash, difficulty, nonce)

            # check whether hash value satisfy the difficulty
            if self.checkHashAndDiffculty(hashValue, difficulty):
                return Block(index, hashValue, previousHash, rootHash, difficulty, nonce, timestamp)
            else:
                nonce += 1

    def checkHashAndDiffculty(self, hashValue, difficulty):

        target = 2 ** (256 - difficulty)
        if int(hashValue, 16) < target:
            return True
        else:
            return False

        # # convert hex hash value to binary string
        # binary_string = bin(int(hashValue, 16))[2:]
        #
        # binaryOfDifficulty = binary_string[0:difficulty]
        #
        # print('hash value:', hashValue)
        # print('binary Of Difficulty:', binaryOfDifficulty)
        # print('Difficulty:', difficulty)
        # print()

        # print("binary_string:",binary_string)
        # print("binaryOfDifficulty:",binaryOfDifficulty)
        # exit()

        # if 1 exist in the prefix of binary string, then return false
        # if "0" in binaryOfDifficulty:
        #     return False
        # # if 1 does not exist in the prefix of binary string, then return true
        # else:
        #     return True

    def calculateHash(self, index, timestamp, previousHash, rootHash, difficulty, nonce):
        rawString = str(index) + str(timestamp) + str(previousHash) + str(rootHash) + str(difficulty) + str(nonce)
        # print("raw string",rawString)
        # apply sha256 twice
        hash = hashlib.sha256(rawString.encode("utf-8")).hexdigest()
        hash_result = hashlib.sha256(hash.encode("utf-8")).hexdigest()
        # print('hash result:',hash_result)
        return hash_result

    def getDifficulty(self, currentBlockchain):
        latestBlock = currentBlockchain[-1]

        # adjust difficulty every diffInterval blocks e.g.: every 2 blocks
        if latestBlock.index % self.diffInterval == 0 and latestBlock.index != 0:
            newDifficulty = self.adjustDiffculty(latestBlock, currentBlockchain)
            print("Difficulty adjusted to", newDifficulty)
            return newDifficulty
        else:
            return latestBlock.difficulty

    def adjustDiffculty(self, latestBlock, currentBlockchain):
        # the time interval to gen a new block
        genBlockIntervel = 5

        # get last adjusted block
        lastAdjustedBlock = currentBlockchain[len(currentBlockchain) - self.diffInterval]
        print('current chain size:', len(currentBlockchain))
        # expected time to gen a new block
        timeExpected = genBlockIntervel * self.diffInterval

        # actual time to gen a new block
        timeUsed = int(latestBlock.timestamp) - int(lastAdjustedBlock.timestamp)
        print('latestBlock:', latestBlock.index, latestBlock.timestamp)
        print('lastAdjustedBlock:', lastAdjustedBlock.index, lastAdjustedBlock.timestamp)
        print('timeUsed:', timeUsed)
        # adjust difficulty based on the gen block time interval
        # to be fixed
        if timeExpected > timeUsed:
            return lastAdjustedBlock.difficulty + 1
        elif timeExpected < timeUsed:
            return lastAdjustedBlock.difficulty - 1
        else:
            return lastAdjustedBlock.difficulty

    def genRootHash(self):
        txStringList = []
        for tx in self.localTxList:
            txStringList.append(tx.genTxString())

        return MerkleTree.genMerkleRoot(txStringList)

    def getTimestamp(self):
        timestamp = datetime.now().timestamp()
        date_time = datetime.fromtimestamp(timestamp)
        # print(t)
        str_date_time = date_time.strftime("%Y%m%d%H%M%S")
        return str_date_time

    def genUTXOs(self):
        print()

        txOutDict = {}
        txInList = []
        for block in self.blockchain:

            for tx in block.transactionList:

                txInofTx = tx.TxInList
                txOutofTx = tx.TxOutList

                # print("txInofTx:",txInofTx)
                # print("txOutofTx:",txOutofTx)

                # get all txIn
                for i in range(len(txInofTx)):
                    txInList.append(txInofTx[i].TxOutId + "[" + str(txInofTx[i].TxOutIndex) + "]")

                # get all txOut
                for i in range(len(txOutofTx)):
                    key = str(tx.TxId + "[" + str(i) + "]")
                    txOutDict[key] = txOutofTx[i]

        # remove the txOut that appears in txIn
        for usedTxIn in txInList:
            if usedTxIn in txOutDict.keys():
                txOutDict.pop(usedTxIn)

        return UTXOs(txOutDict)

    def isValidBlock(self):
        return True

    def isValidTx(self):
        return True

    def isValidSign(self, pk, signature, message):
        # verify the signature using public key
        try:
            pk.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        except:
            return "false"
        else:
            return "true"
