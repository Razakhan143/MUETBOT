"""
MUET Assistant - Streamlit Chatbot UI
Independent RAG-based chatbot (no FastAPI required)
Developed by Raza Khan
"""

import os
import sys
import base64

# Prevent DLL/tracing issues
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_API_KEY"] = ""

import streamlit as st
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion import load_docs, embed_store, chunking
from models import chat_models
from rag import chain, prompt, retriever

load_dotenv()

# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(
    page_title="MUET Assistant - By Raza Khan",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# Load Background Image
# ============================================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

bg_image_path = os.path.join("static", "muet-bg.jpg")
bg_base64 = get_base64_image(bg_image_path)

if bg_base64:
    bg_style = f'background-image: url("data:image/jpg;base64,{bg_base64}"); background-size: cover; background-position: center; background-attachment: fixed;'
else:
    bg_style = 'background: linear-gradient(135deg, #1a365d 0%, #002147 100%);'

# ============================================================
# Custom CSS
# ============================================================
st.markdown(f"""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

* {{ 
    font-family: 'Poppins', sans-serif;
    box-sizing: border-box;
}}

html, body {{
    overflow-x: hidden;
    width: 100%;
}}

.stApp {{ {bg_style} }}

#MainMenu, footer, .stDeployButton {{ display: none; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1rem !important; }}

/* Chat container styling */
.chat-container {{
    background: white !important;
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.25);
    overflow: hidden;
    padding: 0;
}}

.chat-header {{
    background: linear-gradient(135deg, #002147 0%, #001731 100%);
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin: -1rem -1rem 1rem -1rem;
}}

.chat-header-avatar {{
    width: 40px;
    height: 40px;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}}

.chat-header-info h3 {{
    color: white;
    margin: 0;
    font-size: 14px;
    font-weight: 600;
}}

.chat-header-status {{
    display: flex;
    align-items: center;
    gap: 6px;
    color: rgba(255,255,255,0.9);
    font-size: 12px;
}}

.status-dot {{
    width: 8px;
    height: 8px;
    background: #2ecc71;
    border-radius: 50%;
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
}}

/* Hero section */
.hero-card {{
    background: rgba(0, 33, 71, 0.9);
    backdrop-filter: blur(10px);
    padding: 32px;
    border-radius: 20px;
    color: white;
}}

.hero-card h1 {{
    font-size: 32px;
    margin: 0 0 8px 0;
}}

.hero-card .subtitle {{
    font-size: 16px;
    opacity: 0.9;
    margin-bottom: 24px;
}}

.features {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
}}

.feature {{
    background: rgba(255,255,255,0.1);
    padding: 16px;
    border-radius: 12px;
    text-align: center;
}}

.feature-icon {{
    font-size: 24px;
    margin-bottom: 4px;
}}

.feature-text {{
    font-size: 13px;
}}

/* Trademark */
.trademark {{
    background: linear-gradient(135deg, #002147, #001731);
    color: white;
    padding: 12px 16px;
    border-radius: 10px;
    text-align: center;
    margin-top: 20px;
    font-size: 13px;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #002147, #001731);
}}
[data-testid="stSidebar"] * {{
    color: black !important;
}}

/* Chat container background */
[data-testid="stVerticalBlockBorderWrapper"] > div {{
    background: white !important;
    border-radius: 12px;
}}

[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: white !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stChatMessage"]) {{
    background: white !important;
    border-radius: 12px;
}}

/* Scrollable container background */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {{
    background: white !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] > div[style*="overflow"] {{
    background: white !important;
    border-radius: 12px;
}}

/* Target the scrollable chat container specifically */
.stMainBlockContainer [data-testid="stVerticalBlockBorderWrapper"] {{
    background: white !important;
    border-radius: 12px;
}}

.stMainBlockContainer [data-testid="column"] [data-testid="stVerticalBlockBorderWrapper"] {{
    background: white !important;
    border-radius: 12px;
}}

/* Fix for fixed height container */
[data-testid="stVerticalBlockBorderWrapper"] > div > div {{
    background: white !important;
}}

/* Style chat messages */
[data-testid="stChatMessage"] {{
    background: #f8fafc;
    border-radius: 12px;
    margin-bottom: 8px;
}}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {{
    color: #1a1a1a !important;
}}

[data-testid="stChatMessage"] a {{
    color: #0066cc !important;
}}

/* Welcome box */
.welcome-box {{
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    margin-bottom: 16px;
}}

.welcome-box h4 {{
    color: #002147;
    margin: 0 0 12px 0;
}}

.welcome-box p {{
    color: #4a5568;
    margin: 6px 0;
    font-size: 14px;
}}

.welcome-box ul {{
    margin: 10px 0;
    padding-left: 24px;
}}

.welcome-box li {{
    color: #4a5568;
    font-size: 13px;
    margin: 6px 0;
}}

/* Quick suggestion buttons */
.stButton > button {{
    background: linear-gradient(135deg, #002147, #001731) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    padding: 8px 16px !important;
}}

.stButton > button:hover {{
    background: linear-gradient(135deg, #003366, #002147) !important;
    transform: translateY(-1px);
}}

/* ============================================ */
/* MOBILE RESPONSIVE STYLES */
/* ============================================ */

/* Make columns stack on mobile */
@media (max-width: 768px) {{
    /* Full width container on mobile */
    .block-container {{
        padding: 0.5rem 1rem !important;
        max-width: 100% !important;
    }}
    
    /* Stack columns vertically */
    [data-testid="stHorizontalBlock"] {{
        flex-direction: column !important;
    }}
    
    /* Make each column full width */
    [data-testid="stColumn"] {{
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }}
    
    /* Chat header adjustments */
    .chat-header {{
        padding: 10px 12px;
        margin: -0.5rem -1rem 0.5rem -1rem;
    }}
    
    .chat-header-avatar {{
        width: 35px;
        height: 35px;
        font-size: 18px;
    }}
    
    .chat-header-info h3 {{
        font-size: 13px;
    }}
    
    /* Welcome box mobile */
    .welcome-box {{
        padding: 15px;
    }}
    
    .welcome-box h4 {{
        font-size: 16px;
    }}
    
    .welcome-box p,
    .welcome-box li {{
        font-size: 12px;
    }}
    
    /* Chat messages mobile */
    [data-testid="stChatMessage"] {{
        padding: 8px !important;
        margin-bottom: 6px;
    }}
    
    /* Quick buttons smaller on mobile */
    .stButton > button {{
        font-size: 10px !important;
        padding: 6px 10px !important;
    }}
    
    /* Chat input mobile */
    [data-testid="stChatInput"] {{
        padding: 0 !important;
    }}
    
    [data-testid="stChatInput"] textarea {{
        font-size: 14px !important;
    }}
    
    /* Hide sidebar toggle button space */
    header[data-testid="stHeader"] {{
        display: none !important;
    }}
}}

/* Extra small devices */
@media (max-width: 480px) {{
    .block-container {{
        padding: 0.25rem 0.5rem !important;
    }}
    
    .chat-header {{
        padding: 8px 10px;
    }}
    
    .chat-header-avatar {{
        width: 30px;
        height: 30px;
        font-size: 16px;
    }}
    
    .chat-header-info h3 {{
        font-size: 12px;
    }}
    
    .chat-header-status {{
        font-size: 10px;
    }}
    
    .welcome-box {{
        padding: 12px;
    }}
    
    .welcome-box h4 {{
        font-size: 14px;
    }}
    
    .welcome-box ul {{
        padding-left: 16px;
    }}
    
    .stButton > button {{
        font-size: 9px !important;
        padding: 5px 8px !important;
        border-radius: 15px !important;
    }}
}}

/* Tablet landscape */
@media (min-width: 769px) and (max-width: 1024px) {{
    .block-container {{
        padding: 1rem 2rem !important;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Initialize QA Chain (Cached)
# ============================================================
@st.cache_resource(show_spinner=False)
def initialize_qa_chain():
    """Initialize the RAG QA chain - cached for performance"""
    try:
        OUTPUT_FILE = os.path.join("data", "website_documents", "muet_data.txt")
        NEWS_FILE = os.path.join("data", "website_documents", "muet_circular_data.txt")
        
        file_paths = [OUTPUT_FILE, NEWS_FILE]
        
        all_documents = []
        for path in file_paths:
            if os.path.exists(path):
                all_documents.extend(load_docs.document_loader(path))
        
        if not all_documents:
            return None
        
        chunks = chunking.text_splitter(all_documents)
        embed_model = chat_models.embeddings_model()
        vectordb = embed_store.vector_database(chunks, embed_model, flag=True)
        retrievers = retriever.get_retriever(vectordb)
        chat_model = chat_models.chat_model()
        prompt_template = prompt.prompt_templete()
        qa_chain = chain.rag_chain(retrievers, prompt_template, chat_model)
        
        return qa_chain
    
    except Exception as e:
        st.error(f"❌ Failed to initialize: {str(e)}")
        return None

# ============================================================
# Session State
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chain_initialized" not in st.session_state:
    st.session_state.chain_initialized = False

# ============================================================
# Initialize Chain
# ============================================================
if not st.session_state.chain_initialized:
    with st.spinner("🚀 Initializing MUET Assistant..."):
        qa_chain = initialize_qa_chain()
        if qa_chain:
            st.session_state.chain_initialized = True
            st.session_state.qa_chain = qa_chain

# ============================================================
# Get Response Function
# ============================================================
def get_bot_response(query: str) -> str:
    try:
        if hasattr(st.session_state, 'qa_chain') and st.session_state.qa_chain:
            response = st.session_state.qa_chain.invoke(query)
            return response
        else:
            return "⚠️ Chatbot is not initialized. Please refresh the page."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def clear_chat():
    st.session_state.messages = []

# ============================================================
# Layout - Responsive columns
# ============================================================
# Use single column layout that's centered
_, col2, _ = st.columns([0.5, 2, 0.5])

# ============================================================
# Left - Hero Section
# ============================================================
# with col1:
#     st.markdown("""
#         <div class="hero-card">
#             <h1>🎓 Welcome to MUET</h1>
#             <p class="subtitle">Mehran University of Engineering & Technology</p>
#             <div class="features">
#                 <div class="feature">
#                     <div class="feature-icon">📚</div>
#                     <div class="feature-text">Admissions</div>
#                 </div>
#                 <div class="feature">
#                     <div class="feature-icon">📅</div>
#                     <div class="feature-text">Events</div>
#                 </div>
#                 <div class="feature">
#                     <div class="feature-icon">🏛️</div>
#                     <div class="feature-text">Departments</div>
#                 </div>
#                 <div class="feature">
#                     <div class="feature-icon">💼</div>
#                     <div class="feature-text">Jobs</div>
#                 </div>
#             </div>
#             <p>💬 Chat with our AI Assistant for instant answers!</p>
#             <div class="trademark">
#                 Developed with ❤️ by <strong>Raza Khan</strong>
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

# ============================================================
# Right - Chatbot (Using Native Streamlit Chat)
# ============================================================
with col2:
    # Header
    st.markdown("""
        <div class="chat-header">
            <div class="chat-header-avatar">🤖</div>
            <div class="chat-header-info">
                <h3>MUET Assistant</h3>
                <div class="chat-header-status">
                    <div class="status-dot"></div>
                    <span>Online</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Chat container with scrollable area
    chat_container = st.container(height=350, border=True)
    # with chat_container:
    #     st.markdown(
    #         """
    #         <style>
    #         div[data-testid="stVerticalBlock"] {
    #             background-color: white;
    #             padding: 0px;
    #             border-radius: 0px;
    #             width: 100%;
    #         }
    #         </style>
    #         """,
    #         unsafe_allow_html=True
    #     )

    
    with chat_container:
        # Welcome message if no history
        if len(st.session_state.messages) == 0:
            st.markdown("""
                        
                <div class="welcome-box">
                    <h4>👋 Welcome to MUET Assistant!</h4>
                    <p>I can help you with:</p>
                    <ul>
                        <li>🎓 Admissions & Programs</li>
                        <li>📅 Events & News</li>
                        <li>🏛️ Departments & Faculty</li>
                        <li>📋 Circulars & Notices</li>
                        <li>💼 Jobs & Opportunities</li>
                    </ul>
                    <p><strong>How can I assist you today?</strong></p>
                </div>
            """, unsafe_allow_html=True)
        
        # Display chat messages using native Streamlit chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])
    
    # Quick suggestion buttons
    if len(st.session_state.messages) == 0:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("📋 Admissions", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "What are the admission requirements?"})
                st.rerun()
        with c2:
            if st.button("📰 News", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "What are the latest news?"})
                st.rerun()
        with c3:
            if st.button("💼 Jobs", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "What are the latest job openings?"})
                st.rerun()
    
    # Chat input
    if user_input := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get bot response
        with st.spinner("🤔 Thinking..."):
            response = get_bot_response(user_input)
        
        # Add bot response
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Clear chat and trademark
    col_clear, col_trademark = st.columns([1, 2])
    with col_clear:
        if len(st.session_state.messages) > 0:
            if st.button("🗑️ Clear", use_container_width=True):
                clear_chat()
                st.rerun()
    with col_trademark:
        st.markdown(
            "<p style='text-align: right; color: #666; font-size: 11px; margin-top: 8px;'>"
            "© 2025 <strong>Raza Khan</strong></p>",
            unsafe_allow_html=True
        )

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.markdown("## 🎓 MUET Assistant")
    st.markdown("---")
    st.markdown("""
    **About**
    
    AI-powered assistant for MUET - instant answers about admissions, events, departments, and jobs.
    
    **Tech Stack:**
    - 🧠 LangChain
    - 🔍 ChromaDB  
    - 🤖 Google Gemini
    """)
    st.markdown("---")
    if st.button("🗑️ Clear Chat", key="sb_clear", use_container_width=True):
        clear_chat()
        st.rerun()
    st.markdown("---")
    st.markdown("[🌐 MUET Website](https://www.muet.edu.pk)")
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 16px; background: rgba(255,255,255,0.1); border-radius: 12px;">
        <p style="margin: 0; font-size: 11px; opacity: 0.8;">Developed by</p>
        <p style="margin: 4px 0 0 0; font-size: 18px; font-weight: 600;">🚀 Raza Khan</p>
    </div>
    """, unsafe_allow_html=True)
