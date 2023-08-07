from abc import ABC, abstractmethod
from DataBaseMain import 

class DataLogger(ABC):

    @abstractmethod
    def getData(self):
        pass

    @abstractmethod
    def saveToDatabase(self, database: Database):
        pass

class GithubIssuesLogger(DataLogger):

    def __init__(self):
        pass