#Import necessary libraries
import os
from dotenv import load_dotenv

from utilities.memory import chat_to_memory, write_chat_history
from utilities.model import model_embedding, ChatGPT
from utilities.preprocess import get_pdf_text, store_in_vector_database, save_uploaded_file, process_pdf_in_dir
from langchain_community.vectorstores import FAISS

from langchain.prompts import (ChatPromptTemplate, MessagesPlaceholder)
from langchain.chains import (create_history_aware_retriever, create_retrieval_chain)
from langchain.chains.combine_documents import create_stuff_documents_chain

import streamlit as st

def qna_with_generative(user_question, input_language, chat_history):
    if input_language == "en":
        language = "English"
    elif input_language == "id":
        language = "Bahasa Indonesia"
    
    if len(chat_history) == 0:
        chat_history = []
        memory= chat_to_memory([{"input":"", "output":""}])
    else:
        memory = chat_to_memory(chat_history)
    
    contextualize_system_prompt = (
    """
        Given a chat history and the latest user question which might reference context in the chat history, 
        Formulate a standalone question which can be understood 
        Without the chat history. Do NOT answer the question, Just reformulate it if needed and otherwise return it as is
    """
    )

    contextualize_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    model = ChatGPT()
    vector_store = FAISS.load_local("./database/faiss_index", model_embedding(), allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.35})

    history_aware_retriever = create_history_aware_retriever(model, retriever, contextualize_prompt_template)

    f = open("system_prompt.txt", "r")
    text_system_prompt = f.read()

    system_prompt = (
        text_system_prompt.replace("language_here", language) + "\nHere is the context to help you answer:\n{context}"
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    qna_chain = create_stuff_documents_chain(model, prompt_template)

    rag_chain = create_retrieval_chain(history_aware_retriever, qna_chain)

    output_prompt = rag_chain.invoke({"input":user_question, "chat_history":memory, "language":language})

    chat_history.append(
        {"input": user_question}
    )

    chat_history.append(
        {"output": output_prompt["answer"]}
    )
    
    return output_prompt, chat_history

# st.warning('You must upload document before asking the AI-assistant', icon="⚠️")
# pdf_doc = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", 
#                             accept_multiple_files=True, type=["pdf"])

# if st.button("Submit & Process"):
#     with st.spinner("Processing..."):
#         if pdf_doc is not None:
#             list_file_uploaded = save_uploaded_file(pdf_doc)
#             extracted_pdf = process_pdf_in_dir(list_file_uploaded)
#             store_in_vector_database(extracted_pdf)
#             print(list_file_uploaded)
#             st.success("File saved successfully at folder Database (uploaded_file) for files and (faiss_index) for vector database")
#             #Welcoming message

#         for file in list_file_uploaded:
#             print(f"File: {file}")

        
#     st.write("-------")

#     welcoming_message = "Hello! You can ask me anything that related to document you've upload"
#     st.chat_message("ai").markdown(welcoming_message)

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# #For first chat memory intialization
# list_memory = []

# # React to user input
# if user_question := st.chat_input("Your Question"):
#     st.chat_message("user").markdown(user_question)
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": user_question})


#     response, memory_chat = qna_with_generative(user_question, "en", list_memory)
#     write_chat_history(memory_chat)

#     with st.chat_message("assistant"):
#          with st.spinner("Thinking..."):
#              st.markdown(response["answer"])
    
#     # Add assistant response to chat history
#     st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

import time

# Function to simulate streamed response
# def response_streamer(response_text):
#     for word in response_text.split():
#         yield word + " "
#         time.sleep(0.05)  # Delay between words for streaming effect

def response_streamer(response_text):
    """
    Stream a well-formatted response with a slight delay between each word.
    This will ensure that the answer is printed cleanly, maintaining the original structure.
    """
    paragraphs = response_text.split("\n\n")  # Break by paragraphs
    for paragraph in paragraphs:
        words = paragraph.split()  # Split each paragraph into words
        for word in words:
            yield word + " "
            time.sleep(0.05)  # Adjust the typing speed if needed
        yield "\n\n"  # Add newlines between paragraphs
        time.sleep(0.2)  # Add delay between paragraphs

# Initialize file processed flag in session state to track processing status
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

# Placeholder for warning/success message
status_message = st.empty()

# Display warning if file is not yet processed, or success if already processed
if st.session_state.file_processed:
    status_message.success("Document processed successfully! You can now interact with the assistant.", icon="✅")
else:
    status_message.warning("You must upload and submit a document before asking the AI assistant.", icon="⚠️")

# File uploader
pdf_doc = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", 
                           accept_multiple_files=True, type=["pdf"])

# Process button functionality
if st.button("Submit & Process"):
    if pdf_doc is not None:
        list_file_uploaded = save_uploaded_file(pdf_doc)

        # Progress bar for detailed processing feedback
        progress_text = "Processing PDF files..."
        progress_bar = st.progress(0, text=progress_text)

        # Step 1: Extract PDF content
        extracted_pdf = process_pdf_in_dir(list_file_uploaded)
        progress_bar.progress(33, text="Extracted PDF content...")

        # Step 2: Store in vector database
        store_in_vector_database(extracted_pdf)
        progress_bar.progress(66, text="Stored data in vector database...")

        # Step 3: Complete
        progress_bar.progress(100, text="Completed processing files.")
        
        # Set processed flag to True after successful processing and update status message
        st.session_state.file_processed = True
        status_message.success("Document processed successfully! You can now interact with the assistant.", icon="✅")

        for file in list_file_uploaded:
            print(f"File: {file}")
            
    else:
        st.error("Please upload a file before submitting.")

# Separator line
st.divider()  # Alternatively, you can use st.write("----") for a custom separator

# Initialize chat history if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initialize memory list for first chat memory
list_memory = []

# Respond to user input only if the document is processed
if st.session_state.file_processed:
    if user_question := st.chat_input("Your Question"):
        st.chat_message("user").markdown(user_question)
        st.session_state.messages.append({"role": "user", "content": user_question})

        # Generate assistant response and memory update
        response, memory_chat = qna_with_generative(user_question, "en", list_memory)
        write_chat_history(memory_chat)

        # Display assistant response as streamed text
        with st.chat_message("assistant"):
            response_container = st.empty()
            streamed_response = ""
            for chunk in response_streamer(response["answer"]):
                streamed_response += chunk
                response_container.markdown(streamed_response)

        # Save assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

else:
    # st.warning("Chatbox will be shown after you upload document")

    st.markdown(
        """
        <div style="background-color: #EEF0F4; padding: 10px 15px; border-radius: 5px; text-align: center">
            Please <strong>upload and process the document</strong> before asking a question.
        </div>
        """, 
        unsafe_allow_html=True
    )