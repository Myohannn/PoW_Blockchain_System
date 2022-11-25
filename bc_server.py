import time
from concurrent import futures
import logging
import grpc
import grpc_utils.blockchain_pb2 as blockchain_pb2
import grpc_utils.blockchain_pb2_grpc as blockchain_pb2_grpc
from bc_define import *
from ECDSA import *
import pymongo


# We implement the function at server class
class BlockchainServer(blockchain_pb2_grpc.BlockChainServicer):
    # When the server created, a new blockchain will be created too
    def __init__(self):
        self.blockchain = NewBlockchain()
        self.localTxList = []
        self.clientIndex = '-1'

        self.publicKey = ''
        self.privatekey = ''
        self.publicKey_list = []

        myClient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = myClient["BlockchainDB"]
        self.col = None

        # the longest blockchain in the network
        # self.highestBlockIndex = 1

    def initTxList(self, request, context):
        self.localTxList = []
        coinbaseTx = setCoinBaseTx(self.publicKey)
        self.localTxList.append(coinbaseTx)
        response = blockchain_pb2.InitTxListResponse(message="Tx list init")
        return response

    # Receive miner's transaction and expected hash. And return the result or the address of the new block to the miner.
    def addNewBlock(self, request, context):
        current_blockIndex = len(self.blockchain.blocks)
        previousBlockHash = self.blockchain.blocks[current_blockIndex - 1].hash
        nonce = request.nonce
        # print("local TX:", self.localTxList)
        hash_code, block = addNewBlock(self.blockchain.blocks, self.localTxList, current_blockIndex, previousBlockHash,
                                       nonce, self.publicKey)

        if block:
            # mydict = {"_id": block.index, "block info": block}
            # x = self.col.insert_one(mydict)

            self.blockchain.blocks.append(block)
            saveBlocktoDB(self.col, block)
            print(f"Block {block.index} saved in to storage!")
            # time.sleep(5)

            print("Blockchain updated: ")
            for i in range(len(self.blockchain.blocks)):
                print("block " + str(i) + ":")
                print('block hash = ' + self.blockchain.blocks[i].hash)
                # print('block transaction = ' + self.blockchain.blocks[i].Transaction)
            print()

            pb2_block = blockchain_pb2.Block(index=block.index, hash=block.hash, prevBlockHash=block.prevBlockHash,
                                             rootHash=block.rootHash, difficulty=block.difficulty, nonce=block.nonce,
                                             timestamp=block.timestamp,
                                             transactionList=txList2msg(block.transactionList))

            return blockchain_pb2.AddBlockResponse(hash=hash_code, newBlock=pb2_block)
        else:
            return blockchain_pb2.AddBlockResponse(hash=hash_code, newBlock=None)

    def receiveBlock(self, request, context):
        print(request.message)
        msgBlock = request.newBlock
        block = Block(msgBlock.index, msgBlock.hash, msgBlock.prevBlockHash, msgBlock.rootHash, msgBlock.difficulty,
                      msgBlock.nonce, msgBlock.timestamp)
        msgTxList = msgBlock.transactionList
        block.setTransactions(msg2txList(msgTxList))
        # print("received block txlist", msgTxList)
        # block = NewBlock(request.newBlock.transaction, request.newBlock.prevBlockHash)
        if isValidBlock(self.blockchain.blocks, block) or len(self.blockchain.blocks) == 1:
            print("Valid block")
            print("valid block's tx list", block.transactionList)
            self.blockchain.blocks.append(block)
            saveBlocktoDB(self.col, block)

            print("Blockchain updated: ")
            for i in range(len(self.blockchain.blocks)):
                print("block " + str(i) + ":")
                print('block hash = ' + self.blockchain.blocks[i].hash)
                # print('block transaction = ' + self.blockchain.blocks[i].transactionList)
            print()

            response = blockchain_pb2.ReceiveBlockResponse(message="OK")
            blockchain_pb2.AddBlockResponse(hash="Restart")

        else:
            response = blockchain_pb2.ReceiveBlockResponse(message="Invalid Block!!!")

        return response

    def receiveMessage(self, request, context):
        req = request.message
        # print("server MSG: ", req)
        if req == "Highest Index" or req == "Local index":
            response = blockchain_pb2.receiveMessageResponse(message=str(len(self.blockchain.blocks)))
            return response
        if req.startswith("Get Block"):
            block_idx = int(req.split(":")[-1])
            print("some one is getting block", block_idx)

            block = self.blockchain.blocks[block_idx]

            pb2_block = blockchain_pb2.Block(index=block.index, hash=block.hash, prevBlockHash=block.prevBlockHash,
                                             rootHash=block.rootHash, difficulty=block.difficulty, nonce=block.nonce,
                                             timestamp=block.timestamp,
                                             transactionList=txList2msg(block.transactionList))
            # print("needed block:", pb2_block)
            msg = f"Here is block {block_idx}"
            response = blockchain_pb2.receiveMessageResponse(message=msg, newBlock=pb2_block)
            return response

            # initialize server state

    # check channel aliveness
    def getState(self, request, context):
        if self.clientIndex == '-1':
            self.clientIndex = request.message
            sk, vk = loadKey(self.clientIndex)
            self.privatekey = sk
            self.publicKey = vk
            # get public key pair list
            for i in range(4):
                self.publicKey_list.append(loadKey(i))
            col_name = f'miner{self.clientIndex}'
            self.col = self.mydb[col_name]
            # safe genesis block
            # try:
            #     saveBlocktoDB(self.col, self.blockchain.blocks[0])
            # except:
            #     print("Genesis block already in DB")

        message = f'Miner {self.clientIndex} alive!'
        response = blockchain_pb2.getStateResponse(message=message)
        return response

    def getUTXOs(self, request, context):
        utxos = genUTXOs(self.blockchain.blocks).utxos
        print("UTXOS:::::", utxos)
        msgUTXOs = UTXOs2msg(utxos)
        response = blockchain_pb2.getUTXOsResponse(utxos=msgUTXOs)
        return response

    def QueryDB(self, request, context):
        print("Query DB request:", request.message)
        db_blockchain = getBlockchainFromDB(self.col, self.blockchain.blocks)

        print("Blockchain from DB: ")
        for i in range(len(self.blockchain.blocks)):
            print("block " + str(i) + ":")
            print('block hash = ' + self.blockchain.blocks[i].hash)
        print()

        return blockchain_pb2.QueryDBResponse(message='Blockchain reading complete!')

    def addNewtransaction(self, request, context):
        if isValidTx(request.addnew, genUTXOs(self.blockchain.blocks)) != False:
            self.localTxList.append(request.addnew)
            return blockchain_pb2.addNewResponse(addresult='add NewTransaction success!')
        else:
            return blockchain_pb2.addNewResponse(addresult='Not valid transaction!')
    # Receive the miner's query request and return the complete blockchain (list format)
    # def QueryBlockchain(self, request, context):
    #     response = blockchain_pb2.QueryBlockchainResponse()
    #     # Question: What does this for loop statement do? How is his data structure transformed?
    #     for block in self.blockchain.blocks:
    #         pb2_block = blockchain_pb2.Block(transaction=block.Transaction, hash=block.Hash,
    #                                          prevBlockHash=block.PrevBlockHash)
    #         response.blocks.append(pb2_block)
    #     return response

    # For step 3
    # def QueryBlock(self, request, context):
    #     response = blockchain_pb2.QueryBlockResponse()
    #
    #     block = self.blockchain.blocks[-1]
    #     response = blockchain_pb2.Block(transaction=block.Transaction, hash=block.Hash,
    #                                     preBlockHash=block.PrevBlockHash)
    #     return response


