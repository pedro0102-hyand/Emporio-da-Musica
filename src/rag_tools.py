import os
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, "vector_store")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

@tool
def consult_store_policies(query: str) -> str:
    """Busca políticas e regras da loja em uma base vetorial semântica para responder dúvidas sobre devolução, entrega e garantia."""

    if not os.path.exists(CHROMA_DIR):
        return "Erro: A base de políticas da loja ainda não foi indexada."
        
    vectorstore = Chroma(persist_directory = CHROMA_DIR, embedding_function = embeddings)
    docs = vectorstore.similarity_search(query, k=3)
    
    if not docs:
        return "Nenhuma política relevante encontrada para a pergunta."
        
    context = "\n---\n".join([doc.page_content for doc in docs])
    return context