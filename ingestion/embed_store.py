import os
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()
def vector_database(chunks,embeddings,flag):
    print('creating vector database')
    DB_PATH = "ingestion/vector_db/muet_chroma_db"

    # 2. Check if the database already exists locally
    if flag and os.path.exists(DB_PATH):
        print("--- Loading existing database from disk ---")
        vectordb = Chroma(
            persist_directory=DB_PATH, 
            embedding_function=embeddings
        )
        # Check if the database is empty
        doc_count = vectordb._collection.count()
        print(f"--- Database contains {doc_count} documents ---")
        
        if doc_count == 0:
            print("⚠️ Database is empty! Rebuilding with new documents...")
            vectordb = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=DB_PATH
            )
            print(f"--- Database rebuilt with {vectordb._collection.count()} documents ---")
    else:
        print("--- Creating NEW database (This will call Gemini API) ---")
        # This step only runs if the folder doesn't exist
        vectordb = Chroma.from_documents(
            documents=chunks, # Ensure split_docs is defined above
            embedding=embeddings,
            persist_directory=DB_PATH
        )
        print(f"--- Database saved locally with {vectordb._collection.count()} documents! ---")

    return vectordb

