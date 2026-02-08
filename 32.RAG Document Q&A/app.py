
import streamlit as st
import os
import time
import openai

from dotenv import load_dotenv

# =======================
# LangChain / LLM Imports
# =======================
from langchain_groq import ChatGroq
#from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader



# =======================
# Environment Setup
# =======================
load_dotenv()

## load the GROQ API Key
os.environ['OPENAI_API_KEY']=os.getenv("OPENAI_API_KEY")
os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")

groq_api_key=os.getenv("GROQ_API_KEY")

llm=ChatGroq(groq_api_key=groq_api_key,model_name="llama-3.1-8b-instant")

prompt=ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.
    Please provide the most accurate response based on the question
    <context>
    {context}
    <context>
    Question:{input}

    """

)

def create_vector_embedding():
    if "vectors" not in st.session_state:
        st.session_state.embeddings=HuggingFaceEmbeddings()
        st.session_state.loader=PyPDFDirectoryLoader("research_papers") ## Data Ingestion step
        st.session_state.docs=st.session_state.loader.load() ## Document Loading
        st.session_state.text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        st.session_state.final_documents=st.session_state.text_splitter.split_documents(st.session_state.docs[:50])
        st.session_state.vectors=FAISS.from_documents(st.session_state.final_documents,st.session_state.embeddings)
st.title("RAG Document Q&A With Groq And Lama3")

user_prompt=st.text_input("Enter your query from the research paper")

if st.button("Document Embedding"):
    create_vector_embedding()
    st.write("Vector Database is ready")

import time

if user_prompt:
    document_chain=create_stuff_documents_chain(llm,prompt)
    retriever=st.session_state.vectors.as_retriever()
    retrieval_chain=create_retrieval_chain(retriever,document_chain)

    start=time.process_time()
    response=retrieval_chain.invoke({'input':user_prompt})
    print(f"Response time :{time.process_time()-start}")

    st.write(response['answer'])

    ## With a streamlit expander
    with st.expander("Document similarity Search"):
        for i,doc in enumerate(response['context']):
            st.write(doc.page_content)
            st.write('------------------------')





##====================================================================
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# groq_api_key = os.getenv("GROQ_API_KEY")

# # =======================
# # LLM Initialization
# # =======================
# llm = ChatGroq(
#     groq_api_key=groq_api_key,
#     #model_name="Llama3-8b-8192"
#     #temperature=0
#     model_name="llama-3.1-8b-instant"
# )

# # =======================
# # Prompt Template
# # =======================
# prompt = ChatPromptTemplate.from_template(
#     """
#     Answer the questions based on the provided context only.
#     Please provide the most accurate response based on the question

#     <context>
#     {context}
#     </context>

#     Question: {input}
#     """
# )

# # =======================
# # Vector Store Creation
# # =======================
# def create_vector_embedding():
#     if "vectors" not in st.session_state:
#        # ✅ Use FREE local HuggingFace embeddings
#         st.session_state.embeddings = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/all-MiniLM-L6-v2"
#         )

#         loader = PyPDFDirectoryLoader("research_papers")
#         docs = loader.load()

#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200
#         )

#         final_docs = splitter.split_documents(docs[:50])

#         st.session_state.vectors = FAISS.from_documents(
#             final_docs,
#             st.session_state.embeddings
#         )

# # =======================
# # Streamlit UI
# # =======================
# st.title("📄 RAG Document Q&A with Groq + Llama3")

# user_prompt = st.text_input("Enter your query from the research papers")

# if st.button("Create Document Embeddings"):
#     create_vector_embedding()
#     st.success("✅ Vector database created successfully")

# # =======================
# # Query Execution
# # =======================
# if user_prompt:
#     if "vectors" not in st.session_state:
#         st.warning("⚠️ Please create document embeddings first.")
#     else:
#         document_chain = create_stuff_documents_chain(llm, prompt)

#         retriever = st.session_state.vectors.as_retriever()

#         retrieval_chain = create_retrieval_chain(
#             retriever=retriever,
#             combine_docs_chain=document_chain
#         )

#         start = time.process_time()
#         response = retrieval_chain.invoke({"input": user_prompt})
#         end = time.process_time()

#         st.write("### ✅ Answer")
#         st.write(response["answer"])

#         st.caption(f"⏱ Response time: {round(end - start, 2)} seconds")

#         with st.expander("📚 Document Similarity Search"):
#             for doc in response["context"]:
#                 st.write(doc.page_content)
#                 st.write("—" * 40)


##===============================================================================##


######### Second Attempt ###########

# import streamlit as st
# import os
# import time
# from dotenv import load_dotenv

# # =======================
# # LangChain / LLM Imports
# # =======================
# from langchain_groq import ChatGroq
# from langchain_openai import OpenAIEmbeddings

# from langchain_text_splitters import RecursiveCharacterTextSplitter

# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser

# #from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_stuff_documents_chain
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains import create_stuff_documents_chain

