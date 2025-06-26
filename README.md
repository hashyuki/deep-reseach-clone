# Deep Research Clone

このプロジェクトは、React フロントエンドと LangGraph を活用したバックエンドエージェントを使用したフルスタックアプリケーションのデモンストレーションです。エージェントは、ユーザーのクエリに対して包括的な研究を実行するよう設計されており、動的に検索用語を生成し、Tavily Search API を使用してウェブを検索し、結果を反映して知識のギャップを特定し、十分にサポートされた引用付きの回答を提供できるまで検索を反復的に改良します。このアプリケーションは、LangGraph と OpenAI モデルを使用して研究強化された対話型 AI を構築する例として機能します。

<img src="./app.png" title="Deep Research Clone" alt="Deep Research Clone" width="90%">

## 機能

- 💬 React フロントエンドと LangGraph バックエンドを持つフルスタックアプリケーション
- 🧠 高度な研究と対話型 AI のための LangGraph エージェントを搭載
- 🔍 OpenAI モデルを使用した動的検索クエリ生成
- 🌐 Tavily Search API による統合ウェブ研究
- 🤔 知識のギャップを特定し検索を改良する反射的推論
- 📄 収集したソースからの引用付き回答を生成
- 🔄 開発中のフロントエンドとバックエンドの両方でホットリロード対応

## プロジェクト構造

プロジェクトは2つの主要なディレクトリに分かれています：

-   `frontend/`: Vite で構築された React アプリケーションが含まれています
-   `backend/`: 研究エージェントロジックを含む LangGraph/FastAPI アプリケーションが含まれています

## はじめに：開発とローカルテスト

開発とテスト用にアプリケーションをローカルで実行するには、以下の手順に従ってください。

**1. 前提条件：**

-   Node.js と npm (または yarn/pnpm)
-   Python 3.11+
-   uv (Python パッケージマネージャー)
-   **API キー**: バックエンドエージェントには OpenAI と Tavily の API キーが必要です

**2. クイックセットアップ:**

```bash
# プロジェクトルートで実行
./setup.sh
```

このスクリプトは以下を自動的に実行します：
- 前提条件のチェック (uv, Node.js, npm)
- バックエンドの依存関係のインストール (`uv sync`)
- フロントエンドの依存関係のインストール (`npm install`)
- 環境設定ファイルの確認

**3. API キーの設定:**

setup.sh の実行後、API キーを設定してください：

1.  `backend/` ディレクトリに移動します
2.  `backend/.env.example` ファイルをコピーして `.env` という名前のファイルを作成します
3.  `.env` ファイルを開いて API キーを追加します：
    - `OPENAI_API_KEY="YOUR_OPENAI_API_KEY"`
    - `TAVILY_API_KEY="YOUR_TAVILY_API_KEY"`

**4. アプリケーションの起動:**

```bash
# プロジェクトルートで実行
./start.sh
```

これによりバックエンド（ポート 8123）とフロントエンド（ポート 3000）の両方の開発サーバーが実行されます。

## 手動セットアップ（必要な場合）

自動セットアップを使用しない場合は、以下の手順で手動セットアップできます：

**バックエンド（uv を使用）:**

```bash
cd backend
uv sync
```

**フロントエンド:**

```bash
cd frontend
npm install
```

**個別実行:**

バックエンドとフロントエンドの開発サーバーを個別に実行することもできます。バックエンドの場合は、`backend/` ディレクトリでターミナルを開き、`langgraph dev` を実行します。バックエンド API は `http://127.0.0.1:8123` で利用できます。また、LangGraph UI のブラウザウィンドウも開きます。フロントエンドの場合は、`frontend/` ディレクトリでターミナルを開き、`npm run dev` を実行します。フロントエンドは `http://localhost:3000` で利用できます。

## バックエンドエージェントの動作（概要）

バックエンドのコアは `backend/src/graphs/research_graph.py` で定義された LangGraph エージェントです。以下の手順に従います：

<img src="./agent.png" title="Agent Flow" alt="Agent Flow" width="50%">

