from __future__ import print_function

import logging
import random
import time
import grpc

import grpc_utils.blockchain_pb2 as blockchain_pb2
import grpc_utils.blockchain_pb2_grpc as blockchain_pb2_grpc
import ECDSA


# The client initialization


class bc_Miner:
    def __init__(self, minerIndex):

        self.port_list = []
        self.miner_index = minerIndex
        self.localport = ''
        self.latestBlockIndex = 1
        self.localBlockIndex = 0

        # self.initMiner()

    def run(self):
        self.initMiner()
        self.QueryDB()

        local_channel = grpc.insecure_channel('localhost:' + self.localport)
        resposne = self.sendMessage(local_channel, 'Local index')
        self.localBlockIndex = int(resposne.message)
        self.latestBlockIndex = self.localBlockIndex

    def initMiner(self):
        f = open("portList.txt")
        line = f.readline()
        while line:
            self.port_list.append(line.replace('\n', ''))
            line = f.readline()
        f.close()

        # get key pair

        # update server side miner_index
        local_port = self.port_list[self.miner_index]
        local_channel = grpc.insecure_channel('localhost:' + local_port)
        stub = blockchain_pb2_grpc.BlockChainStub(local_channel)
        response = stub.getState(blockchain_pb2.getStateRequest(message=self.miner_index))
        print(response)

        self.localport = self.port_list[self.miner_index]

        # self.mining()

    def QueryDB(self):
        local_channel = grpc.insecure_channel('localhost:' + self.localport)
        stub = blockchain_pb2_grpc.BlockChainStub(local_channel)
        response = stub.QueryDB(blockchain_pb2.QueryDBRequest(message='Read blockchain from DB'))
        print("Query DB result:", response)

    def getLatestBlockIdx(self):
        index_list = self.broadcastMsg("Highest Index")

        # print("Live miner's latest block index", index_list)
        for idx in index_list:
            if int(idx.message) <= self.latestBlockIndex:
                # self.latestBlockIndex = self.localBlockIndex
                continue
            else:
                self.latestBlockIndex = int(idx.message)
                print("The highest index is:", idx.message)

    def broadcastMsg(self, message):
        channel_list = self.getAliveChannel(self.port_list)
        response_list = []

        # # for port in port_list:
        # #     channel = grpc.insecure_channel()
        # channel1 = grpc.insecure_channel('localhost:50051')
        # channel2 = grpc.insecure_channel('localhost:50052')
        # channel3 = grpc.insecure_channel('localhost:50053')
        #
        # channel_list = [channel2, channel3]

        for c in channel_list:
            try:
                response = self.sendMessage(c, message)
                response_list.append(response)
            except Exception as e:
                print("broadcastMsg err", e)
        return response_list

    def mining(self):
        nonce = 0
        while 1 == 1:
            if self.isMining():
                print("Start mining")
                self.mineBlock(nonce)
                nonce += 1
            else:
                print(f"Getting block {self.localBlockIndex}")
                self.getBlock(self.localBlockIndex)
                self.getLatestBlockIdx()
                # query next block

    def isMining(self):
        # check whether the mining should start mining
        local_channel = grpc.insecure_channel('localhost:' + self.localport)
        resposne = self.sendMessage(local_channel, 'Local index')
        self.localBlockIndex = int(resposne.message)
        self.getLatestBlockIdx()

        print("local:", self.localBlockIndex)
        print("latest:", self.latestBlockIndex)
        if self.localBlockIndex < self.latestBlockIndex:
            # query next block
            return False
        else:
            # start mining
            return True

    def mineBlock(self, nonce):
        # local_channel = implementations.insecure_channel('localhost', local_port)
        local_channel = grpc.insecure_channel('localhost:' + self.localport)
        stub = blockchain_pb2_grpc.BlockChainStub(local_channel)

        # initialize coinbase tx
        initTX = stub.initTxList(blockchain_pb2.InitTxListRequest(message="init transaction"))
        # print(initTX.message)

        tran_msg = f"This block was added by client {self.miner_index}."

        response = stub.addNewBlock(blockchain_pb2.AddBlockRequest(transaction=tran_msg, nonce=nonce))

        # print("trying nonce:", nonce)
        if response.hash == "Restart":
            nonce = 0
        elif response.hash != 'False':
            print("Add the block successfully. The nonce is " + str(nonce))
            print("New block address: " + response.hash)
            initTX = stub.initTxList(blockchain_pb2.InitTxListRequest(message="init transaction"))
            print(initTX.message)

            self.broadcastBlock(response.newBlock)
            nonce = 0

        # time.sleep(1)

        # print("Mining the next Block, Guessing the expected puzzle is " + str(nonce))
        # response = stub.addNewBlock(blockchain_pb2.AddBlockRequest(transaction=tran_msg, nonce=nonce))

    def sendMessage(self, channel, message):
        stub = blockchain_pb2_grpc.BlockChainStub(channel)

        # tran_msg = f"{self.miner_index} find a new Block!"
        response = stub.receiveMessage(blockchain_pb2.receiveMessageRequest(message=message))
        # print("client MSG:", response.message)
        return response

    def broadcastBlock(self, block):
        channel_list = self.getAliveChannel(self.port_list)

        for c in channel_list:
            try:
                self.sendBlock(c, block)
            except Exception as e:
                print("broadcastBlock err: ", e)

    def sendBlock(self, channel, block):
        stub = blockchain_pb2_grpc.BlockChainStub(channel)

        tran_msg = f"{self.miner_index} find a new Block!"
        response = stub.receiveBlock(blockchain_pb2.ReceiveBlockRequest(message=tran_msg, newBlock=block))
        print(response)

    def getAliveChannel(self, port_list):
        channel_list = []
        alive_miner = []
        for i, p in enumerate(port_list):
            if i == self.miner_index:
                continue
            channel = grpc.insecure_channel('localhost:' + p)

            try:
                grpc.channel_ready_future(channel).result(timeout=0.1)
            except:
                result = f"channel:{p} connect timeout"
            else:
                result = f"channel:{p} connect success"
                channel_list.append(channel)
                alive_miner.append(i)

        print(f"Miner {alive_miner} are alive")
        return channel_list

    def getUTXOs(self):
        local_channel = grpc.insecure_channel('localhost:' + self.localport)
        stub = blockchain_pb2_grpc.BlockChainStub(local_channel)
        response = stub.getUTXOs(blockchain_pb2.getUTXOsRequest(message="get UTXOs"))
        return response

    def broadcastNewTransaction(transaction):
        channel = grpc.insecure_channel('localhost:50052')
        localchannel = grpc.insecure_channel('localhost:50051')
        localstub = blockchain_pb2_grpc.BlockChainStub(localchannel)

        channel_list = [channel]
        successadd = 0

        for c in channel_list:
            stub = blockchain_pb2_grpc.BlockChainStub(c)
            if stub.addNewtransaction(
                    blockchain_pb2.addNewRequest(addnew=transaction)) == 'add NewTransaction success!':
                successadd += 1
        if successadd > 0:
            localstub.addNewtransaction(blockchain_pb2.addNewRequest(addnew=transaction))

    def getBlock(self, block_index):
        # get block message from other miner
        msg = f"Get Block:{block_index}"
        response_list = self.broadcastMsg(msg)
        # print("block response list", response_list)
        requeried_block = response_list[0].newBlock

        # add block into local blockchain
        local_channel = grpc.insecure_channel('localhost:' + self.localport)
        try:
            self.sendBlock(local_channel, requeried_block)
        except:
            print("Error get block")

    def getBlockInfo(self, block_index):
        msg = f"Get Block:{block_index}"
        local_channel = grpc.insecure_channel('localhost:' + self.localport)
        response = self.sendMessage(local_channel, msg)

        return response


if __name__ == '__main__':
    logging.basicConfig()

    miner = bc_Miner(0)
    miner.initMiner()
    # read from stroge and then start mining
    miner.mining()
