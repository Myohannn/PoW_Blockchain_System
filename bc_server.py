from concurrent import futures
import logging
import grpc
import grpc_utils.blockchain_pb2 as blockchain_pb2
import grpc_utils.blockchain_pb2_grpc as blockchain_pb2_grpc
from bc_define import *
from ECDSA import *
import pymongo


class BlockchainServer(blockchain_pb2_grpc.BlockChainServicer):
    def __init__(self):
        self.blockchain = NewBlockchain()
        self.localTxList = []
        self.clientIndex = '-1'

        self.publicKey = ''
        self.privateKey = ''
        self.publicKey_list = []

        # database setup
        myClient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = myClient["BlockchainDB"]
        self.col = None

    def initTxList(self, request, context):
        # initialize transaction list (Add coinbase transaction)
        self.localTxList = []
        coinbaseTx = setCoinBaseTx(self.publicKey)
        self.localTxList.append(coinbaseTx)
        response = blockchain_pb2.InitTxListResponse(message="Tx list init")
        return response

    def addNewBlock(self, request, context):
        # Receive miner's transaction and expected hash.
        # And return the result or the address of the new block to the miner.
        current_blockIndex = len(self.blockchain.blocks)
        previousBlockHash = self.blockchain.blocks[current_blockIndex - 1].hash
        nonce = request.nonce
        hash_code, block = addNewBlock(self.blockchain.blocks, self.localTxList, current_blockIndex, previousBlockHash,
                                       nonce, self.publicKey)

        if block:
            # new block found
            self.blockchain.blocks.append(block)
            saveBlocktoDB(self.col, block)
            print(f"Block {block.index} saved in to storage!")

            print("Blockchain updated: ")
            for i in range(len(self.blockchain.blocks)):
                print("block " + str(i) + ":")
                print('block hash = ' + self.blockchain.blocks[i].hash)
            print()

            pb2_block = blockchain_pb2.Block(index=block.index, hash=block.hash, prevBlockHash=block.prevBlockHash,
                                             rootHash=block.rootHash, difficulty=block.difficulty, nonce=block.nonce,
                                             timestamp=block.timestamp,
                                             transactionList=txList2msg(block.transactionList))

            return blockchain_pb2.AddBlockResponse(hash=hash_code, newBlock=pb2_block)
        else:
            return blockchain_pb2.AddBlockResponse(hash=hash_code, newBlock=None)

    def receiveBlock(self, request, context):
        # receive a block broadcast by others
        print(request.message)
        msgBlock = request.newBlock
        block = Block(msgBlock.index, msgBlock.hash, msgBlock.prevBlockHash, msgBlock.rootHash, msgBlock.difficulty,
                      msgBlock.nonce, msgBlock.timestamp)
        msgTxList = msgBlock.transactionList
        block.setTransactions(msg2txList(msgTxList))

        # Validate the block
        if isValidBlock(self.blockchain.blocks, block) or len(self.blockchain.blocks) == 1:
            print("Valid block")
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
            msg = f"Here is block {block_idx}"
            response = blockchain_pb2.receiveMessageResponse(message=msg, newBlock=pb2_block)
            return response

    # check channel aliveness
    def getState(self, request, context):
        if self.clientIndex == '-1':
            self.clientIndex = request.message
            sk, vk = loadKey(self.clientIndex)
            self.privateKey = sk
            self.publicKey = vk

            # get public key pair list from disk
            for i in range(4):
                self.publicKey_list.append(loadKey(i))
            col_name = f'miner{self.clientIndex}'
            self.col = self.mydb[col_name]

        message = f'Miner {self.clientIndex} alive!'
        response = blockchain_pb2.getStateResponse(message=message)
        return response

    def getUTXOs(self, request, context):
        utxos = genUTXOs(self.blockchain.blocks).utxos
        print("UTXOs:::::", utxos)
        msgUTXOs = UTXOs2msg(utxos)
        response = blockchain_pb2.getUTXOsResponse(utxos=msgUTXOs)
        return response

    def QueryDB(self, request, context):
        print("Query DB request:", request.message)
        getBlockchainFromDB(self.col, self.blockchain.blocks)

        print("Blockchain from DB: ")
        for i in range(len(self.blockchain.blocks)):
            print("block " + str(i) + ":")
            print('block hash = ' + self.blockchain.blocks[i].hash)
        print()

        return blockchain_pb2.QueryDBResponse(message='Blockchain reading complete!')

    def addNewTransaction(self, request, context):
        if isValidTx(request.addnew, genUTXOs(self.blockchain.blocks)):
            self.localTxList.append(request.addnew)
            return blockchain_pb2.addNewTransactionResponse(addresult='add NewTransaction success!')
        else:
            return blockchain_pb2.addNewTransactionResponse(addresult='Not valid transaction!')


# server setting
def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    blockchain_pb2_grpc.add_BlockChainServicer_to_server(BlockchainServer(), server)
    server.add_insecure_port('127.0.0.1:' + port)
    server.start()
    print("blockchain-demo started, listening on " + port)
    server.wait_for_termination()


def txList2msg(tx_list):
    # convert transactionList obj to gRPC message
    msgTxList = []
    for tx in tx_list:
        msgTxInList = []
        msgTxOutList = []

        for txIn in tx.TxInList:
            msgTxIn = blockchain_pb2.TxIn(TxOut=txIn.TxOutId, TxOutIndex=txIn.TxOutIndex, signature=txIn.signature)
            msgTxInList.append(msgTxIn)

        for txOut in tx.TxOutList:
            if not isinstance(txOut.address, str):
                addr = txOut.address.to_pem().decode()
            else:
                addr = txOut.address
            msgTxOut = blockchain_pb2.TxOut(address=addr, amount=txOut.amount)
            msgTxOutList.append(msgTxOut)

        msgTx = blockchain_pb2.Transaction(TxId=tx.TxId, TxInList=msgTxInList, TxOutList=msgTxOutList)
        msgTxList.append(msgTx)

    return msgTxList


def UTXOs2msg(UTXOs):
    # convert UTXO obj to gRPC message
    msgkey_list = []
    msgOwner_list = []
    msgAmount_list = []
    for k, v in UTXOs.items():
        msgkey_list.append(k)
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


# run the server
if __name__ == '__main__':
    logging.basicConfig()
    port = "50051"
    serve(port)