1.  **初期クエリの生成:** あなたの入力に基づいて、OpenAI GPT-4o-mini を使用して初期検索クエリのセットを生成します
2.  **ウェブ研究:** 各クエリに対して、Tavily Search API を使用して関連するウェブページと情報を見つけます
3.  **反映と知識ギャップ分析:** エージェントは検索結果を分析して、情報が十分かどうか、または知識のギャップがあるかどうかを判断します。この反映プロセスには OpenAI GPT-4o を使用します
4.  **反復的改良:** ギャップが見つかったり情報が不十分な場合、フォローアップクエリを生成し、ウェブ研究と反映の手順を繰り返します（設定された最大ループ数まで）
5.  **最終回答:** 研究が十分とみなされると、エージェントは収集した情報を OpenAI GPT-4o を使用してウェブソースからの引用を含む一貫した回答に統合します

## 設定

### モデル

使用するモデルは `backend/src/config/configuration.py` で設定できます：

- **クエリ生成**: `gpt-4o-mini` (デフォルト)
- **反映**: `gpt-4o` (デフォルト)
- **回答生成**: `gpt-4o` (デフォルト)

### 研究パラメータ

- **初期クエリ数**: 3 (デフォルト)
- **最大研究ループ数**: 2 (デフォルト)

## CLI の例

一回限りの質問をすばやく実行するには、コマンドラインからエージェントを実行できます。スクリプト `backend/examples/cli_research.py` は LangGraph エージェントを実行し、最終回答を出力します：

```bash
cd backend
python examples/cli_research.py "再生可能エネルギーの最新トレンドは何ですか？"
```

## デプロイメント

本番環境では、バックエンドサーバーが最適化された静的フロントエンドビルドを提供します。LangGraph には Redis インスタンスと Postgres データベースが必要です。Redis は pub-sub ブローカーとして使用され、バックグラウンド実行からのリアルタイム出力のストリーミングを可能にします。Postgres は、アシスタント、スレッド、実行の保存、スレッド状態と長期メモリの永続化、および「完全に一度」セマンティクスを持つバックグラウンドタスクキューの状態管理に使用されます。バックエンドサーバーのデプロイ方法の詳細については、[LangGraph Documentation](https://langchain-ai.github.io/langgraph/concepts/deployment_options/) をご覧ください。以下は、最適化されたフロントエンドビルドとバックエンドサーバーを含む Docker イメージを構築し、`docker-compose` で実行する例です。

_注意: docker-compose.yml の例では LangSmith API キーが必要です。[LangSmith](https://smith.langchain.com/settings) から取得できます。_

_注意: docker-compose.yml の例を実行していない場合、またはバックエンドサーバーを公開インターネットに公開していない場合は、`frontend/src/App.tsx` ファイルの `apiUrl` をあなたのホストに更新してください。現在、`apiUrl` は docker-compose 用に `http://localhost:8123`、開発用に `http://localhost:2024` に設定されています。_

**1. Docker イメージのビルド:**

   **プロジェクトルートディレクトリ**から以下のコマンドを実行します：
   ```bash
   docker build -t deep-research-clone -f Dockerfile .
   ```

**2. 本番サーバーの実行:**

   ```bash
   OPENAI_API_KEY=<your_openai_api_key> TAVILY_API_KEY=<your_tavily_api_key> LANGSMITH_API_KEY=<your_langsmith_api_key> docker-compose up
   ```

ブラウザで `http://localhost:8123/app/` にアクセスしてアプリケーションを確認してください。API は `http://localhost:8123` で利用できます。

## 使用技術

- [React](https://reactjs.org/) ([Vite](https://vitejs.dev/) 使用) - フロントエンドユーザーインターフェース用
- [Tailwind CSS](https://tailwindcss.com/) - スタイリング用
- [Shadcn UI](https://ui.shadcn.com/) - コンポーネント用
- [LangGraph](https://github.com/langchain-ai/langgraph) - バックエンド研究エージェントの構築用
- [OpenAI](https://openai.com/) - クエリ生成、反映、回答統合のための LLM
- [Tavily](https://tavily.com/) - 情報収集のためのウェブ検索 API

## ライセンス

このプロジェクトは Apache License 2.0 の下でライセンスされています。詳細は [LICENSE](LICENSE) ファイルをご覧ください。