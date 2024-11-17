import time
import streamlit as st

from utilities.memory import chat_to_memory, write_chat_history
from utilities.model import model_embedding, ChatGPT
from utilities.preprocess import store_in_vector_database, save_uploaded_file, process_pdf
from langchain_community.vectorstores import FAISS

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Config Page
st.set_page_config(
    page_title="EDTS Chatbot",
    page_icon="assets/favicon.ico")

# Function QnA Initialization
def qna_with_generative(user_question, chat_history):
    """
    Function:
    Args:
    
    Returns:
    """

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
    
    # FILL THIS BLANK (Hint: Intialize Chat GPT)
    model = " ... "
    vector_store = FAISS.load_local("./database/faiss_index", model_embedding(), allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    history_aware_retriever = create_history_aware_retriever(model, retriever, contextualize_prompt_template)

    f = open("system_prompt_pdf.txt", "r")
    text_system_prompt = f.read()

    # FILL THIS BLANK (Hint: Just pass the value of text_system_prompt)
    # But before that you could edit the prompt in system_prompt_pdf.txt with you customize prompt
    system_prompt = (
        " ... " + "\nYour answer must use the same language as the language in the latest question \nHere is the context to help you answer:\n{context}"
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

    output_prompt = rag_chain.invoke({"input":user_question, "chat_history":memory})

    memory_to_write = []
    memory_to_write.append(
        {"input": user_question}
    )

    memory_to_write.append(
        {"output": output_prompt["answer"]}
    )
    
    return output_prompt, memory_to_write

# Stream Response
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
        yield "\n\n"  
        time.sleep(0.2)  # Add delay between paragraphs

# Initialize file processed flag in session state to track processing status
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

# Initialize list_memory in session state to track memory across interactions
if "list_memory" not in st.session_state:
    st.session_state.list_memory = []

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
    if len(pdf_doc) != 0:
        list_file_uploaded = save_uploaded_file(pdf_doc)

        # Progress bar for detailed processing feedback
        progress_text = "Processing PDF files..."
        progress_bar = st.progress(0, text=progress_text)

        # Step 1: Extract PDF content
        extracted_pdf = process_pdf(list_file_uploaded)
        progress_bar.progress(33, text="Extracted PDF content...")

        # Step 2: Store in vector database
        store_in_vector_database(extracted_pdf)
        progress_bar.progress(66, text="Stored data in vector database...")

        # Step 3: Complete
        progress_bar.progress(100, text="Completed processing files.")
        
        # Set processed flag to True after successful processing and update status message
        st.session_state.file_processed = True
        status_message.success("Document processed successfully! You can now interact with the assistant.", icon="✅")

        for file in list_file_uploaded["pdf_files"]:
            print(f"File: {file.split('/')[-1]}")          
    
        # Separator line
        st.divider()  # Alternatively, you can use st.write("----") for a custom separator
    
    else:
        st.error("Please upload a file before submitting.")

#Message Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Respond to user input only if the document is processed
if st.session_state.file_processed:
    if user_question := st.chat_input("Your Question"):
        st.chat_message("user").markdown(user_question)
        st.session_state.messages.append({"role": "user", "content": user_question})

        # Generate assistant response and memory update
        with st.spinner("Assistant is thinking..."):
            response, memory_chat = qna_with_generative(user_question,  st.session_state.list_memory)
            st.session_state.list_memory.append(memory_chat[0])
            st.session_state.list_memory.append(memory_chat[1])
            write_chat_history(st.session_state.list_memory)
        
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
    st.markdown(
        """
        <div style="background-color: #EEF0F4; padding: 10px 15px; border-radius: 5px; text-align: center">
            Please <strong>upload and process the document</strong> before asking a question.
        </div>
        """, 
        unsafe_allow_html=True
    )

   
