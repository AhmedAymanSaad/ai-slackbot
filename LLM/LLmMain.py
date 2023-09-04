from abc import ABC, abstractmethod

class LLM (ABC):
    @abstractmethod
    def InitializeModel(self):
        pass

    @abstractmethod
    def quickTestModel(self):
        pass

    @abstractmethod
    def respond(self, text):
        pass

