#!/bin/bash
# Local LLM Setup — One-click installation
set -e

echo "=========================================="
echo "  Local LLM Setup — One-Click Install"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker not found. Install Docker first.${NC}"
    echo "https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose not found.${NC}"
    exit 1
fi

echo -e "${GREEN}[1/4] Starting services...${NC}"
docker compose up -d --build

echo ""
echo -e "${GREEN}[2/4] Waiting for Ollama to be ready...${NC}"
for i in $(seq 1 30); do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}Ollama is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}Ollama taking long to start. Check with: docker logs ollama${NC}"
    fi
    sleep 2
done

echo ""
echo -e "${GREEN}[3/4] Pulling default model (llama3)...${NC}"
echo "This may take a few minutes on first run..."
docker exec ollama ollama pull llama3 || echo -e "${YELLOW}Model pull failed. You can pull manually later.${NC}"

echo ""
echo -e "${GREEN}[4/4] Setup complete!${NC}"
echo ""
echo "=========================================="
echo "  Services are running:"
echo "=========================================="
echo ""
echo "  🌐 Open WebUI:  http://localhost:3000"
echo "  🔗 API:         http://localhost:8000"
echo "  📚 API Docs:    http://localhost:8000/docs"
echo "  🤖 Ollama:      http://localhost:11434"
echo ""
echo "=========================================="
echo "  Quick commands:"
echo "=========================================="
echo ""
echo "  docker compose logs -f        # View logs"
echo "  docker compose down           # Stop services"
echo "  docker compose up -d          # Start services"
echo "  docker exec ollama ollama list # List models"
echo ""
echo -e "${GREEN}Happy chatting with your local LLM! 🚀${NC}"
