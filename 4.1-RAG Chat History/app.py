# ## RAG Q&A CONVERSATION with PDF Including Chat History

## RAG Q&A Conversation With PDF Including Chat History
import streamlit as st
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from chromadb import Client
from chromadb.config import Settings
import os

from dotenv import load_dotenv
load_dotenv()

os.environ['HF_TOKEN']=os.getenv("HF_TOKEN")
embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


## set up Streamlit 
st.title("Conversational RAG With PDF uplaods and chat history")
st.write("Upload Pdf's and chat with their content")

## Input the Groq API Key
api_key=st.text_input("Enter your Groq API key:",type="password")

## Check if groq api key is provided
if api_key:
    llm=ChatGroq(groq_api_key=api_key,model_name="llama-3.1-8b-instant")

    ## chat interface

    session_id=st.text_input("Session ID",value="default_session")
    ## statefully manage chat history

    if 'store' not in st.session_state:
        st.session_state.store={}

    uploaded_files=st.file_uploader("Choose A PDf file",type="pdf",accept_multiple_files=True)
    ## Process uploaded  PDF's
    if uploaded_files:
        documents=[]
        for uploaded_file in uploaded_files:
            temppdf=f"./temp.pdf"
            with open(temppdf,"wb") as file:
                file.write(uploaded_file.getvalue())
                file_name=uploaded_file.name

            loader=PyPDFLoader(temppdf)
            docs=loader.load()
            documents.extend(docs)

    # Split and create embeddings for the documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
        splits = text_splitter.split_documents(documents)
        
        client = Client(
            Settings(
                persist_directory="./chroma_db",
                anonymized_telemetry=False
            ),
            tenant="default_tenant",
            database="default_database"
        )
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            client=client,
            collection_name="rag_collection"
        )   
        #vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever()    

        contextualize_q_system_prompt=(
            "Given a chat history and the latest user question"
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", contextualize_q_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
        
        history_aware_retriever=create_history_aware_retriever(llm,retriever,contextualize_q_prompt)

        ## Answer question

        # Answer question
        system_prompt = (
                "You are an assistant for question-answering tasks. "
                "Use the following pieces of retrieved context to answer "
                "the question. If you don't know the answer, say that you "
                "don't know. Use three sentences maximum and keep the "
                "answer concise."
                "\n\n"
                "{context}"
            )
        qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
        
        question_answer_chain=create_stuff_documents_chain(llm,qa_prompt)
        rag_chain=create_retrieval_chain(history_aware_retriever,question_answer_chain)

        def get_session_history(session:str)->BaseChatMessageHistory:
            if session_id not in st.session_state.store:
                st.session_state.store[session_id]=ChatMessageHistory()
            return st.session_state.store[session_id]
        
        conversational_rag_chain=RunnableWithMessageHistory(
            rag_chain,get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )

        user_input = st.text_input("Your question:")
        if user_input:
            session_history=get_session_history(session_id)
            response = conversational_rag_chain.invoke(
                {"input": user_input},
                config={
                    "configurable": {"session_id":session_id}
                },  # constructs a key "abc123" in `store`.
            )
            st.write(st.session_state.store)
            st.write("Assistant:", response['answer'])
            st.write("Chat History:", session_history.messages)
else:
    st.warning("Please enter the GRoq API Key")












# import os
# import streamlit as st
# from dotenv import load_dotenv

# from langchain_groq import ChatGroq
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.chat_message_histories import ChatMessageHistory

# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory

# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains.history_aware_retriever import create_history_aware_retriever
# from langchain.chains.retrieval import create_retrieval_chain
# from langchain_core.messages import HumanMessage, AIMessage

# from langchain_chroma import Chroma

# # --------------------------------------------------
# # ENV SETUP
# # --------------------------------------------------
# load_dotenv()
# os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

# # --------------------------------------------------
# # STREAMLIT UI
# # --------------------------------------------------
# st.set_page_config(page_title="Conversational RAG", layout="wide")
# st.title("📄 Conversational RAG with PDF + Chat History")

# api_key = st.text_input("Enter your Groq API Key", type="password")

# # --------------------------------------------------
# # SESSION STATE INIT
# # --------------------------------------------------
# if "store" not in st.session_state:
#     st.session_state.store = {}

# if "session_id" not in st.session_state:
#     st.session_state.session_id = "default_session"

# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# # --------------------------------------------------
# # LLM + EMBEDDINGS
# # --------------------------------------------------
# if api_key:
#     llm = ChatGroq(
#         groq_api_key=api_key,
#         model_name="llama-3.1-8b-instant"
#     )

#     embeddings = HuggingFaceEmbeddings(
#         model_name="all-MiniLM-L6-v2"
#     )

#     session_id = st.text_input(
#         "Session ID",
#         value=st.session_state.session_id
#     )
#     st.session_state.session_id = session_id

#     # --------------------------------------------------
#     # FILE UPLOAD
#     # --------------------------------------------------
#     uploaded_files = st.file_uploader(
#         "Upload PDF files",
#         type=["pdf"],
#         accept_multiple_files=True
#     )

#     if uploaded_files:
#         documents = []

#         for uploaded_file in uploaded_files:
#             temp_path = f"./temp_{uploaded_file.name}"
#             with open(temp_path, "wb") as f:
#                 f.write(uploaded_file.getvalue())

#             loader = PyPDFLoader(temp_path)
#             documents.extend(loader.load())

#         # --------------------------------------------------
#         # SPLIT + VECTOR STORE
#         # --------------------------------------------------
#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1500,
#             chunk_overlap=200
#         )
#         splits = splitter.split_documents(documents)

#         vectorstore = Chroma.from_documents(
#             documents=splits,
#             embedding=embeddings,
#             persist_directory="./chroma_db"
#         )

#         retriever = vectorstore.as_retriever()

#         # --------------------------------------------------
#         # HISTORY-AWARE QUESTION PROMPT
#         # --------------------------------------------------
#         contextualize_q_prompt = ChatPromptTemplate.from_messages([
#             ("system",
#              "Given the chat history and the latest user question, "
#              "reformulate the question into a standalone question. "
#              "Do NOT answer the question."),
#             MessagesPlaceholder("chat_history"),
#             ("human", "{input}")
#         ])

#         history_aware_retriever = create_history_aware_retriever(
#             llm,
#             retriever,
#             contextualize_q_prompt
#         )

#         # --------------------------------------------------
#         # QA PROMPT
#         # --------------------------------------------------
#         qa_prompt = ChatPromptTemplate.from_messages([
#             ("system",
#              "You are a helpful assistant. Use the provided context to answer "
#              "the question. If you don't know, say you don't know.\n\n{context}"),
#             MessagesPlaceholder("chat_history"),
#             ("human", "{input}")
#         ])

#         qa_chain = create_stuff_documents_chain(llm, qa_prompt)
#         rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

#         # --------------------------------------------------
#         # CHAT HISTORY HANDLER
#         # --------------------------------------------------
#         def get_session_history(session_id: str) -> BaseChatMessageHistory:
#             if session_id not in st.session_state.store:
#                 st.session_state.store[session_id] = ChatMessageHistory()
#             return st.session_state.store[session_id]

#         conversation_chain = RunnableWithMessageHistory(
#             rag_chain,
#             get_session_history,
#             input_message_key="input",
#             history_message_key="chat_history",
#             output_message_key="answer",
#         )

#         # --------------------------------------------------
#         # CHAT UI
#         # --------------------------------------------------
#         user_question = st.chat_input("Ask a question from the PDFs")

#         if user_question:
#             response = conversation_chain.invoke({
#                 "input": user_question,
#                 "chat_history": st.session_state.chat_history
#             },
#             config={ 
#                 "configurable": {"session_id": "default"}
#             })
#             st.session_state.chat_history.append(HumanMessage(content=user_question))
#             st.session_state.chat_history.append(AIMessage(content=response["answer"]))


#             st.chat_message("assistant").write(response["answer"])

#             with st.expander("🔍 Chat History"):
#                 st.write(st.session_state.store[session_id].messages)

# else:
#     st.warning("Please enter your Groq API Key to proceed.")




















# import streamlit as st
# #from langchain.chains import create_history_aware_retrieval, create_retrieval_chain

# from langchain.chains.history_aware_retriever import create_history_aware_retriever
# from langchain.chains.retrieval import create_retrieval_chain

# from langchain_chroma import Chroma
# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_groq import ChatGroq
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter 
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain_chroma import Chroma
# from chromadb import Client
# from chromadb.config import Settings
# from langchain_chroma import Chroma
# from langchain_openai import OpenAIEmbeddings

# import os

# from dotenv import load_dotenv
# load_dotenv()

# os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")  
# embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ## set up StreamLit
# st.title("Conversational RAG with PDF uploads and Chat History")
# st.write("Upload your PDF documents and chat with context of the conversation!")

# ## Inpput the groq API key
# api_key=st.text_input("Enter your Groq API Key:", type="password")  

# ## check if groq api key is provided
# if api_key:
#     llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.1-8b-instant")

#     ## chat interface
#     session_id = st.text_input("Enter a session ID for chat history", value="default_session")

#     ## statefully manage chat history
#     if 'store' not in st.session_state:
#         st.session_state.store = {}

#     uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

#     ## Process uploaded PDFs
#     if uploaded_files:
#         documents=[]
#         for uploaded_file in uploaded_files:
#             temppdf=f"./temp.pdf"
#             with open(temppdf, "wb") as file:
#                 file.write(uploaded_file.getvalue())
#                 file_name=uploaded_file.name
            
#             loader=PyPDFLoader(temppdf)
#             docs=loader.load()
#             documents.extend(docs)

#         ## Split and create embeddings for the documents
#         text_splitter=RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
#         splits=text_splitter.split_documents(documents)
#         #vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
#         vectorstore = Chroma.from_documents(documents=splits,embedding=embeddings,persist_directory="./chroma_db")


#         retriever=vectorstore.as_retriever()
    
#         contextualize_q_system_prompt=(
#             "Given a chart history and the latest user question"
#             "which might reference context from the chat history,"
#             "formulate a standalone question that includes all necessary context"
#             "without the chart history. Do not include the question,"
#             "just reformulate it if needed and otherwise return it as is." 
#         )
        
#         contextualize_q_prompt=ChatPromptTemplate.from_messages( 
#             [
#                 ("system", contextualize_q_system_prompt),
#                 MessagesPlaceholder("chat_history"),
#                 ("human", "{input}"),
#             ]
#         )

#         history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    
#         ## Answer Questions with chat history
#         system_prompt=(
#             "You are a helpful AI assistant that helps people find information"
#             "from their uploaded PDF documents. Use the following context"
#             "to answer the users question. If you don't know the answer,"
#             "just say you don't know, don't try to make up an answer."
#             "answer in a concise manner."
#             "\n\n"
#             "{context}"
#         )
#         qa_prompt=ChatPromptTemplate.from_messages(
#             [   
#             ("system", system_prompt),
#                 MessagesPlaceholder("chat_history"),
#                 ("human", "{input}"),
#             ]
#         )

#         question_answering_chain = create_stuff_documents_chain(llm, qa_prompt)
#         rag_chain = create_retrieval_chain(history_aware_retriever,question_answering_chain)

#         def get_session_history(session: str) -> BaseChatMessageHistory:
#             if session_id not in st.session_state.store:
#                 st.session_state.store[session_id] = ChatMessageHistory()
#             return st.session_state.store[session_id]

#         conversation_rag_chain = RunnableWithMessageHistory(
#             rag_chain, get_session_history,
#             input_message_key="input",
#             history_message_key="chat_history",
#             output_message_key="answer",
#         )

#         if "chat_history" not in st.session_state:
#             st.session_state.chat_history = []

#         if "session_id" not in st.session_state:
#             st.session_state.session_id = "default_session"

#         user_question = st.chat_input("Ask your question")

#         if user_question:
#             session_history = get_session_history(session_id)
#             response = conversation_rag_chain.invoke(
#                 {"input": user_question},
#                 config={"configurable": {"session_id": session_id}}
#             )   

#             # response = conversation_rag_chain.invoke(
#             #     {"input": user_input}, 
#             #     config={
#             #         "configurable": {"session_id": session_id
#             #         },  #contruct a key "abc123" in 'store'.
#             #     }
#             # )
#             st.write(st.session_state.store)
#             st.success("Assistant: ", response["answer"])
#             st.write("Chat History: ", session_history.messages)
# else:
#     st.warning("Please enter your Groq API Key to proceed.")