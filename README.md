# 🤖 Chatbot with RAG + OpenAI

A simple chatbot project that uses **OpenAI API** and **Retrieval-Augmented Generation (RAG)**  
with a **Python backend** and a **web-based frontend**.

---

## 📂 Project Structure

```
chatbot-python-rag/       # Root project folder
│
├── app/                  # Core chatbot application
│   ├── main.py           # Entry point of chatbot server
│   ├── openai_client.py  # Handles OpenAI API calls
│   ├── rag.py            # RAG (Retrieval-Augmented Generation) logic
│   ├── utils.py          # Helper functions
│
├── scripts/
│   └── build_index.py    # Script to build/search index for RAG
│
├── web/                  # Web interface
│   ├── index.html        # Chatbot frontend (HTML UI)
│   ├── static/           # Static files (JS, CSS)
│   │   └── js/           # JavaScript frontend logic
│
├── .env                  # Environment variables (API keys, configs)
├── .gitignore            # Git ignore file
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # (Optional) For Docker multi-container setup
├── Dockerfile            # Docker build file
└── README.md             # Project documentation
```

---

## ⚙️ Installation & Setup

1. **Clone repo**:
   ```bash
   git clone https://github.com/Sachin-jala/Chat-Bot.git
   cd Chat-Bot
