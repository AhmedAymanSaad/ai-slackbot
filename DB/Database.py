from abc import ABC, abstractmethod
from pymongo import MongoClient
import os
from dotenv import find_dotenv, load_dotenv

class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass


    
class MongoDBHandler(Database):
    def __init__(self, cluster_url, database_name='your_database_name', username=None, password=None):
        self.cluster_url = cluster_url
        self.database_name = database_name
        self.username = username
        self.password = password
        self.client = None
        self.db = None

    def connect(self):
        try:
            connection_string = f'mongodb+srv://{self.username}:{self.password}@{self.cluster_url}/{self.database_name}'
            self.client = MongoClient(connection_string)
            self.db = self.client[self.database_name]
            print("Connected to MongoDB cluster successfully!")
        except Exception as e:
            print("Failed to connect to MongoDB:", e)

    def insert_document(self, collection_name, data):
        try:
            collection = self.db[collection_name]
            inserted_document = collection.insert_one(data)
            print('Inserted document ID:', inserted_document.inserted_id)
        except Exception as e:
            print("Failed to insert document:", e)


    def disconnect(self):
        try:
            if self.client:
                self.client.close()
                print("Disconnected from MongoDB.")
        except Exception as e:
            print("Error while disconnecting:", e)



    
