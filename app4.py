# chatbot_pengaduan_ai.py
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv
from os import getenv
import os
import datetime
import uuid
import requests
import json
import numpy as np
import faiss
import time

load_dotenv()

# Function to get environment variables from st.secrets or .env
def get_env_var(key, default=None):
    """Get environment variable from st.secrets (for Streamlit Cloud) or os.getenv (local)"""
    try:
        # Try st.secrets first (for Streamlit Cloud)
        return st.secrets[key]
    except (KeyError, AttributeError):
        # Fallback to environment variable (for local development)
        return getenv(key, default)

# Debug function to check API key availability
def check_api_keys():
    """Debug function to check if API keys are properly loaded"""
    openrouter_key = get_env_var("OPENROUTER_API_KEY")
    jina_key = get_env_var("JINA_API_KEY")
    
    if openrouter_key:
        st.success(f"✅ OpenRouter API key loaded (ending with: ...{openrouter_key[-4:]})")
    else:
        st.error("❌ OpenRouter API key not found!")
        
    if jina_key:
        st.success(f"✅ Jina API key loaded (ending with: ...{jina_key[-4:]})")
    else:
        st.error("❌ Jina API key not found!")
    
    return openrouter_key is not None and jina_key is not None

# Load FAISS index (wajib ada sebelum aplikasi dijalankan)
faiss_index_path = "extracted/faiss_index"
faiss_metadata_path = "extracted/faiss_metadata.json"  
chunks_path = "extracted/chunks.json"

# Initialize flags for file existence
has_faiss_files = (
    os.path.exists(faiss_index_path) and 
    os.path.exists(faiss_metadata_path) and 
    os.path.exists(chunks_path)
)

if not has_faiss_files:
    st.warning("⚠️ File FAISS index belum tersedia. Fitur pencarian dokumen akan dibatasi.")
    st.info("Untuk menggunakan fitur pencarian dokumen, silakan upload file FAISS index yang diperlukan.")
    
    # For deployment - add demo mode indicator
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = True

# Load FAISS index (cached) - with error handling
@st.cache_resource
def load_faiss_index(index_file=faiss_index_path):
    try:
        if os.path.exists(index_file):
            return faiss.read_index(index_file)
        return None
    except Exception as e:
        st.error(f"Error loading FAISS index: {e}")
        return None

