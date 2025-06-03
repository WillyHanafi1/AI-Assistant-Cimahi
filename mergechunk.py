import json

# Load chunks
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

merged_chunks = []
current = None

TARGET_LEN = 1000

for chunk in chunks:
    # Mulai chunk baru jika belum ada, atau jika file/doc_part berubah
    if (
        current is None
        or chunk["filename"] != current["filename"]
        or chunk["doc_part"] != current["doc_part"]
    ):
        if current:
            merged_chunks.append(current)
        current = {
            "filename": chunk["filename"],
            "doc_part": chunk["doc_part"],
            "chunk_index": chunk["chunk_index"],
            "chunk": chunk["chunk"],
        }
    else:
        # Gabungkan ke chunk sebelumnya
        if len(current["chunk"]) < TARGET_LEN:
            current["chunk"] += chunk["chunk"]
        else:
            merged_chunks.append(current)
            current = {
                "filename": chunk["filename"],
                "doc_part": chunk["doc_part"],
                "chunk_index": chunk["chunk_index"],
                "chunk": chunk["chunk"],
            }

# Tambahkan chunk terakhir
if current:
    merged_chunks.append(current)

# Simpan hasil
with open("chunks_merged.json", "w", encoding="utf-8") as f:
    json.dump(merged_chunks, f, ensure_ascii=False, indent=2)

print(f"Total merged chunks: {len(merged_chunks)}")