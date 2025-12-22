import os

BASE_DIR = "university-rag-chatbot"

STRUCTURE = {
    "data": {
        "syllabi": {},
        "policies": {},
        "notices": {}
    },
    "ingestion": {
        "load_docs.py": "",
        "chunking.py": "",
        "embed_store.py": ""
    },
    "rag": {
        "retriever.py": "",
        "prompt.py": "",
        "chain.py": ""
    },
    "app": {
        "api.py": "",
        "ui.py": ""
    },
    "requirements.txt": "",
    "README.md": "",
    "architecture.png": None  # placeholder file
}


def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)

        # Create directory
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)

        # Create file
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    if content:
                        f.write(content)


if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    create_structure(BASE_DIR, STRUCTURE)
    print("✅ university-rag-chatbot project structure created successfully!")
