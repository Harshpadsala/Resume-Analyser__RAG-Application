import os
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter("ignore", ResourceWarning)

from dotenv import load_dotenv
load_dotenv()

# this code is available on weaviate connectivity docs
# Best practice: store your credentials in environment variables
# Connect to Weaviate Cloud
import weaviate
from weaviate.classes.init import Auth

weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)
print("is client of weaviate ready !? : " ,client.is_ready())
print()

# now initialize embedding model : huggingface
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# loading document 
from langchain_community.document_loaders import PyPDFLoader

file_path = "/Users/harshpadsala/RAG/Resume Analyser/Harsh  Padsala.pdf"
loader = PyPDFLoader(file_path)
pages = loader.load()
print()
print('******************* file content *******************')
print(pages[0].page_content)
print()

## split the text into chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 100, 
    chunk_overlap = 30
)

docs = text_splitter.split_documents(pages)
print()
print ("******************* Chunks have been created *******************")
print("Total chunks are :" , len(docs))
print()



# creating vector database on weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore

vector_db = WeaviateVectorStore.from_documents(
    docs , embeddings , client = client, by_text = False
)
print()
print ("******************* Documents stored in vector database successfully *******************")
print()


# we can test some similarity search 
# print(vector_db.similarity_search("what is neural network?", k=3)[0].page_content)


# generate prompt for model to instantiate
from langchain.prompts import ChatPromptTemplate

template="""You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use ten sentences maximum and keep the answer concise.
Question: {question}
Context: {context}
Answer:
"""

prompt=ChatPromptTemplate.from_template(template)

print()
print("prompt : ", prompt)
print()

# Initiate LLM 
from langchain_groq import ChatGroq

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

print("Demo")
# create retriever for fetching the data from the vector database
retriever = vector_db.as_retriever()
print("Demo")

# Create chain 
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
print("Demo")

chain = (
    { "context" : retriever , "question" : RunnablePassthrough() } |
    prompt |
    model |
    StrOutputParser()
)
print()
print("*********************** Chain is created ****************************")
print()

# test model
result = chain.invoke("Share all details of candidate ")
print()
print("Question : Share all details of candidate ")
print("AI : ")
print()
print(result)
print()

# test model
result = chain.invoke("Share schooling details of candidate ")
print()
print("Question : Share schooling details of candidate ")
print("AI : ")
print()
print(result)
print()

# test model
result = chain.invoke("in which project candidate has used Mongodb ?")
print()
print("Question : in which project candidate has used Mongodb  ")
print("AI : ")
print()
print(result)
print()

# test model
result = chain.invoke("is there any certification candidate has done ?")
print()
print("Question : is there any certification candidate has done ?")
print("AI : ")
print()
print(result)
print()

# test model
result = chain.invoke("try to score this resume out of 100?")
print()
print("Question : try to score this resume out of 100?")
print("AI : ")
print()
print(result)
print()



client.close()