# server setting
def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    blockchain_pb2_grpc.add_BlockChainServicer_to_server(BlockchainServer(), server)
    server.add_insecure_port('127.0.0.1:' + port)
    server.start()
    print("blockchain-demo started, listening on " + port)
    server.wait_for_termination()


def saveBlocktoDB(mycol, block):
    b_dict = block2Dict(block)
    mydict = {"_id": block.index, "block info": b_dict}

    x = mycol.insert_one(mydict)


def getBlockchainFromDB(mycol, blockchain):
    # db_blockchain = []
    for x in mycol.find():
        db_block = dict2Block(x['block info'])
        # db_blockchain.append(db_block)
        blockchain.append(db_block)

    # return db_blockchain


def getBlockFromDB(mycol, blockIndex):
    myquery = {"_id": blockIndex}

    mydoc = mycol.find(myquery)
    block = None

    for x in mydoc:
        block = dict2Block(x['block info'])

    return block


def txList2msg(tx_list):
    msgTxList = []
    # msgTxList = ''
    for tx in tx_list:
        msgTxInList = []
        msgTxOutList = []

        for txIn in tx.TxInList:
            msgTxIn = blockchain_pb2.TxIn(TxOut=txIn.TxOutId, TxOutIndex=txIn.TxOutIndex, signature=txIn.signature)
            msgTxInList.append(msgTxIn)

        for txOut in tx.TxOutList:
            # TODO
            if not isinstance(txOut.address, str):
                addr = txOut.address.to_pem().decode()
                # print(addr)
            else:
                addr = txOut.address
            msgTxOut = blockchain_pb2.TxOut(address=addr, amount=txOut.amount)
            msgTxOutList.append(msgTxOut)

        msgTx = blockchain_pb2.Transaction(TxId=tx.TxId, TxInList=msgTxInList, TxOutList=msgTxOutList)
        msgTxList.append(msgTx)

    return msgTxList