# Load chunks data (cached) - with error handling
@st.cache_resource  
def load_chunks_data(chunks_file=chunks_path):
    try:
        if os.path.exists(chunks_file):
            with open(chunks_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading chunks data: {e}")
        return []

# Load metadata (cached) - with error handling
@st.cache_resource
def load_faiss_metadata(metadata_file=faiss_metadata_path):
    try:
        if os.path.exists(metadata_file):
            with open(metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading metadata: {e}")
        return {}

# Initialize session-state for temporary vectorstore and embedding cache
if "temp_vectorstore" not in st.session_state:
    st.session_state.temp_vectorstore = None

# Initialize embedding cache to reduce API calls for similar queries
if "embedding_cache" not in st.session_state:
    st.session_state.embedding_cache = {}

def get_cached_embedding(text, api_key, cache_key=None):
    """Get embedding with caching to reduce API calls."""
    if cache_key is None:
        cache_key = text[:100]  # Use first 100 chars as cache key
    
    if cache_key in st.session_state.embedding_cache:
        return st.session_state.embedding_cache[cache_key]
    
    embedding = get_jina_embedding(text, api_key)
    if embedding:
        st.session_state.embedding_cache[cache_key] = embedding
        # Limit cache size to prevent memory issues
        if len(st.session_state.embedding_cache) > 50:
            # Remove oldest entries
            oldest_key = next(iter(st.session_state.embedding_cache))
            del st.session_state.embedding_cache[oldest_key]
    
    return embedding

# --- Inisialisasi Model & Embedding ---
llm = ChatOpenAI(
    openai_api_key=get_env_var("OPENROUTER_API_KEY"),
    openai_api_base=get_env_var("OPENROUTER_BASE_URL"),
    model_name=get_env_var("DEFAULT_MODEL", "deepseek/deepseek-chat"),
    temperature=0.1,
    streaming=True,  # Enable streaming for better user experience
)

# Build retriever using FAISS index
def build_combined_retriever():
    faiss_index = load_faiss_index()
    chunks_data = load_chunks_data()
    metadata = load_faiss_metadata()
    
    if faiss_index and chunks_data and metadata:
        return faiss_index, chunks_data, metadata
    else:
        return None, None, None

def search_similar_chunks_batch(queries, api_key, k=50):
    """Search for similar chunks using batch embeddings for multiple queries."""
    faiss_index, chunks_data, metadata = build_combined_retriever()
    
    if not faiss_index:
        return []
    
    # Get batch embeddings for all queries
    query_embeddings = get_jina_batch_embedding(queries, api_key)
    if not query_embeddings:
        return []
    
    batch_results = []
    for i, query_embedding in enumerate(query_embeddings):
        # Convert to numpy array and search
        query_embedding_np = np.array(query_embedding, dtype='float32').reshape(1, -1)
        distances, indices = faiss_index.search(query_embedding_np, k=k)
        
        # Retrieve actual text content for this query
        results = []
        for j, idx in enumerate(indices[0]):
            if idx < len(chunks_data):
                chunk_text = chunks_data[idx]["chunk"]
                results.append({
                    "text": chunk_text,
                    "score": distances[0][j],
                    "filename": chunks_data[idx]["filename"],
                    "chunk_index": chunks_data[idx]["chunk_index"]
                })
        
        batch_results.append({
            "query": queries[i],
            "results": results
        })
    
    return batch_results

def search_similar_chunks(query, api_key, k=50):
    """Search for similar chunks using FAISS and return actual text content."""
    faiss_index, chunks_data, metadata = build_combined_retriever()
    
    if not faiss_index:
        return []
    
    # Get query embedding with caching
    query_embedding = get_cached_embedding(query, api_key)
    if query_embedding is None:
        return []
    
    # Convert to numpy array and search
    query_embedding_np = np.array(query_embedding, dtype='float32').reshape(1, -1)
    distances, indices = faiss_index.search(query_embedding_np, k=k)
    
    # Retrieve actual text content
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(chunks_data):
            chunk_text = chunks_data[idx]["chunk"]
            results.append({
                "text": chunk_text,
                "score": distances[0][i],
                "filename": chunks_data[idx]["filename"],
                "chunk_index": chunks_data[idx]["chunk_index"]
            })
    
    return results

# --- Simpan Pengaduan ---
def save_report(report):
    if "report_data" not in st.session_state:
        st.session_state.report_data = []
    st.session_state.report_data.append(report)

# --- NLP Klasifikasi Dinas ---
def classify_department(text):
    mapping = {
        "jalan": "Dinas Pekerjaan Umum",
        "lampu": "Dinas Perhubungan",
        "air": "PDAM",
        "sampah": "DLH",
        "ktp": "Disdukcapil",
        "puskesmas": "Dinkes",
    }
    for keyword, dinas in mapping.items():
        if keyword in text.lower():
            return dinas
    return "Lainnya"

# --- Fungsi untuk Mendapatkan Embedding dari Jina AI ---
def get_jina_embedding(text, api_key=None, model="jina-embeddings-v3"):
    """Get embedding from Jina AI for a single text (returns list of floats)."""
    if api_key is None:
        api_key = get_env_var("JINA_API_KEY")
        if not api_key:
            st.error("JINA API key not found. Please set it in your environment variables or Streamlit secrets.")
            return None
            
    url = 'https://api.jina.ai/v1/embeddings'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        "model": model,
        "task": "retrieval.query",  # Changed to retrieval.query for user queries
        "late_chunking": False,
        "truncate": False,
        "input": [text]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json().get("data", [])
        if result and "embedding" in result[0]:
            return result[0]["embedding"]
        else:
            return None
    else:
        st.error(f"Jina API error: {response.status_code} {response.text}")
        return None

def get_jina_batch_embedding(texts, api_key, model="jina-embeddings-v3"):
    """Get batch embeddings from Jina AI for multiple texts (returns list of embeddings)."""
    url = 'https://api.jina.ai/v1/embeddings'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        "model": model,
        "task": "retrieval.query",  # For user queries
        "late_chunking": False,
        "truncate": False,
        "input": texts
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json().get("data", [])
        return [item["embedding"] for item in result if "embedding" in item]
    else:
        st.error(f"Jina API error: {response.status_code} {response.text}")
        return None

# --- Navigasi Halaman ---
page = st.sidebar.radio("Pilih Halaman", ["Chatbot Layanan", "Pengaduan Masyarakat", "Dashboard Admin"])

# Add debug section in sidebar
with st.sidebar.expander("🔧 Debug Info"):
    if st.button("Check API Keys"):
        check_api_keys()

# ----------------------------
# PAGE 1: Chatbot Layanan Publik
# ----------------------------
if page == "Chatbot Layanan":
    st.title("🤖 Chatbot Layanan Kota Cimahi")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_question = st.chat_input("Ajukan pertanyaan...")    # Tampilkan riwayat chat (termasuk chat user terbaru jika ada)
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
      # Jika user baru saja mengirim pertanyaan, tampilkan langsung di UI
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_question)

        # Check if FAISS files are available
        if not has_faiss_files:
            # Fallback response when FAISS is not available
            answer = "Maaf, sistem pencarian dokumen sedang tidak tersedia. Namun saya dapat membantu dengan informasi umum tentang layanan Kota Cimahi. Untuk informasi lebih detail, silakan hubungi kantor pelayanan terkait."
            with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(answer)
        else:
            # Normal processing with FAISS
            # Start performance monitoring
            start_time = time.time()
            answer = ""  # Initialize answer variable
            with st.spinner("🔍 Mencari informasi yang relevan..."):
                api_key = get_env_var("JINA_API_KEY")
                search_start = time.time()
                results = search_similar_chunks(user_question, api_key, k=50)
                search_time = time.time() - search_start

                if results:
                    # Create shorter context for faster processing
                    context = "\n\n".join([result["text"][:800] for result in results[:3]])
                      # Show retrieved sources
                    with st.expander("📚 Sumber Informasi"):
                        st.info(f"⚡ Pencarian: {search_time:.2f}s | Dokumen: {len(results)}")
                        for i, result in enumerate(results[:3], 1):  # Fixed: showing only top 3
                            st.write(f"**{i}. {result['filename']}**")
                            st.write(f"_{result['text'][:150]}..._")                    # Optimized system message for better response reliability
                    system_prompt = """Anda adalah chatbot resmi Kota Cimahi yang membantu warga dengan informasi layanan publik. 
                    
INSTRUKSI PENTING:
1. Jawab HANYA berdasarkan dokumen yang disediakan
2. Berikan jawaban yang lengkap dan informatif
3. Jika informasi tidak ada dalam dokumen, katakan "Maaf, informasi tersebut tidak tersedia dalam dokumen yang saya miliki"
4. Gunakan bahasa yang sopan dan mudah dipahami
5. SELALU berikan jawaban yang substantif, bukan hanya informasi teknis"""

                    messages = [
                        SystemMessage(content=system_prompt),
                        SystemMessage(content=f"KONTEKS DOKUMEN:\n{context}"),
                        HumanMessage(content=f"Pertanyaan: {user_question}")
                    ]
                      # Initialize response container
                    with st.chat_message("assistant", avatar="🤖"):
                        llm_start = time.time()
                        response_placeholder = st.empty()
                        full_response = ""
                        
                        try:
                            # Check API key before making LLM call
                            openrouter_key = get_env_var("OPENROUTER_API_KEY")
                            if not openrouter_key:
                                st.error("❌ OpenRouter API key tidak ditemukan! Silakan periksa konfigurasi API key.")
                                # Provide detailed response from context without LLM
                                full_response = f"**Berdasarkan dokumen yang tersedia mengenai '{user_question}':**\n\n{context}\n\n**Catatan:** Respon ini dibuat berdasarkan pencarian dokumen tanpa pemrosesan AI karena masalah konfigurasi API."                             
                            else:# Use streaming for better user experience
                                full_response = ""
                                
                                # Stream the response with character limit
                                for chunk in llm.stream(messages):
                                    if hasattr(chunk, 'content') and chunk.content:
                                        # Stream full response without character limit
                                        full_response += chunk.content
                                        # Update display in real-time with cursor
                                        response_placeholder.markdown(full_response + "▋")
                                
                                # Clean up the final response
                                if isinstance(full_response, str):
                                    full_response = full_response.strip()
                                
                                # Check if we got a meaningful response
                                if not full_response or len(full_response) < 5:
                                    st.warning("⚠️ Model memberikan respons kosong. Menggunakan respons alternatif...")
                                    full_response = f"Berdasarkan dokumen yang tersedia mengenai '{user_question}':\n\n{context[:800]}...\n\nUntuk informasi lebih lengkap, silakan hubungi kantor pelayanan terkait."                            

                            llm_time = time.time() - llm_start
                            total_time = time.time() - start_time
                            
                            # Add performance info
                            perf_info = f"\n\n---\n⚡ **Waktu**: {total_time:.2f}s (Pencarian: {search_time:.2f}s, LLM: {llm_time:.2f}s)"
                            final_response = full_response + perf_info
                            
                            # Show final response without cursor
                            response_placeholder.markdown(final_response)
                            answer = final_response  # Store the complete answer
                        
                        except Exception as e:
                            llm_time = time.time() - llm_start
                            error_str = str(e)
                            
                            # Handle specific API authentication errors
                            if "401" in error_str or "auth" in error_str.lower():
                                st.error("❌ **Masalah Autentikasi API**: Silakan periksa API key di sidebar > Debug Info")
                                # Provide a comprehensive response based on context
                                fallback_response = f"""**Berdasarkan informasi yang tersedia:**

{context}

**Catatan:** Respon ini dibuat berdasarkan pencarian dokumen. Untuk informasi lengkap, silakan hubungi kantor pelayanan terkait."""
                                response_placeholder.markdown(fallback_response)
                                answer = fallback_response
                            else:
                                st.error(f"Error saat mengambil respons LLM: {error_str}")
                                # Provide fallback response based on context
                                error_msg = f"Terjadi kesalahan saat memproses permintaan. Namun berdasarkan informasi yang tersedia:\n\n{context[:600]}...\n\nSilakan coba lagi atau hubungi layanan terkait untuk informasi lebih detail."
                                response_placeholder.markdown(error_msg)
                                answer = error_msg
                
                else:
                    answer = "Maaf, tidak menemukan informasi relevan dalam dokumen."
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(answer)

        # Store the answer in chat history AFTER it's been generated
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

# ----------------------------
# PAGE 2: Pengaduan Masyarakat
# ----------------------------
elif page == "Pengaduan Masyarakat":
    st.title("📣 Formulir Pengaduan Masyarakat")
    nama = st.text_input("Nama Lengkap")
    kontak = st.text_input("Nomor HP / Email")
    isi_aduan = st.text_area("Tuliskan pengaduan Anda")

    if st.button("Kirim Pengaduan"):
        if not nama or not kontak or not isi_aduan:
            st.warning("Mohon lengkapi semua field!")
        else:
            tiket_id = str(uuid.uuid4())[:8]
            dinas_tujuan = classify_department(isi_aduan)
            laporan = {
                "id": tiket_id,
                "nama": nama,
                "kontak": kontak,
                "isi": isi_aduan,
                "dinas": dinas_tujuan,
                "waktu": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "Menunggu Tanggapan"
            }
            save_report(laporan)
            st.success(f"Pengaduan berhasil dikirim! ID Tiket Anda: {tiket_id} (Dikirim ke: {dinas_tujuan})")

# ----------------------------
# PAGE 3: Dashboard Admin
# ----------------------------
elif page == "Dashboard Admin":
    st.title("🛠️ Dashboard Pengaduan Dinas")
    if "report_data" not in st.session_state or not st.session_state.report_data:
        st.info("Belum ada pengaduan masuk.")
    else:
        for rpt in reversed(st.session_state.report_data):
            with st.expander(f"📝 Tiket {rpt['id']} | {rpt['dinas']} | {rpt['status']}"):
                st.markdown(f"**Nama:** {rpt['nama']}")
                st.markdown(f"**Kontak:** {rpt['kontak']}")
                st.markdown(f"**Isi Pengaduan:** {rpt['isi']}")
                st.markdown(f"**Waktu:** {rpt['waktu']}")
                status_options = ["Menunggu Tanggapan", "Diproses", "Selesai"]
                new_status = st.selectbox("Update Status", status_options, index=status_options.index(rpt["status"]), key=rpt["id"])
                if new_status != rpt["status"]:
                    rpt["status"] = new_status
                    st.success("Status diperbarui.")
