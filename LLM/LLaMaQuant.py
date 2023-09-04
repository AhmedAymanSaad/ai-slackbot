from LLM.LLmMain import LLM

from langchain import LLMChain, PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import LlamaCpp

class LLaMaQuant(LLM):
    modelPath = "/home/ahmedaymansaad/.cache/huggingface/hub/models--TheBloke--Llama-2-7B-Chat-GGML/snapshots/b616819cd4777514e3a2d9b8be69824aca8f5daf/llama-2-7b-chat.ggufv3.q4_K_M.bin"
    nGpuLayers = 1
    nBatch = 512
    nCtx = 4096
    nThreads = 2
    callbackManager = CallbackManager([StreamingStdOutCallbackHandler()])

    def __init__(self):
        self.InitializeModel()
        testStatus = self.quickTestModel()
        if testStatus == False:
            raise Exception("Model failed to pass quick test")


    def InitializeModel(self):
        self.llm = LlamaCpp(
            model_path=self.modelPath,
            callback_manager=self.callbackManager,
            verbose=True,
            n_ctx=self.nCtx,
            n_batch= self.nBatch,
            n_gpu_layers=self.nGpuLayers,
            f16_kv=True,
            streaming = True,
            seed = 0,
        )

    def quickTestModel(self):
        output = self.llm("Q: What is the capital of France? A:", stop=["Q:", "\n"],echo=False)
        if output.lower().find("paris") != -1:
            print("Test passed")
            return True
        else:
            print("Test failed")
            print(output)
            return False
        
    def respond(self, question, context):
        template = """
        <<SYS>>
        You are Sil, a friendly chatbot assistant that responds conversationally to users' questions.
        Keep the answers short, Lower character count answers are preferred.
        If you do not know the answer to a question say that you do not know, don't try to guess.
        You have context that you can use to answer questions, if the context is not relevant to the question, you can ignore it.
        All information in the context is public information, you can use it to answer questions.
        Context: 
        
        {context}

        <</SYS>>
        [INST]

        Question: {question}

        [/INST]"""
        prompt = PromptTemplate(template=template, input_variables=["question", "context"])

        llm_chain = LLMChain(prompt=prompt, llm=self.llm)
        output = llm_chain({'question':question,'context':context})
        print(output)
        return output["text"]
        