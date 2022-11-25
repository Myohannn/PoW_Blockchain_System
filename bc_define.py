import hashlib
import random

import hashlib
from datetime import datetime

from TxOut import TxOut
from Transaction import Transaction
from Block import Block
from TxIn import TxIn
from UTXOs import UTXOs

import MerkleTree
import ECDSA

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

# blockchain pre define info
diffInterval = 2


# blockchain class is a list to append the block one by one.
class Blockchain:
    def __init__(self):
        self.blocks = []
        self.target_hash = 0

        # when a new blockchain class was implement, the genesis block will be created as first block
        genesis_block = genGenesisBlock()
        self.blocks.append(genesis_block)
        # blockchain difficulty

        utxos = ''

        publicKey = ''
        privateKey = ''

        publicKeyList = []

        diffInterval = 2


def NewBlockchain():
    new_blockchain = Blockchain()
    return new_blockchain


def genGenesisBlock():
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
                         'bf8ffdf71974a51a0862e6d618650bc0', 3, 123, '123456')
    genesisBlock.setTransactions(genesisTXList)

    # add genesis block to blockchain
    return genesisBlock


def setCoinBaseTx(address):
    # initiate coinbase tx
    coinbaseTxInList = []
    coinbaseTxOutList = []
    coinbaseTxOutList.append(TxOut(address, 50))

    coinbaseTx = Transaction(coinbaseTxInList, coinbaseTxOutList)

    # add coinbase tx to tx list
    return coinbaseTx


def addNewBlock(blocks, tx_list, index, previousHash, nonce, address):
    # add coinbase TX
    # tx_list.append(setCoinBaseTx(address))
    hash_code, newBlock = genNewBlock(blocks, tx_list, index, previousHash, nonce)
    if newBlock:
        newBlock.setTransactions(tx_list)
    return hash_code, newBlock

    # print("new block found! Block index:", index)
    # # deep copy tx list
    # newBlockTxList = []
    # for i in tx_list:
    #     newBlockTxList.append(i)
    # newBlock.setTransactions(newBlockTxList)
    #
    # return newBlock


def genNewBlock(blocks, tx_list, index, previousHash, nonce):
    # initiate block parameters
    # nonce = 0
    timestamp = getTimestamp()
    difficulty = getDifficulty(blocks)

    # start solving puzzle
    # check whether the miner has synchronized the blockchain
    if index < len(blocks):
        return None

    # gen transactions' merkle root (rootHash)
    rootHash = genRootHash(tx_list)

    # calculate block hash value
    hashValue = calculateHash(index, timestamp, previousHash, rootHash, difficulty, nonce)

    # check whether hash value satisfy the difficulty
    if checkHashAndDiffculty(hashValue, difficulty):
        hash_code = "New block's hash is" + str(hashValue)
        return hash_code, Block(index, hashValue, previousHash, rootHash, difficulty, nonce, timestamp)
    else:
        hash_code = "False"
        return hash_code, None


def checkHashAndDiffculty(hashValue, difficulty):
    target = 2 ** (256 - difficulty)
    if int(hashValue, 16) < target:
        return True
    else:
        return False


def calculateHash(index, timestamp, previousHash, rootHash, difficulty, nonce):
    rawString = str(index) + str(timestamp) + str(previousHash) + str(rootHash) + str(difficulty) + str(nonce)

    # print("raw string",rawString)
    # apply sha256 twice
    hash = hashlib.sha256(rawString.encode("utf-8")).hexdigest()
    hash_result = hashlib.sha256(hash.encode("utf-8")).hexdigest()
    # print('hash result:',hash_result)
    return hash_result


def getDifficulty(blocks):
    latestBlock = blocks[-1]

    # adjust difficulty every diffInterval blocks e.g.: every 2 blocks
    if latestBlock.index % diffInterval == 0 and latestBlock.index != 0:
        newDifficulty = adjustDiffculty(latestBlock, blocks)
        # print("Difficulty adjusted to", newDifficulty)
        return newDifficulty
    else:
        return latestBlock.difficulty


