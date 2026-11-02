import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PDF_PATH = os.path.join(DATA_DIR, "políticas_da_loja.pdf")
CHROMA_DIR = os.path.join(BASE_DIR, "vector_store")

def ingest_policies():

    print("📖 A iniciar a leitura do PDF de políticas da loja...")
    pdf_file = PDF_PATH if os.path.exists(PDF_PATH) else os.path.join(BASE_DIR, "politicas_da_loja.pdf")
    if not os.path.exists(pdf_file):
        raise FileNotFoundError(f"⚠️ Ficheiro PDF não encontrado em: {pdf_file}")

    # load the PDF document
    loader = PyPDFLoader(pdf_file)
    documents = loader.load()
    print(f"✅ PDF carregado com sucesso ({len(documents)} páginas).")

    # slice the text into semantic chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 700, chunk_overlap = 150, separators=["\n\n", "\n", " ", ""])
    chunks = text_splitter.split_documents(documents)
    print(f"✂️ Texto dividido em {len(chunks)} chunks semânticos.")

    # create a vector store (ChromaDB) for semantic search
    print("🧠 A gerar embeddings e a guardar no ChromaDB local...")
    embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(documents = chunks, embedding = embeddings, persist_directory = CHROMA_DIR)
    print(f"🎉 Base vetorial (RAG) criada com sucesso no diretório: {CHROMA_DIR}")

if __name__ == "__main__":

    ingest_policies()