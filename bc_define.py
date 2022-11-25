import hashlib
import MerkleTree
from ECDSA import *

from TxOut import TxOut
from Transaction import Transaction
from Block import Block
from TxIn import TxIn
from UTXOs import UTXOs

from datetime import datetime

# blockchain pre define info
# block update difficulty per 2 block
diffInterval = 2


class Blockchain:
    # blockchain class is a list to append the block one by one.
    def __init__(self):
        self.blocks = []
        self.target_hash = 0

        # when a new blockchain class was implement,
        # the genesis block will be created as first block
        genesis_block = genGenesisBlock()
        self.blocks.append(genesis_block)


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
    # the block data is hard code
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

    return coinbaseTx


def addNewBlock(blocks, tx_list, index, previousHash, nonce, address):
    hash_code, newBlock = genNewBlock(blocks, tx_list, index, previousHash, nonce)
    if newBlock:
        newBlock.setTransactions(tx_list)
    return hash_code, newBlock


def genNewBlock(blocks, tx_list, index, previousHash, nonce):
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

    hash = hashlib.sha256(rawString.encode("utf-8")).hexdigest()
    hash_result = hashlib.sha256(hash.encode("utf-8")).hexdigest()
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

    # expected time to gen a new block
    timeExpected = genBlockIntervel * diffInterval

    # actual time to gen a new block
    timeUsed = int(latestBlock.timestamp) - int(lastAdjustedBlock.timestamp)

    # difficulty adjustment
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

    # get UTXOs in the blockchain
    # utxos = genUTXOs(blockchain)

    # validate the tx in blocks
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


def isValidTx(newTx, utxos):
    # validate transaction
    for txIn in newTx.TxInList:
        key = txIn.TxOutId + '[' + str(txIn.TxOutIndex) + ']'
        if key not in utxos.keys():
            return False
        else:
            newtxOut = utxos[key]

            if (verify(newtxOut.address, txIn.Signature, '123') == "true"):
                for txOut in newTx.TxOutList:
                    if txOut.amount > newtxOut.amount:
                        return False
                    elif txOut.amount <= newtxOut.amount:
                        diff = newtxOut.amount - txOut.amount
                        return True, diff
            else:
                return False


def sendTX():
    # Send the transaction to other miner's public key
    # TODO
    print()


def buildNewTransaction(id, index, signature, address, amount):
    # build a new transaction
    newTxIn = []
    newTxIn = newTxIn.append(TxIn(id, index, signature))
    newTxOut = []
    newTxOut = newTxOut.append(TxOut(address, amount))
    NewTransaction = Transaction(newTxIn, newTxOut)
    return NewTransaction


def block2Dict(block):
    # convert Block obj to dict
    b_dict = {}
    b_dict['index'] = block.index
    b_dict['hash'] = block.hash
    b_dict['prevBlockHash'] = block.prevBlockHash
    b_dict['rootHash'] = block.rootHash
    b_dict['difficulty'] = block.difficulty
    b_dict['nonce'] = block.nonce
    b_dict['timestamp'] = block.timestamp

    txList2dict = []
    for tx in block.transactionList:
        txList2dict.append(tx2dict(tx))

    b_dict['transactionList'] = txList2dict

    return b_dict


def tx2dict(tx):
    # convert Transaction obj to dict
    tx_dict = {}
    tx_dict['TxId'] = tx.TxId
    txIn_list = []
    txOut_list = []
    for txIn in tx.TxInList:
        txIn_list.append(txIn2Dict(txIn))

    for txOut in tx.TxOutList:
        txOut_list.append(txOut2Dict(txOut))

    tx_dict['TxInList'] = txIn_list
    tx_dict['TxOutList'] = txOut_list

    return tx_dict


def txIn2Dict(txIn):
    # convert TxIn obj to dict
    txIn_dict = {'TxOutId': txIn.TxOutId, 'TxOutIndex': txIn.TxOutIndex, 'signature': txIn.signature}
    return txIn_dict


def txOut2Dict(txOut):
    # convert TxOut obj to dict
    if not isinstance(txOut.address, str):
        addr = txOut.address.to_pem().decode()
    else:
        addr = txOut.address
    txOut_dict = {'address': addr, 'amount': txOut.amount}
    return txOut_dict


def dict2Block(b_dict):
    # convert dict to Block obj

    index = b_dict['index']
    hash = b_dict['hash']
    prevBlockHash = b_dict['prevBlockHash']
    rootHash = b_dict['rootHash']
    difficulty = b_dict['difficulty']
    nonce = b_dict['nonce']
    timestamp = b_dict['timestamp']

    block = Block(index, hash, prevBlockHash, rootHash, difficulty, nonce, timestamp)
    txList = []
    for tx_dict in b_dict['transactionList']:
        txList.append(dict2Tx(tx_dict))

    block.setTransactions(txList)

    return block


def dict2Tx(tx_dict):
    # convert dict to Transaction obj

    TxId = tx_dict['TxId']
    TxInList = tx_dict['TxInList']
    TxOutList = tx_dict['TxOutList']

    tx = Transaction(dict2TxIn(TxInList), dict2TxOut(TxOutList))
    tx.setTxID(TxId)

    return tx


def dict2TxIn(txInList_dict):
    # convert dict to TxIn obj

    TxInList = []

    for txIn in txInList_dict:
        TxOutId = txIn['TxOutId']
        TxOutIndex = txIn['TxOutIndex']
        signature = txIn['signature']

        newtxIn = TxIn(TxOutId, TxOutIndex, signature)
        TxInList.append(newtxIn)
    return TxInList


def dict2TxOut(txOutList_dict):
    # convert dict to TxOut obj

    TxOutList = []

    for txOut in txOutList_dict:
        address = str(txOut['address'])
        vk = VerifyingKey.from_pem(address.encode())

        amount = txOut['amount']
        newtxOut = TxOut(vk, amount)
        TxOutList.append(newtxOut)
    return TxOutList


def msg2txList(msgtxList):
    # convert gRPC message to transactionList obj
    txList = []

    for msgtx in msgtxList:
        txInList = []
        txOutList = []

        for msgTxIn in msgtx.TxInList:
            txIn = TxIn(msgTxIn.TxOutId, msgTxIn.TxOutIndex, msgTxIn.signature)
            txInList.append(txIn)

        for msgTxOut in msgtx.TxOutList:
            addr = VerifyingKey.from_pem(msgTxOut.address.encode())
            txOut = TxOut(addr, msgTxOut.amount)
            txOutList.append(txOut)

        tx = Transaction(txInList, txOutList)
        tx.setTxID(msgtx.TxId)
        txList.append(tx)

    return txList


# Database utils
def saveBlocktoDB(mycol, block):
    b_dict = block2Dict(block)
    mydict = {"_id": block.index, "block info": b_dict}

    mycol.insert_one(mydict)


def getBlockchainFromDB(mycol, blockchain):
    for x in mycol.find():
        db_block = dict2Block(x['block info'])
        blockchain.append(db_block)


def getBlockFromDB(mycol, blockIndex):
    myquery = {"_id": blockIndex}

    mydoc = mycol.find(myquery)
    block = None

    for x in mydoc:
        block = dict2Block(x['block info'])

    return block
