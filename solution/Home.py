import streamlit as st
import os

st.set_page_config(
    page_title="EDTS Chatbot",
    page_icon="assets/favicon.ico",)

# #Side Navbar
# pdf_page = st.Page("pages/chat_pdf.py", title="Chat with PDF", icon=":material/home:")
# img_page = st.Page("pages/chat_img.py", title="Chat with Image", icon=":material/home:")
                    

# pg = st.navigation([pdf_page, img_page])

# Design move app further up and remove top padding
st.markdown('''<style>.css-1egvi7u {margin-top: -1rem;}</style>''',
    unsafe_allow_html=True)

# Design hide top header line
hide_decoration_bar_style = '''<style>header {visibility: hidden;}</style>'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

# Design hide "made with streamlit" footer menu area
hide_streamlit_footer = """<style>#MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}</style>"""
st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

#Banner Section
st.image('assets/banner-white.png')
st.divider()

#Description Section
st.markdown("<p style='text-align: center; color:#6F7071'> <strong> EDTS Gen AI Chatbot is your assistant for exploring your own documents. <br> Just upload a PDF or Image, ask questions, and receive answers based on content you uploaded. <strong> </p>", unsafe_allow_html=True)

#Web Development Stack Section
st.markdown("<h4 style='text-align: center; color:#6F7071'> <strong> Web Development Stack <strong> </h3>", unsafe_allow_html=True)

# with st.expander("Show the stack", expanded=True):
col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.image("assets/chatgpt.png")
    st.write("<p style='text-align: center; color:#6F7071'> <strong> ChatGPT <strong> </p>", unsafe_allow_html=True)
    st.write("<p style='text-align: center; color:#6F7071; font-size: 14px;'> Powers the natural language understanding and responses. </p>", unsafe_allow_html=True)

with col2:
    st.image("assets/langchain.png")
    st.write("<p style='text-align: center; color:#6F7071'> <strong> LangChain <strong> </p>", unsafe_allow_html=True)
    st.write("<p style='text-align: center; color:#6F7071; font-size: 14px;'> Orchestrates the conversation, managing logic and flow. </p>", unsafe_allow_html=True)

with col3:
    st.image("assets/faiss.png")
    st.write("<p style='text-align: center; color:#6F7071'> <strong> FAISS <strong> </p>", unsafe_allow_html=True)
    st.write("<p style='text-align: center; color:#6F7071; font-size: 14px;'> Ensures fast, accurate vector search and retrieval. </p>", unsafe_allow_html=True)

with col4:
    st.image("assets/streamlit.png")
    st.write("<p style='text-align: center; color:#6F7071'> <strong> Streamlit <strong> </p>", unsafe_allow_html=True)
    st.write("<p style='text-align: center; color:#6F7071; font-size: 14px;'> Provides an intuitive, user-friendly interface. </p>", unsafe_allow_html=True)


st.divider()

col_button1, col_button2, col_button3 = st.columns(3, gap="medium")
with col_button1:
    pass

with col_button2:
    st.button("Visit Code Repository")

with col_button3:
    pass








