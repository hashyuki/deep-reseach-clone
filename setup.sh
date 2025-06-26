#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Deep Research Clone セットアップを開始します...${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}前提条件をチェックしています...${NC}"

# Check for uv
if ! command_exists uv; then
    echo -e "${RED}エラー: uv がインストールされていません。${NC}"
    echo -e "${YELLOW}以下のコマンドでインストールしてください:${NC}"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check for Node.js and npm
if ! command_exists node; then
    echo -e "${RED}エラー: Node.js がインストールされていません。${NC}"
    echo -e "${YELLOW}https://nodejs.org/ からインストールしてください。${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}エラー: npm がインストールされていません。${NC}"
    echo -e "${YELLOW}Node.js とともにインストールされるはずです。${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 前提条件はすべて満たされています${NC}"
echo ""

# Install backend dependencies
echo -e "${GREEN}バックエンドの依存関係をインストールしています (uv sync)...${NC}"
cd backend

if ! uv sync; then
    echo -e "${RED}エラー: バックエンドの依存関係のインストールに失敗しました${NC}"
    exit 1
fi

echo -e "${GREEN}✓ バックエンドの依存関係のインストールが完了しました${NC}"
echo ""

# Go back to root and install frontend dependencies
cd ..
echo -e "${GREEN}フロントエンドの依存関係をインストールしています (npm install)...${NC}"
cd frontend

if ! npm install; then
    echo -e "${RED}エラー: フロントエンドの依存関係のインストールに失敗しました${NC}"
    exit 1
fi

echo -e "${GREEN}✓ フロントエンドの依存関係のインストールが完了しました${NC}"
echo ""

# Go back to root
cd ..

# Check for .env file
echo -e "${BLUE}環境設定をチェックしています...${NC}"
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  backend/.env ファイルが見つかりません${NC}"
    echo -e "${BLUE}backend/.env.example をコピーして .env ファイルを作成し、APIキーを設定してください:${NC}"
    echo ""
    echo -e "${YELLOW}cp backend/.env.example backend/.env${NC}"
    echo ""
    echo -e "${BLUE}そして backend/.env ファイルを編集して以下のAPIキーを設定してください:${NC}"
    echo -e "${YELLOW}OPENAI_API_KEY=your_openai_api_key_here${NC}"
    echo -e "${YELLOW}TAVILY_API_KEY=your_tavily_api_key_here${NC}"
    echo ""
else
    echo -e "${GREEN}✓ backend/.env ファイルが見つかりました${NC}"
fi

echo ""
echo -e "${GREEN}🎉 セットアップが完了しました！${NC}"
echo ""
echo -e "${BLUE}次のステップ:${NC}"
echo -e "${YELLOW}1. backend/.env ファイルでAPIキーが正しく設定されていることを確認${NC}"
echo -e "${YELLOW}2. ./start.sh を実行してアプリケーションを起動${NC}"
echo ""
echo -e "${BLUE}アプリケーション起動後のURL:${NC}"
echo -e "${GREEN}• フロントエンド: http://localhost:3000${NC}"
echo -e "${GREEN}• バックエンドAPI: http://localhost:8123${NC}"