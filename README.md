# Smart Chatbot Kota Cimahi

Aplikasi chatbot cerdas untuk layanan publik Kota Cimahi menggunakan teknologi AI dan vector search.

## Features
- 🤖 Chatbot AI dengan kemampuan RAG (Retrieval Augmented Generation)
- 📝 Sistem pengaduan masyarakat 
- 🛠️ Dashboard admin untuk mengelola pengaduan
- 🔍 Pencarian dokumen dengan FAISS vector search
- ⚡ Streaming response untuk experience yang lebih baik

## Tech Stack
- **Framework**: Streamlit
- **AI Model**: OpenRouter API (DeepSeek)
- **Embeddings**: Jina AI
- **Vector Search**: FAISS
- **Backend**: Python

## Local Development

### Prerequisites
- Python 3.8+
- API Keys:
  - OpenRouter API key
  - Jina AI API key

### Setup
1. Clone repository
```bash
git clone <repository-url>
cd smart-chatbot
```

2. Create virtual environment
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Setup environment variables
```bash
# Copy template and edit with your API keys
cp secrets_template.toml .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your actual API keys
```

5. Run application
```bash
streamlit run app4.py
```

## Deployment to Streamlit Cloud

### Step 1: Prepare Repository
1. Push your code to GitHub
2. Make sure these files are included:
   - `app4.py` (main application)
   - `requirements.txt` (dependencies)
   - `.streamlit/config.toml` (configuration)

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Click "New app"
4. Select your repository
5. Set main file path: `app4.py`
6. Click "Deploy!"

### Step 3: Configure Secrets
1. In your Streamlit Cloud dashboard, go to app settings
2. Go to "Secrets" tab
3. Add the following secrets:
```toml
OPENROUTER_API_KEY = "your_openrouter_api_key_here"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "deepseek/deepseek-r1-0528:free"
JINA_API_KEY = "your_jina_api_key_here"
```

### Step 4: Upload FAISS Files (Optional)
If you have FAISS index files:
1. Include `faiss_index`, `faiss_metadata.json`, and `chunks.json` in your repository
2. Or implement a file uploader in the app for dynamic document loading

## API Keys Required

### OpenRouter API
- Get free API key at [openrouter.ai](https://openrouter.ai)
- Used for LLM inference

### Jina AI
- Get free API key at [jina.ai](https://jina.ai)
- Used for text embeddings

## File Structure
```
smart-chatbot/
├── app4.py                 # Main application
├── requirements.txt        # Python dependencies
├── .streamlit/
│   ├── config.toml        # Streamlit configuration
│   └── secrets.toml       # API keys (local only)
├── .gitignore             # Git ignore file
├── secrets_template.toml  # Template for secrets
├── faiss_index           # FAISS vector index (optional)
├── faiss_metadata.json   # FAISS metadata (optional)
├── chunks.json           # Document chunks (optional)
└── README.md             # This file
```

## Usage
1. **Chatbot Layanan**: Ask questions about Cimahi city services
2. **Pengaduan Masyarakat**: Submit public complaints
3. **Dashboard Admin**: Manage and update complaint status

## Troubleshooting

### Common Issues
1. **FAISS files not found**: App will still work with limited functionality
2. **API rate limits**: Check your API key quotas
3. **Slow responses**: Try reducing context size or use faster models

### Performance Tips
- Use caching for FAISS operations
- Limit document chunk size
- Implement proper error handling for API calls

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This project is open source and available under the MIT License.
