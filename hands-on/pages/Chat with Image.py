import time
import streamlit as st

from utilities.memory import chat_to_memory, write_chat_history
from utilities.model import ChatGPT
from utilities.preprocess import save_uploaded_file, process_image

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.messages import HumanMessage

# Config Page
st.set_page_config(
    page_title="EDTS Chatbot",
    page_icon="assets/favicon.ico")

# Function QnA Initialization
def qna_with_generative(user_question, list_image_base64, chat_history):
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
    
    content = []
    for image_base64 in list_image_base64:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        })
    
    content.append({"type": "text", "text": user_question})

    f = open("system_prompt_image.txt", "r")
    text_system_prompt = f.read()

    # FILL THIS BLANK (Hint: Just pass the value of text_system_prompt)
    # But before that you could edit the prompt in system_prompt_pdf.txt with you customize prompt
    system_prompt = (
        " ... "+ "\nYour answer must use the same language as the language in the latest question \n"
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            HumanMessage(content),
        ]
    )

    # FILL THIS BLANK (Hint: Intialize Chat GPT)
    model = " ... "
    
    chain = prompt_template | model
   
    output_prompt = chain.invoke({"chat_history" : memory})

    memory_to_write = []
    memory_to_write.append(
        {"input": user_question}
    )

    memory_to_write.append(
        {"output": output_prompt.content}
    )
    
    return output_prompt, memory_to_write

# Stream Response
def response_streamer(response_text):
    paragraphs = response_text.split("\n\n")  # Break by paragraphs
    for paragraph in paragraphs:
        words = paragraph.split()  # Split each paragraph into words
        for word in words:
            yield word + " "
            time.sleep(0.05)  # Adjust the typing speed if needed
        yield "\n\n"  
        time.sleep(0.2)  # Add delay between paragraphs

# Initialize file processed flag in session state to track processing status
if "image_processed" not in st.session_state:
    st.session_state.image_processed = False

# Initialize list_memory in session state to track memory across interactions
if "list_memory" not in st.session_state:
    st.session_state.list_memory = []

# Placeholder for warning/success message
status_message = st.empty()

# Display warning if file is not yet processed, or success if already processed
if st.session_state.image_processed:
    status_message.success("Image processed successfully! You can now interact with the assistant.", icon="✅")
else:
    status_message.warning("You must upload and submit an image before asking the AI assistant.", icon="⚠️")

# File uploader
image_file = st.file_uploader("Upload your Image Files and Click on the Submit & Process Button (Max. 3 Image)", 
                           accept_multiple_files=True, type=["jpg"])

# Process button functionality
if st.button("Submit & Process"):
    if len(image_file) != 0 and len(image_file) <= 2:
        list_file_uploaded = save_uploaded_file(image_file)

        # Progress bar for detailed processing feedback
        progress_text = "Processing Image files..."
        progress_bar = st.progress(0, text=progress_text)

        # Step 1: Extract PDF content
        st.session_state.list_image_base64 = process_image(list_file_uploaded)
        progress_bar.progress(33, text="Process image content...")

        # Step 2: Loading
        progress_bar.progress(66, text="Process image content...")

        # Step 3: Complete
        progress_bar.progress(100, text="Completed processing image.")
        
        # Set processed flag to True after successful processing and update status message
        st.session_state.image_processed = True
        status_message.success("Image processed successfully! You can now interact with the assistant.", icon="✅")

        try:
            col_1, col_2= st.columns(2)
        
            with col_1:
                st.image(f"./database/uploaded_image/resize_{image_file[0].name}")
                st.write(f"<p style='text-align: center; color:#6F7071'> {image_file[0].name} </p>", unsafe_allow_html=True)

            with col_2:
                st.image(f"./database/uploaded_image/resize_{image_file[1].name}")
                st.write(f"<p style='text-align: center; color:#6F7071'> {image_file[1].name} </p>", unsafe_allow_html=True)

        except Exception as Error:
            pass

        for img in list_file_uploaded["jpg_files"]:   
             print(f"File: {img.split('/')[-1]}")
            
    elif len(image_file) == 0:
        st.error("Please upload a image before submitting.")
    
    elif len(image_file) >= 2:
        st.error("Please upload images with maximum 2 images")

# Separator line
st.divider()  # Alternatively, you can use st.write("----") for a custom separator

#Message Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Respond to user input only if the document is processed
if st.session_state.image_processed:      
    if user_question := st.chat_input("Your Question"):
        st.chat_message("user").markdown(user_question)
        st.session_state.messages.append({"role": "user", "content": user_question})

        # Generate assistant response and memory update
        with st.spinner("Assistant is thinking..."):
            response, memory_chat = qna_with_generative(user_question, st.session_state.list_image_base64, st.session_state.list_memory)
            st.session_state.list_memory.append(memory_chat[0])
            st.session_state.list_memory.append(memory_chat[1])
            write_chat_history(st.session_state.list_memory)
            
        # Display assistant response as streamed text
        with st.chat_message("assistant"):
            response_container = st.empty()
            streamed_response = ""
            for chunk in response_streamer(response.content):
                streamed_response += chunk
                response_container.markdown(streamed_response)

        # Save assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response.content})

else:
    st.markdown(
        """
        <div style="background-color: #EEF0F4; padding: 10px 15px; border-radius: 5px; text-align: center">
            Please <strong>upload and process the image</strong> before asking a question.
        </div>
        """, 
        unsafe_allow_html=True
    )