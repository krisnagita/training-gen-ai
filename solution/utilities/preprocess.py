import os
import base64
from langchain_core.documents import Document
from unstructured.partition.pdf import partition_pdf
from .model import model_embedding
from langchain_community.vectorstores import FAISS
from concurrent.futures import ThreadPoolExecutor
from langchain_community.document_loaders import PyPDFLoader
import cv2


def get_pdf_text(pdf_path):
    """
    Extracts text and metadata from a PDF and returns them as Document objects using Unstructured.

    Args:
        pdf_path (str): Path to the PDF file to process.

    Returns:
        extracted_pdf (list): A list of `Document` objects containing page content and metadata for each PDF page.
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

def get_pdf_text_pypdf(pdf_path):
    """
    Extracts text and metadata from a PDF and returns them as Document objects using PyPDFLoader.

    Args:
    pdf_path (str): Path to the PDF file to process.

    Returns:
    extracted_pdf (list): A list of `Document` objects containing page content and metadata for each PDF page.
    """
    loader = PyPDFLoader(pdf_path)
    extracted_pdf = []
    
    for page in loader.load():
        extracted_pdf.append(page)
    
    return extracted_pdf


def store_in_vector_database(extracted_pdf):
    """
    Stores extracted PDF data in a FAISS vector database.

    Args:
        extracted_pdf (list): List of `Document` objects to store in the vector database.

    Returns:
        None
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
    Saves uploaded files (PDF and JPG) to respective directories, resizing JPG images as needed.

    Args:
        uploaded_files (list): List of uploaded files with `.name` and `.getbuffer()` attributes.

    Returns:
        saved_paths (dict): Paths of saved files, with separate lists for "pdf_files" and "jpg_files".
    """
    # Create the temporary folder if it doesn't exist
    saved_paths = {
        "pdf_files": [],
        "jpg_files": []
    }

    # Ensure directories exist
    pdf_dir = "./database/uploaded_file"
    jpg_dir = "./database/uploaded_image"

    for file in uploaded_files:
        if file.name.lower().endswith(".pdf"):
            file_path = os.path.join(pdf_dir, file.name)
            saved_paths["pdf_files"].append(file_path)
        elif file.name.lower().endswith(".jpg"):
            file_path = os.path.join(jpg_dir, file.name)
            saved_paths["jpg_files"].append(file_path)
        else:
            # Optionally, handle unsupported file types
            print(f"Unsupported file type: {file.name}")
            continue

        # Write the file to the appropriate directory
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        if file.name.lower().endswith(".jpg"):
            # image = Image.open(file_path)
            image= cv2.imread(file_path)
            new_image = cv2.resize(image, None, fx = 0.75, fy = 0.75)
            file_path_resize = os.path.join(jpg_dir, f"resize_{file.name}")
            cv2.imwrite(file_path_resize, new_image)

    return saved_paths

def process_pdf(uploaded_files):
    """
    Processes each uploaded PDF file to extract its content.

    Args:
        uploaded_files (dict): Dictionary with "pdf_files" key, containing a list of PDF file paths.

    Returns:
        results (list): A list of extracted text data for each PDF.
    """
    
    args = [(file) for file in uploaded_files["pdf_files"]]
    
    # Use ThreadPoolExecutor to process all PDFs simultaneously
    with ThreadPoolExecutor(max_workers=3) as executor:
        
        # Map the load_pdf_data function to all PDF files with corresponding arguments
        # results = list(executor.map(get_pdf_text, args))
        results = list(executor.map(get_pdf_text_pypdf, args))
    
    return results

def image_to_base64(image_path):
    """
    Converts an image file to a base64-encoded string.

    Args:
        image_path (str): Path to the image file.

    Returns:
        image)base64 (str): Base64-encoded string representation of the image.
    """
    with open(image_path, "rb") as image:
         image_base64 = base64.b64encode(image.read()).decode("utf-8")

    return image_base64

def process_image(uploaded_files):
    """
    Processes each uploaded image file, converting it to a base64-encoded string.

    Args:
        uploaded_files (dict): Dictionary with "jpg_files" key, containing a list of image file paths.

    Returns:
        results (list): A list of base64-encoded strings for each image.
    """
    
    args = [(file) for file in uploaded_files["jpg_files"]]
    
    # Use ThreadPoolExecutor to process all Image simultaneously
    with ThreadPoolExecutor(max_workers=3) as executor:
        
        # Map the load_pdf_data function to Image with corresponding arguments
        results = list(executor.map(image_to_base64, args))
    
    return results