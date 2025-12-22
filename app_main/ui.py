# =========================
# Environment & Warnings
# =========================
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"

import warnings
warnings.filterwarnings("ignore")

# =========================
# Imports
# =========================
import gradio as gr
from app import api

# =========================
# Gradio Interface
# =========================
file_path='data\muet_news_data.txt'
rag_application = gr.Interface(
    fn=api.retriever_qa(file_path),
    inputs=[
       
        gr.Textbox(
            label="Your Question",
            placeholder="Ask something from the document...",
            lines=2
        ),
    ],
    outputs=gr.Textbox(label="Answer"),
    title="📄 PDF Question Answering Bot",
    description="Upload a PDF and ask questions using Watsonx + LangChain.",
    allow_flagging="never",
)

# =========================
# Launch App
# =========================
if __name__ == "__main__":
    rag_application.launch(
        server_name="127.0.0.1",
        server_port=7870,
    )
