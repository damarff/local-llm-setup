# Local LLM Setup

One-click local LLM deployment with Ollama, Open WebUI, and FastAPI. Run AI models on your own hardware — no API keys, no cloud costs, full privacy.

## Features

- **One-Click Setup** — `./setup.sh` and you're running
- **Multiple Models** — Llama 3, Mistral, DeepSeek, Qwen, and more
- **Web UI** — Chat interface via Open WebUI (localhost:3000)
- **API Backend** — FastAPI endpoints for integration (localhost:8000)
- **RAG Support** — Upload documents and chat with them
- **GPU Accelerated** — NVIDIA GPU support out of the box
- **Self-Hosted** — Full control, no data leaves your machine

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/damarff/local-llm-setup.git
cd local-llm-setup

# 2. Run setup
./setup.sh

# 3. Open WebUI
# Navigate to http://localhost:3000
```

That's it! The setup script will:
1. Start Ollama, Open WebUI, and FastAPI via Docker
2. Wait for Ollama to be ready
3. Pull the default model (llama3)

## Services

| Service | URL | Description |
|---------|-----|-------------|
| Open WebUI | http://localhost:3000 | Chat interface (browser) |
| FastAPI | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Ollama | http://localhost:11434 | LLM inference server |

## API Endpoints

### Chat
```bash
# Simple chat
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python?", "model": "llama3"}'
```

### Models
```bash
# List models
curl http://localhost:8000/models/

# Pull a new model
curl -X POST http://localhost:8000/models/pull \
  -H "Content-Type: application/json" \
  -d '{"model": "mistral"}'
```

### RAG (Chat with Documents)
```bash
# Upload a document
curl -X POST http://localhost:8000/rag/upload \
  -F "file=@document.pdf"

# Chat with documents
curl -X POST http://localhost:8000/rag/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'
```

## Supported Models

| Model | Size | RAM Required | Speed |
|-------|------|--------------|-------|
| llama3 | 4.7 GB | 8 GB | Fast |
| mistral | 4.1 GB | 8 GB | Fast |
| deepseek-coder | 7.4 GB | 16 GB | Medium |
| qwen2 | 4.4 GB | 8 GB | Fast |
| phi3 | 2.2 GB | 4 GB | Very Fast |

Pull any model: `docker exec ollama ollama pull <model>`

## Project Structure

```
local-llm-setup/
├── docker-compose.yml      # Service orchestration
├── Dockerfile              # FastAPI container
├── setup.sh               # One-click setup
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── src/
│   ├── main.py            # FastAPI entry point
│   ├── config.py          # Configuration
│   ├── routers/
│   │   ├── chat.py        # Chat endpoints
│   │   ├── models.py      # Model management
│   │   └── rag.py         # RAG endpoints
│   └── utils/
│       └── rag.py         # RAG engine
├── examples/
│   ├── chat_example.py    # Chat usage
│   └── rag_example.py     # RAG usage
└── assets/
    └── banner.md          # Fiverr banner
```

## Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | http://localhost:11434 | Ollama server URL |
| `DEFAULT_MODEL` | llama3 | Default model |
| `PORT` | 8000 | FastAPI port |
| `CHUNK_SIZE` | 500 | RAG text chunk size |

## Production Deployment

### Without GPU
```bash
# Edit docker-compose.yml, remove GPU reservation
# Then:
docker compose up -d
```

### With Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name llm.example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

### Systemd Service
```ini
[Unit]
Description=Local LLM Setup
After=docker.service

[Service]
Type=oneshot
ExecStart=/path/to/setup.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Ollama won't start
```bash
docker logs ollama
# Check if port 11434 is in use
lsof -i :11434
```

### Out of memory
```bash
# Use a smaller model
docker exec ollama ollama pull phi3
# Or reduce context size in .env
```

### GPU not detected
```bash
# Check NVIDIA driver
nvidia-smi
# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

## License

MIT

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a PR

---

Built with ❤️ for the self-hosted AI community