def msg2txList(msgtxList):
    txList = []

    for msgtx in msgtxList:
        txInList = []
        txOutList = []

        for msgTxIn in msgtx.TxInList:
            txIn = TxIn(msgTxIn.TxOutId, msgTxIn.TxOutIndex, msgTxIn.signature)
            txInList.append(txIn)

        for msgTxOut in msgtx.TxOutList:
            addr = VerifyingKey.from_pem(msgTxOut.address.encode())
            # print('msg2Txout', msgTxOut.address)
            txOut = TxOut(addr, msgTxOut.amount)
            txOutList.append(txOut)

        tx = Transaction(txInList, txOutList)
        print("old", tx.TxId)
        tx.setTxID(msgtx.TxId)
        print("new set tx id", tx.TxId)
        # print()
        txList.append(tx)
        # if tx.TxId == msgtx.TxId:
        #     txList.append(tx)
        #     continue
        # else:
        #     print("Transaction error")

    return txList


def UTXOs2msg(UTXOs):
    msgkey_list = []
    msgOwner_list = []
    msgAmount_list = []
    for k, v in UTXOs.items():
        msgkey_list.append(k)

        # addr = str(v.address.to_pem())

        # msgAmount = blockchain_pb2.TxOut(amount=)
        # print("v.amount",v.amount)
        msgAmount_list.append(v.amount)

        if not isinstance(v.address, str):
            addr = v.address.to_pem().decode()
            # print(addr)
        else:
            addr = v.address
        hash = hashlib.sha256((addr).encode("utf-8")).hexdigest()
        hash_result = hashlib.sha256(hash.encode("utf-8")).hexdigest()
        msgOwner_list.append(hash_result)

    msgUTXOs = blockchain_pb2.UTXOs(key=msgkey_list, amount=msgAmount_list, owner=msgOwner_list)

    return msgUTXOs


def block2Dict(block):
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
    txIn_dict = {'TxOutId': txIn.TxOutId, 'TxOutIndex': txIn.TxOutIndex, 'signature': txIn.signature}
    return txIn_dict


def txOut2Dict(txOut):
    if not isinstance(txOut.address, str):
        addr = txOut.address.to_pem().decode()
        # print("Before save txOut",txOut)
        # print("Before save txOut address",txOut.address)
        # print()
    else:
        addr = txOut.address
    txOut_dict = {'address': addr, 'amount': txOut.amount}
    return txOut_dict


def dict2Block(b_dict):
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
    TxId = tx_dict['TxId']
    TxInList = tx_dict['TxInList']
    TxOutList = tx_dict['TxOutList']

    tx = Transaction(dict2TxIn(TxInList), dict2TxOut(TxOutList))
    tx.setTxID(TxId)

    # print("new txid", tx.TxId)
    # print("old txid", TxId)
    # print(tx.TxInList)
    # print(tx.TxOutList[0].address)
    # print(tx.TxOutList[0])
    return tx
    # if tx.TxId == TxId:
    #     return tx
    # else:
    #     print("Invalid transaction")


def dict2TxIn(txInList_dict):
    TxInList = []

    for txIn in txInList_dict:
        TxOutId = txIn['TxOutId']
        TxOutIndex = txIn['TxOutIndex']
        signature = txIn['signature']

        newtxIn = TxIn(TxOutId, TxOutIndex, signature)
        TxInList.append(newtxIn)
    return TxInList


def dict2TxOut(txOutList_dict):
    TxOutList = []

    for txOut in txOutList_dict:
        address = str(txOut['address'])
        # print("new addr",type(address))
        # print(address.encode())
        vk = VerifyingKey.from_pem(address.encode())
        # print("addr", vk)

        amount = txOut['amount']

        newtxOut = TxOut(vk, amount)
        TxOutList.append(newtxOut)
    return TxOutList


# run the server
if __name__ == '__main__':
    logging.basicConfig()
    port = "50051"
    serve(port)
