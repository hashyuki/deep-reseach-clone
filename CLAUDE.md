# CLAUDE.md

このファイルは、このリポジトリでコードを扱う際の Claude Code (claude.ai/code)へのガイダンスを提供します。

## プロジェクト概要

Deep Research Clone - LangGraph を使用して包括的なウェブリサーチを引用付きで実行するフルスタック AI リサーチアシスタント。システムは動的に検索クエリを生成し、反復的なリサーチを実行し、十分にサポートされた回答を提供します。

## アーキテクチャ

**モノレポ構造:**

- `backend/` - LangGraph/FastAPI Python バックエンド (ポート 8123)
- `frontend/` - Next.js React フロントエンド (ポート 3000)

**主要技術:**

- バックエンド: Python 3.12+, LangGraph, FastAPI, OpenAI, Tavily Search API
- フロントエンド: Next.js 15.3.4, React 19, Tailwind CSS v4, Shadcn UI
- インフラ: Redis (pub-sub), PostgreSQL (状態永続化)

## よく使う開発コマンド

### クイックスタート

```bash
./setup.sh    # すべての依存関係をインストール
./start.sh    # フロントエンドとバックエンドの両方を起動
```

### バックエンド開発

```bash
cd backend
uv sync                    # 依存関係のインストール/更新
langgraph dev             # 開発サーバーを起動 (ポート 8123)
uv run mypy src           # 型チェック
uv run ruff check src     # リンティング
uv run ruff format src    # コードフォーマット
```

### フロントエンド開発

```bash
cd frontend
npm install               # 依存関係をインストール
npm run dev              # Turbopackで開発サーバーを起動 (ポート 3000)
npm run build            # 本番用ビルド
npm run lint             # Next.jsリンティング
```

### テスト

```bash
# CLIテスト
cd backend && python examples/cli_research.py "あなたの質問をここに"

# Jupyterノートブックは backend/test-agent.ipynb で利用可能
```

## 環境設定

`backend/.env` を作成:

```
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
LANGSMITH_API_KEY=your_key_here  # オプション、デプロイメント監視用
```

## エージェントワークフローアーキテクチャ

リサーチエージェント (`backend/src/graphs/research_graph.py`) は以下のステートマシンに従います:

1. **generate_queries** → ユーザー入力から初期検索クエリを作成
2. **web_research** → Tavily API を使用してウェブを検索
3. **reflect** → 知識のギャップを分析
4. **generate_followup_queries** → 必要に応じて追加クエリを作成 (web_research にループバック)
5. **generate_answer** → 引用付きで調査結果をまとめる

**設定** (`backend/src/config/configuration.py`):

- クエリ生成: GPT-4o-mini
- 反映と回答: GPT-4o
- 最大リサーチループ数: 2
- 初期クエリ数: 3

## コード構成

### バックエンド構造

- `src/api/` - FastAPI アプリケーションとルート
- `src/graphs/` - LangGraph エージェント定義
- `src/nodes/` - 個別のグラフノード実装
- `src/prompts/` - LLM プロンプトテンプレート
- `src/schemas/` - Pydantic データモデル
- `src/states/` - エージェントの状態管理
- `src/utils/` - ユーティリティ関数

### フロントエンド構造

- `app/` - Next.js app router ページ
- `components/` - 再利用可能な UI コンポーネント
- `features/` - 機能固有のコンポーネント
- `lib/` - ユーティリティ関数と LangGraph SDK 統合

## 重要な注意事項

- プロジェクトはデフォルトで日本語に設定されています
- 最新の Python ツールの`uv`パッケージマネージャーを使用
- フロントエンドは高速開発のため Next.js Turbopack を使用
- 本番環境では、バックエンドが最適化されたフロントエンドビルドを提供
- エージェントは Redis pub-sub 経由でストリーミングレスポンスをサポート

## デプロイメント

本番デプロイメントは Docker を使用:

```bash
docker build -t deep-research-clone -f Dockerfile .
docker-compose up  # 環境変数としてAPIキーが必要
```

アプリケーションへのアクセス: `http://localhost:8123/app/`
