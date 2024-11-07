from langchain_core.documents import Document
from unstructured.partition.pdf import partition_pdf
from .model import model_embedding
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
import streamlit as st
import os
from concurrent.futures import ThreadPoolExecutor

def get_pdf_text(pdf_path):
    """
    Function:
    Args:

    Returns:
    
    """
    extracted_element =  partition_pdf(
        filename=pdf_path,
        extract_images_in_pdf=True,
        infer_table_structure=False,
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        strategy="fast",
        include_page_break = True
    )

    extracted_pdf = []
    for i in range(0, len(extracted_element)):
        data_metadata = extracted_element[i].metadata.to_dict()
        extracted_pdf.append(Document(page_content=extracted_element[i].text, metadata=data_metadata))
    
    return extracted_pdf

def store_in_vector_database(extracted_pdf):
    """
    Function:
    Args:

    Returns:
    
    """
    embedding = model_embedding()

    for i in range(len(extracted_pdf)):
        document = extracted_pdf[i]
        if i == 0:
            vector_store = FAISS.from_documents(document, embedding)
        else:
            vector_store_temp = FAISS.from_documents(document, embedding)
            vector_store.merge_from(vector_store_temp)

    vector_store.save_local("./database/faiss_index")


def save_uploaded_file(uploaded_files):
    """
    Function:
    Args:

    Returns:
    
    """
    # Create the temporary folder if it doesn't exist
    file_path_final = []
    for file in uploaded_files:
        file_path = os.path.join("./database/uploaded_file", file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
            file_path_final.append(file_path)
    
    return file_path_final

# Function to process all PDFs in a given directory
def process_pdf_in_dir(uploaded_files):
    
    # Prepare arguments for each PDF file
    args = [(file) for file in uploaded_files]
    
    # Use ThreadPoolExecutor to process all PDFs simultaneously
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Map the load_pdf_data function to all PDF files with corresponding arguments
        results = list(executor.map(get_pdf_text, args))
        # print(f"Document Text\n\n: {results}")
    
    return results








    





