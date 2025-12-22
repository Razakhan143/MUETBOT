from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()
def chat_model():
    print("selecting chat model")
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.7)
    

# 1. Initialize the model with OpenRouter configuration
#     llm = ChatOpenAI(
#     model="xiaomi/mimo-v2-flash:free",
#     openai_api_key=os.getenv("OPENROUTER_API_KEY"),
#     openai_api_base="https://openrouter.ai/api/v1",
#     model_kwargs={"extra_body": {"reasoning": {"enabled": True}}}
# )
    return llm

def embeddings_model():
    print("selecting embeding model")
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")