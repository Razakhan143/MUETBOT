
import os
# These MUST stay at the very top to prevent the DLL block error
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = ""

import asyncio
import sys
from dotenv import load_dotenv

# Ensure the root directory is in the path so local modules are found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion import load_docs, embed_store, chunking
from models import chat_models
from rag import chain, prompt, retriever


load_dotenv()

def retriever_qa(file_paths, flag):
    """
    file_paths: Can be a single string or a list of strings
    """
    try:
        # Step 1: Load Documents
        # Logic check: If document_loader expects a string, we loop if a list is provided
        all_documents = []
        if isinstance(file_paths, list):
            for path in file_paths:
                # path=f"data\website_documents\{path}"
                print(path)
                if os.path.exists(path):
                    all_documents.extend(load_docs.document_loader(path))
                else:
                    print(f"⚠️ Warning: File not found at {path}")
        else:
            all_documents = load_docs.document_loader(file_paths)

        if not all_documents:
            raise ValueError("No documents were loaded. Check your file paths.")

        # Step 2: Split Text
        chunks = chunking.text_splitter(all_documents)

        # Step 3: Embeddings & Vector DB
        embed_model = chat_models.embeddings_model()
        vectordb = embed_store.vector_database(chunks, embed_model, flag)

        # Step 4: Retriever
        retrievers = retriever.get_retriever(vectordb)

        # Step 5: LLM & Prompt
        chat_model = chat_models.chat_model()
        prompt_template = prompt.prompt_templete()

        # Step 6: QA Chain
        qa_chain = chain.rag_chain(retrievers, prompt_template, chat_model)

        return qa_chain

    except Exception as e:
        print(f"❌ Initialization Error: {str(e)}")
        return None
