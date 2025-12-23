from langchain_community.document_loaders import TextLoader,PyMuPDFLoader
def document_loader(file_path: str):
    try:
        # i="data/website_documents/"+i
        print(f"loading document:{file_path}")
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()

        if 'muet_data.txt'in file_path:
            documents=documents+pdf_loader()
        return documents
    except Exception as e:
        print(f"Error in load_docs.py: {e}")
        raise e

    
def pdf_loader():
    print("loading PDF Document")
    loader=PyMuPDFLoader('data/website_documents/prospectus.pdf')
    documents = loader.load()
    return documents