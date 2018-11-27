import pymongo
client = pymongo.MongoClient("localhost", 27017)
db = client.wealth
print(db.name)
print (db.testNLP)
db.testNLP.insert_one({"x": 10}).inserted_id
db.testNLP.insert_one({"x": 8}).inserted_id
print(db.testNLP.find_one())
for item in db.testNLP.find():
    print(item["x"])
db.testNLP.create_index("x")
for item in db.testNLP.find().sort("x", pymongo.ASCENDING):
    print(item["x"])