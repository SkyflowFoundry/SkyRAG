import fitz  # PyMuPDF
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from service.detect_api import skyflow_detect, skyflow_identify

# Initialize the OpenAI embeddings for use with Chroma
embeddings = OpenAIEmbeddings()
persist_directory = "./chroma_db"

# vector_db = Chroma(collection_name='documents', embedding_function=embeddings)

def ingest_data(file_paths,auth_level):
    """Ingests data from files into a vector database using Langchain."""
    documents = []
    chunker = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=50)
    for path in file_paths:
        doc = fitz.open(path)
        content = ""
        for page in doc:  # Iterate through each page
            content += page.get_text()
        tokenize_response = skyflow_detect(content)
        tokenize_text = tokenize_response['processed_text']
        print(tokenize_text)
        chunks = chunker.create_documents([tokenize_text], [{"auth_level": auth_level}])
        documents.extend(chunks)
        print(f"Total Documents: {len(documents)}")
        os.remove(path)
    db = Chroma.from_documents(documents, embeddings, persist_directory=persist_directory)
    print(f"Total Documents Ingested: {len(documents)}")

def query_vector_db(query_text, top_k=5):
    """Query the vector database to find the top_k most similar entries to the query_text."""
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    tokenize_response = skyflow_detect(query_text)
    tokenize_prompt = tokenize_response['processed_text']
    results = db.similarity_search(tokenize_prompt, k=top_k)
    print("Query Results Length:", len(results))
    return results,tokenize_prompt

def print_query_results(query_text, auth_level):
    print(auth_level)
    """Prints the results of a query against the vector database, filtered by auth level."""
    results, tokenize_prompt = query_vector_db(query_text)
    response_objects = {}
    response_objects["results"] = []

    # Filter results based on the given auth_level
    for idx, result in enumerate(results):
        result_auth_level = result.metadata.get('auth_level', 'Unknown')
        
        # Include the result only if the auth_level matches
        if result_auth_level == auth_level:
            response_object = {
                "Result": idx + 1,
                "Content": result.page_content,
                "Score": result.metadata.get('score', 'Unknown'),
                "auth_level": result_auth_level,
            }
            response_objects["results"].append(response_object)
    response_objects["tokenize_query"] = tokenize_prompt
    return response_objects
