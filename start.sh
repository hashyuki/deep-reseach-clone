#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Deep Research Clone を起動しています...${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo -e "\n${RED}サービスを終了しています...${NC}"
    # Kill all child processes
    pkill -P $$
    exit 0
}

# Set up trap for cleanup on script exit
trap cleanup INT TERM

# Start backend
echo -e "${GREEN}バックエンド (LangGraph) を起動しています...${NC}"
cd backend && uv run langgraph dev --port 8123 &
BACKEND_PID=$!

# Wait a bit for backend to start
echo -e "${BLUE}バックエンドの初期化を待機しています...${NC}"
sleep 5

# Start frontend
echo -e "${GREEN}フロントエンド (Next.js) を起動しています...${NC}"
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✓ 両方のサービスが起動中です！${NC}"
echo -e "${BLUE}バックエンド (LangGraph API): http://localhost:8123${NC}"
echo -e "${BLUE}フロントエンド (Next.js): http://localhost:3000${NC}"
echo ""
echo -e "${RED}Ctrl+C ですべてのサービスを停止${NC}"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID