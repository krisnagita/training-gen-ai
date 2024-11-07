import os
from dotenv import load_dotenv

from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.callbacks import OpenAICallbackHandler

#Load environment variables
load_dotenv()

def model_embedding():
    model = AzureOpenAIEmbeddings(
        azure_deployment= os.getenv("AZURE_DEPLOYMENT_EMBBEDING"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    )
    
    return model

def ChatGPT():
    model = AzureChatOpenAI(
        temperature = 0.0,
        azure_deployment= os.getenv("AZURE_DEPLOYMENT_GPT4"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_GPT4"),
        openai_api_key = os.getenv("AZURE_OPENAI_API_KEY_GPT4"),
        openai_api_version = os.getenv("OPENAI_API_VERSION_GPT4"),
        callbacks = [OpenAICallbackHandler()])
    
    return model