def adjustDiffculty(latestBlock, currentBlockchain):
    # the time interval to gen a new block
    genBlockIntervel = 5

    # get last adjusted block
    lastAdjustedBlock = currentBlockchain[len(currentBlockchain) - diffInterval]
    # print('current chain size:', len(currentBlockchain))
    # expected time to gen a new block
    timeExpected = genBlockIntervel * diffInterval

    # actual time to gen a new block
    timeUsed = int(latestBlock.timestamp) - int(lastAdjustedBlock.timestamp)
    # print('latestBlock:', latestBlock.index, latestBlock.timestamp)
    # print('lastAdjustedBlock:', lastAdjustedBlock.index, lastAdjustedBlock.timestamp)
    # print('timeUsed:', timeUsed)
    # adjust difficulty based on the gen block time interval
    # to be fixed
    if timeExpected > timeUsed:
        return lastAdjustedBlock.difficulty + 1
    elif timeExpected < timeUsed:
        return lastAdjustedBlock.difficulty - 1
    else:
        return lastAdjustedBlock.difficulty


def genRootHash(tx_list):
    txStringList = []
    for tx in tx_list:
        txStringList.append(tx.genTxString())

    return MerkleTree.genMerkleRoot(txStringList)


def getTimestamp():
    timestamp = datetime.now().timestamp()
    date_time = datetime.fromtimestamp(timestamp)
    # print(t)
    str_date_time = date_time.strftime("%Y%m%d%H%M%S")
    return str_date_time


def genUTXOs(blocks):
    print(blocks)

    txOutDict = {}
    txInList = []
    for block in blocks:

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


def isValidBlock(blockchain, block):
    prevBlock = blockchain[-1]
    if prevBlock.index != block.index - 1:
        return False

    if prevBlock.hash != block.prevBlockHash:
        return False

    hash = hashlib.sha256(block.genBlockString().encode("utf-8")).hexdigest()
    hash_result = hashlib.sha256(hash.encode("utf-8")).hexdigest()
    if block.hash != hash_result:
        return False

    utxos = genUTXOs(blockchain)

    # if not isValidTxInBlock(block, utxos.utxos):
    #     return False

    return True


def isValidTxInBlock(block, utxos):
    txList = block.transactionList

    for tx in txList:
        if isValidTx(tx, utxos):
            continue
        else:
            print("Invalid TX:", tx.TxId)
            return False

    return True


# def isValidTx(newTx, utxos):
#     for txIn in newTx.TxInList:
#         key = txIn.TxOutId + '[' + str(txIn.TxOutIndex) + ']'
#         if key not in utxos.keys():
#             return False
#         else:
#             newtxOut = utxos[key]
#
#             # check signature TODO
#
#             for txOut in newTx.TxOutList:
#                 if txOut.amount > newtxOut.amount:
#                     return False
#                 elif txOut.amount < newtxOut.amount:
#                     diff = newtxOut.amount - txOut.amount
#                     return True
#
#     # return True


def isValidSign(pk, signature, message):
    # verify the signature using public key
    try:
        pk.verify(signature, message, ec.ECDSA(hashes.SHA256()))
    except:
        return "false"
    else:
        return "true"


def sendTX():
    # TODO
    print()


def buildNewTransaction(id, index, signature, address, amount):
    newTxIn = []
    newTxIn = newTxIn.append(TxIn(id, index, signature))
    newTxOut = []
    newTxOut = newTxOut.append(TxOut(address, amount))
    NewTransaction = Transaction(newTxIn, newTxOut)
    return NewTransaction


# def isValidTx(newTx, utxos):
#     for txIn in newTx.TxInList:
#         key = txIn.TxOutId + '[' + str(txIn.TxOutIndex) + ']'
#         if key not in utxos.keys():
#             return False
#         else:
#             newtxOut = utxos[key]
#
#             # check signature TODO
#             if (ECDSA.verify(newtxOut.address, txIn.Signature, '123') == "true"):
#                 for txOut in newTx.TxOutList:
#                     if txOut.amount > newtxOut.amount:
#                         return False
#                     elif txOut.amount <= newtxOut.amount:
#                         diff = newtxOut.amount - txOut.amount
#                         return True, diff
#             else:
#                 return False

def isValidTx(newTx, utxos):
    for txIn in newTx.TxInList:
        key = txIn.TxOutId + '[' + str(txIn.TxOutIndex) + ']'
        if key not in utxos.keys():
            return False
        else:
            newtxOut = utxos[key]

            # check signature TODO

            for txOut in newTx.TxOutList:
                if txOut.amount > newtxOut.amount:
                    return False
                elif txOut.amount < newtxOut.amount:
                    diff = newtxOut.amount - txOut.amount
                    return True
