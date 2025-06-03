# Smart Chatbot Kota Cimahi

Aplikasi chatbot untuk layanan publik Kota Cimahi dengan fitur:
- Chat dengan AI untuk informasi layanan publik
- Sistem pengaduan masyarakat
- Dashboard admin untuk mengelola pengaduan

## 🚀 Deployment ke Streamlit Cloud

### Persiapan
1. Fork/clone repository ini ke GitHub Anda
2. Dapatkan API keys yang diperlukan:
   - OpenRouter API Key (untuk LLM)
   - Jina AI API Key (untuk embedding)

### Deploy ke Streamlit Cloud
1. Kunjungi [share.streamlit.io](https://share.streamlit.io)
2. Login dengan akun GitHub
3. Klik "New app"
4. Pilih repository ini
5. Set file utama: `app4.py`
6. Tambahkan secrets di Advanced Settings:

```toml
OPENROUTER_API_KEY = "your_openrouter_api_key"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "deepseek/deepseek-r1-0528:free"
JINA_API_KEY = "your_jina_api_key"
```

### Local Development
1. Copy `secrets_template.toml` ke `.streamlit/secrets.toml`
2. Isi dengan API keys Anda
3. Run: `streamlit run app4.py`

## 📁 File Structure
- `app4.py` - Main application
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `secrets_template.toml` - Template for secrets

## ⚠️ Note
Aplikasi akan berjalan dalam mode fallback jika file FAISS tidak tersedia. Fitur pencarian dokumen akan terbatas tetapi fungsi dasar tetap berjalan.
