# --- Import Libraries ---
import os
import pymupdf  
import streamlit as st
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

gemini_api_key = os.environ.get("GEMINI_API_KEY")
if gemini_api_key is None:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")

# --- Streamlit App ---
st.set_page_config(page_title="TechSpec AI", layout="wide")

# --- Function to Extract Text from PDFs ---
@st.cache_resource
def extract_text_from_pdfs(pdf_folder):
    extracted_texts = {}
    pdf_paths = [os.path.join(pdf_folder, file) for file in os.listdir(pdf_folder) if file.endswith(".pdf")]

    for pdf_path in pdf_paths:
        file_name = os.path.basename(pdf_path)
        try:
            doc = pymupdf.open(pdf_path)
            text = "\n".join([page.get_text() for page in doc if page.get_text()])
            extracted_texts[file_name] = text
            print(f"Extracted text from {file_name}")
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

    return extracted_texts

# --- Function to Load and Cache FAISS Vector Store for RAG ---
@st.cache_resource
def load_faiss_index():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)
    return vector_store

# --- Load FAISS if not already loaded --- (For first time)
if "vector_store" not in st.session_state:
    if os.path.exists("faiss_index"):
        st.session_state.vector_store = load_faiss_index()
    else:
        extracted_texts = extract_text_from_pdfs("3gpp_specs")
        combined_context = "\n\n".join([f"### {file_name} ###\n{text}" for file_name, text in extracted_texts.items()])
        
        # Chunking the text for storing the vector embeddings
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=250)
        chunks = text_splitter.create_documents([combined_context])

        # Store in FAISS
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_store = FAISS.from_documents(chunks, embedding_model, normalize_L2=True)
        vector_store.save_local("faiss_index")

        print("FAISS vector database created and saved.")
        
        # Load FAISS into session state
        st.session_state.vector_store = load_faiss_index()

# --- Function for Retrieval-Augmented Generation (RAG) using Gemini ---
def generate_answer_with_rag(query):
    retriever = st.session_state.vector_store.as_retriever(search_kwargs={"k": 7})  # Retrieve the top 3 chunks for preventing hallucination and keeping context coherence
    relevant_docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])  # Combine top chunks

    # Generate response with Gemini
    model = genai.GenerativeModel("gemini-1.5-pro")  
    response = model.generate_content(f"Context: {context}\n\nQuestion: {query}")

    return response.text  # Extract the generated answer

# --- Streamlit UI ---
st.title("🤖 TechSpec AI: An Interactive 3GPP Technical Assistant for Telecom R&D")
st.write("Ask questions about **5G 3GPP specifications**, get precise answers!! Save Time!!")
st.write("**Limit : 15 queries/day**")

user_question = st.text_input("🔍 Ask a Technical Question:")

if user_question:
    with st.spinner("🤖 Thinking..."):
        answer = generate_answer_with_rag(user_question)  
    st.success("✅ Answer:")
    st.write(answer)
