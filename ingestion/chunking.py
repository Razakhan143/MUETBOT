from langchain_text_splitters import RecursiveCharacterTextSplitter
def text_splitter(documents):
    print("splitting text")
    splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("Text splitting resulted in zero chunks.")

    return chunks