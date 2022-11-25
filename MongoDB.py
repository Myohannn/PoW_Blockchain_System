import pymongo
from bc_server import dict2Block
from bc_server import *

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["BlockchainDB"]

mycol1 = mydb["miner0"]
mycol2 = mydb["miner1"]
mycol3 = mydb["miner2"]
mycol4 = mydb["miner3"]
#
mycol1.drop()
mycol2.drop()
mycol3.drop()
mycol4.drop()

for x in mycol1.find():
    print(x)

print()

for x in mycol2.find():
    print(x)

#
# block = getBlockFromDB(mycol,2)
# print(block.index)
# print(block.hash)
# # print(block.prevBlockHash)
# # print(block.rootHash)

# print(block.transactionList)

#
# db_blockchain = []
# for x in mycol.find():
#     db_block = dict2Block(x['block info'])
#     db_blockchain.append(db_block)
# print(db_blockchain)
#
# # # mycol.drop()
# #
# # for x in mycol.find():
# #     print(x[])
# myquery = {"_id": 1}
#
# mydoc = mycol.find(myquery)
# block = None
#
# for x in mydoc:
#     print(x['block info'])

# myquery = { "_id": 11 }
#
# mydoc = mycol.find(myquery)
#
#
# for x in mydoc:
#   print(x['address'])
# print(mydb.list_collection_names())