# from langchain.chains.retrieval import create_retrieval_chain

# from langchain_community.vectorstores import FAISS
# from langchain_community.document_loaders import PyPDFDirectoryLoader

# # =======================
# # Environment Setup
# # =======================
# load_dotenv()

# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# groq_api_key = os.getenv("GROQ_API_KEY")

# # =======================
# # LLM Initialization
# # =======================
# llm = ChatGroq(
#     groq_api_key=groq_api_key,
#     model_name="Llama3-8b-8192"
# )

# # =======================
# # Prompt Template
# # =======================
# prompt = ChatPromptTemplate.from_template(
#     """
#     Answer the question strictly using the provided context.
#     If the answer is not in the context, say "I don't know".

#     <context>
#     {context}
#     </context>

#     Question: {input}
#     """
# )

# # =======================
# # Vector Store Creation
# # =======================
# def create_vector_embedding():
#     if "vectors" not in st.session_state:
#         st.session_state.embeddings = OpenAIEmbeddings()

#         st.session_state.loader = PyPDFDirectoryLoader("research_papers")
#         docs = st.session_state.loader.load()

#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200
#         )

#         final_docs = splitter.split_documents(docs[:50])

#         st.session_state.vectors = FAISS.from_documents(
#             final_docs,
#             st.session_state.embeddings
#         )

# # =======================
# # Streamlit UI
# # =======================
# st.title("📄 RAG Document Q&A with Groq + Llama3")

# user_prompt = st.text_input("Enter your query from the research papers")

# if st.button("Create Document Embeddings"):
#     create_vector_embedding()
#     st.success("✅ Vector database created successfully")

# # =======================
# # Query Execution
# # =======================
# if user_prompt:
#     if "vectors" not in st.session_state:
#         st.warning("⚠️ Please create document embeddings first.")
#     else:
#         document_chain = create_stuff_documents_chain(llm, prompt)

#         retriever = st.session_state.vectors.as_retriever()

#         retrieval_chain = create_retrieval_chain(
#             retriever=retriever,
#             combine_docs_chain=document_chain
#         )

#         start = time.process_time()
#         response = retrieval_chain.invoke({"input": user_prompt})
#         end = time.process_time()

#         st.write("### ✅ Answer")
#         st.write(response["answer"])

#         st.caption(f"⏱ Response time: {round(end - start, 2)} seconds")

#         with st.expander("📚 Document Similarity Search"):
#             for i, doc in enumerate(response["context"]):
#                 st.write(doc.page_content)
#                 st.write("—" * 40)






#######First Attempt ###########


# import streamlit as st

# import os
# from langchain_groq import ChatGroq
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.embeddings import OllamaEmbeddings
# # Text splitters import varies between langchain versions; prefer plural module name
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# #from langchain.chains import create_stuff_documents_chain
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnablePassthrough

# from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains import create_retrieval_chain
# from langchain_community.vectorstores import FAISS
# from langchain_community.document_loaders import PyPDFDirectoryLoader
# import openai

# from dotenv import load_dotenv
# load_dotenv()
# ## load the GROQ API Key
# os.environ['OPENAI_API_KEY']=os.getenv("OPENAI_API_KEY")
# os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")

# groq_api_key=os.getenv("GROQ_API_KEY")

# llm=ChatGroq(groq_api_key=groq_api_key,model_name="Llama3-8b-8192")

# prompt=ChatPromptTemplate.from_template(
#     """
#     Answer the questions based on the provided context only.
#     Please provide the most accurate respone based on the question
#     <context>
#     {context}
#     <context>
#     Question:{input}

#     """

# )

# def create_vector_embedding():
#     if "vectors" not in st.session_state:
#         st.session_state.embeddings=OpenAIEmbeddings()
#         st.session_state.loader=PyPDFDirectoryLoader("research_papers") ## Data Ingestion step
#         st.session_state.docs=st.session_state.loader.load() ## Document Loading
#         st.session_state.text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
#         st.session_state.final_documents=st.session_state.text_splitter.split_documents(st.session_state.docs[:50])
#         st.session_state.vectors=FAISS.from_documents(st.session_state.final_documents,st.session_state.embeddings)
# st.title("RAG Document Q&A With Groq And Lama3")

# user_prompt=st.text_input("Enter your query from the research paper")

# if st.button("Document Embedding"):
#     create_vector_embedding()
#     st.write("Vector Database is ready")

# import time

# if user_prompt:
#     document_chain=create_stuff_documents_chain(llm,prompt)
#     retriever=st.session_state.vectors.as_retriever()
#     retrieval_chain=create_retrieval_chain(retriever,document_chain)

#     start=time.process_time()
#     response=retrieval_chain.invoke({'input':user_prompt})
#     print(f"Response time :{time.process_time()-start}")

#     st.write(response['answer'])

#     ## With a streamlit expander
#     with st.expander("Document similarity Search"):
#         for i,doc in enumerate(response['context']):
#             st.write(doc.page_content)
#             st.write('------------------------')






