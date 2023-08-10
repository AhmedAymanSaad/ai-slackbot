from abc import ABC, abstractmethod
from pymongo import MongoClient
import os
from dotenv import find_dotenv, load_dotenv

class Database(ABC):
    @abstractmethod
    def Connect(self):
        pass

    @abstractmethod
    def Disconnect(self):
        pass


    
class MongoDBHandler(Database):
    def __init__(self, cluster_url, database_name='your_database_name', username=None, password=None):
        self.cluster_url = cluster_url
        self.database_name = database_name
        self.username = username
        self.password = password
        self.client = None
        self.db = None

    def Connect(self):
        try:
            connection_string = f'mongodb+srv://{self.username}:{self.password}@{self.cluster_url}/{self.database_name}'
            self.client = MongoClient(connection_string)
            self.db = self.client[self.database_name]
            print("Connected to MongoDB cluster successfully!")
        except Exception as e:
            print("Failed to connect to MongoDB:", e)

    def InsertDocument(self, collection_name, data):
        try:
            collection = self.db[collection_name]
            inserted_document = collection.insert_one(data)
            print('Inserted document ID:', inserted_document.inserted_id)
        except Exception as e:
            print("Failed to insert document:", e)

    def insert_documents(self, collection_name, data):
        try:
            collection = self.db[collection_name]
            inserted_documents = collection.insert_many(data)
            print('Inserted documents IDs:', inserted_documents.inserted_ids)
        except Exception as e:
            print("Failed to insert documents:", e)

    def load_all_documents(self, collection_name):
        try:
            collection = self.db[collection_name]
            documents = collection.find()
            return documents
        except Exception as e:
            print("Failed to load documents:", e)


    def Disconnect(self):
        try:
            if self.client:
                self.client.close()
                print("Disconnected from MongoDB.")
        except Exception as e:
            print("Error while disconnecting:", e)



    
