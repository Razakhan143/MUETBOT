def get_retriever(vectordb):
    print("getting retriever")
    # Check database has documents
    doc_count = vectordb._collection.count()
    print(f"Vector DB contains {doc_count} documents")
    
    if doc_count == 0:
        print("⚠️ WARNING: Vector database is empty! Retrieval will not work.")
    
    retriever = vectordb.as_retriever(search_kwargs={"k": 10})
    print("="*50)
    print(retriever)
    print("="*50)

    return retriever