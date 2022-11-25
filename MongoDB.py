from bc_server import *

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["BlockchainDB"]

# drop database
for i in range(10):
    mycol = mydb[f"miner{i}"]
    mycol.drop()

# print database
# for x in mycol1.find():
#     print(x)
#
# print()
#
# for x in mycol2.find():
#     print(x)
