# Pencarian dengan FAISS dan Embedding Jina AI

import faiss
import numpy as np
import json
import requests
import os

# Load FAISS index
faiss_index = faiss.read_index("extracted/faiss_index")

# Load metadata untuk mapping ke dokumen/chunk
with open("extracted/faiss_metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Fungsi untuk mendapatkan embedding dari Jina AI
def get_jina_embedding(text, api_key, model="jina-embeddings-v3"):
    url = "https://api.jina.ai/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "task": "text-matching",
        "late_chunking": False,
        "truncate": False,
        "input": [text]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json().get("data", [])
        if result and "embedding" in result[0]:
            return result[0]["embedding"]
    print("Jina API error:", response.status_code, response.text)
    return None

# Contoh query
query = "bagaimana jika aku tidak membayar pajak?"

# Dapatkan embedding query dari Jina AI menggunakan environment variable
api_key = os.getenv('JINA_API_KEY')
if not api_key:
    raise Exception("JINA_API_KEY tidak ditemukan dalam environment variables")

query_emb = get_jina_embedding(query, api_key)
if query_emb is None:
    raise Exception("Gagal mendapatkan embedding dari Jina AI")

# Ubah ke numpy array dan reshape
query_emb_np = np.array(query_emb, dtype="float32").reshape(1, -1)

# Cari top-10 dokumen terdekat di FAISS
D, I = faiss_index.search(query_emb_np, k=10)
print("Top 10 index:", I)
print("Top 10 distance:", D)

# Ambil metadata dan tampilkan hasil
print("\nHasil pencarian:")
for i, idx in enumerate(I[0]):
    print(f"{i+1}. {metadata[idx]}")

# Menyusun konteks dari hasil FAISS
context = "\n\n".join([str(metadata[idx]) for idx in I[0]])
print(f"\nKonteks lengkap:\n{context}")