from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from datetime import datetime
from pytz import timezone

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_current_datetime():
    """Get current datetime in Pakistan timezone"""
    pk_tz = timezone('Asia/Karachi')
    return datetime.now(pk_tz).strftime("%Y-%m-%d %H:%M:%S %Z")

def rag_chain(retriever, prompt_template, llm):
    print("creating RAG chain")
    rag_chain = (
        {
            "content": retriever | format_docs,
            "question": RunnablePassthrough(),
            "date_time": RunnableLambda(lambda x: get_current_datetime())
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )

    print("Professional MUET Chatbot Chain is ready!")
    return rag_chain
