import os
from dotenv import load_dotenv

from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.callbacks import OpenAICallbackHandler

#Load environment variables
load_dotenv()

#Text Embedding 3 Small
def model_embedding():
    """
    Initializes an embedding model using Azure OpenAI Embeddings with environment 
    variables for deployment, endpoint, and API key.

    Returns:
        model (AzureOpenAIEmbeddings): An instance configured for text embedding.
    """
    model = AzureOpenAIEmbeddings(
        azure_deployment= os.getenv("AZURE_DEPLOYMENT_EMBBEDING"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    )
    
    return model

#GPT 4o
def ChatGPT():
    """
    Initializes a GPT model for chat using Azure OpenAI with environment variables
    for deployment, endpoint, API key, and API version. Configured with a callback handler 
    for tracking OpenAI API usage.

    Returns:
        model (AzureChatOpenAI): An instance configured for chat using the GPT model.
    """
    model = AzureChatOpenAI(
        temperature = 0.0,
        azure_deployment= os.getenv("AZURE_DEPLOYMENT_GPT4"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_GPT4"),
        openai_api_key = os.getenv("AZURE_OPENAI_API_KEY_GPT4"),
        openai_api_version = os.getenv("OPENAI_API_VERSION_GPT4"),
        callbacks = [OpenAICallbackHandler()])
    
    return model