# knowledge_bot
# knowledge_bot

PDF や Markdown ドキュメントに基づいて、AI が社内ナレッジを高速に検索・回答する RAG チャットボットです。

## 🚀 概要
Google Colab などの環境から手軽に起動し、社内の製品マニュアルや提案書をインデックス化できるシステムです。無料枠で利用可能な LLM（Groq）や組み込み型の Vector DB（ChromaDB）を組み合わせることで、コストを抑えつつ高速かつ高精度なドキュメント検索・回答生成（RAG）を実現しています。

## ✨ 主な機能
- **差分永続化インデックス（高速な起動コスト）**：`docs/` フォルダ内のファイル変更や削除を自動で検知し、更新されたドキュメントのみを再 Embedding します。
- **ドキュメント外の情報を答えない制約（ハルシネーションの抑制）**：システムプロンプトによる厳格なルール設定により、確実なソースに基づいた簡潔な回答のみを行います。
- **引用元（根拠ソース）の可視化**：Streamlit の UI 上で、AI が回答の根拠としたドキュメント名や該当チャンクのテキストを即座に確認できます。
- **ngrok による簡単外部公開**：ローカル環境や Colab 上で起動した Streamlit アプリへのアクセス URL を安全に自動生成します。

## 🛠️ 使用技術 (Tech Stack)

### AI / RAG Framework
- **Python 3**
- **LangChain / LangChain Community**: RAG チェーンの構築およびドキュメント処理
- **Groq (llama-3.3-70b-versatile)**: 高速かつ無料枠で使える高性能 LLM
- **HuggingFaceEmbeddings (intfloat/multilingual-e5-small)**: 日本語対応の無料 Embedding モデル

### Data / Vector DB
- **ChromaDB (langchain-chroma)**: 差分取り込みに対応したローカル永続化ベクトルデータベース
- **PyMuPDF (fitz)**: PDF ドキュメントからの高精度なテキスト抽出

### UI / Infrastructure
- **Streamlit**: 直感的でレスポンシブなチャット UI の提供
- **pyngrok**: ローカルサーバー（Port: 8501）のセキュアなトンネリングおよび外部公開

## 💡 こだわった点・工夫したポイント
- **スマートな差分インジェスト機能 (`ingest.py`)**
  ドキュメントの追加・変更・削除を `ingested.json` で管理しています。毎回すべてのドキュメントを Embedding し直す必要がないため、起動コストを最小限に抑え、API の無駄な消費を防ぎます。
- **設定ファイルの一元管理 (`config.yaml`)**
  LLM のモデル名、Temperature、RAG のチャンクサイズ（デフォルト: 600、Overlap: 100）などのパラメータを `config.yaml` に切り離しています。コードを一切汚さずに、実験やチューニングが可能です。
- **ユーザーフレンドリーな UI/UX**
  サイドバーから「現在インデックスされているファイル」が一目で分かり、ドキュメントを追加した際も Streamlit 画面上のボタンひとつでインデックスの再構築が可能です。

## ⚙️ ローカルでの起動方法

### 1. クローンと依存関係のインストール
```bash
git clone [https://github.com/Yyuiiu/knowledge_bot.git](https://github.com/Yyuiiu/knowledge_bot.git)
cd knowledge_bot
pip install -r requirements.txt

# knowledge_bot

An AI-powered RAG chatbot that quickly searches and answers questions based on your PDF and Markdown documents.

## 🚀 Overview
This system allows you to easily index company documents (such as product manuals or proposals) directly from environments like Google Colab or local machines. By combining a free-tier high-performance LLM (Groq) with an embedded Vector DB (ChromaDB), it delivers high-speed, high-accuracy Document Retrieval-Augmented Generation (RAG) while keeping costs at zero.

## ✨ Key Features
- **Incremental Indexing (Low Startup Cost)**: Automatically detects changes, additions, or deletions of files in the `docs/` folder, and only re-embeds the updated documents.
- **Strict Hallucination Prevention**: System prompts enforce strict constraints, ensuring the AI only provides concise answers based directly on the provided context without hallucinating outside information.
- **Source Citation Visibility**: Users can immediately review the exact document names and text chunks that the AI used as a basis for its response directly on the Streamlit UI.
- **Easy Deployment via ngrok**: Automatically generates a secure public URL for the Streamlit application running on a local machine or Colab environment.

## 🛠️ Tech Stack

### AI / RAG Framework
- **Python 3**
- **LangChain / LangChain Community**: RAG chain orchestration and document processing
- **Groq (llama-3.3-70b-versatile)**: Fast and free-tier high-performance LLM
- **HuggingFaceEmbeddings (intfloat/multilingual-e5-small)**: High-quality multilingual embedding model

### Data / Vector DB
- **ChromaDB (langchain-chroma)**: Persistent local vector database supporting incremental updates
- **PyMuPDF (fitz)**: High-precision text extraction from PDF documents

### UI / Infrastructure
- **Streamlit**: Intuitive and responsive chat interface
- **pyngrok**: Secure tunneling and public exposure for the local server (Port: 8501)

## 💡 Key Highlights & Optimizations
- **Smart Incremental Ingestion (`ingest.py`)**
  Document statuses are managed via `ingested.json`. There is no need to re-embed all documents every time the application starts, minimizing startup time and avoiding unnecessary API consumption.
- **Centralized Configuration (`config.yaml`)**
  Parameters such as LLM model names, temperature, and RAG chunk sizes (default: 600, overlap: 100) are isolated into `config.yaml`. You can experiment and tune parameters seamlessly without modifying the core codebase.
- **User-Friendly UI/UX**
  The sidebar displays currently indexed files at a glance. When new documents are added, you can rebuild the vector index with a single click of a button right on the Streamlit screen.

## ⚙️ Local Setup & Getting Started

### 1. Clone the Repository and Install Dependencies
```bash
git clone [https://github.com/Yyuiiu/knowledge_bot.git](https://github.com/Yyuiiu/knowledge_bot.git)
cd knowledge_bot
pip install -r requirements.txt

# knowledge_bot

基於 PDF 和 Markdown 文件，利用 AI 實現企業知識庫高效檢索與問答的 RAG 智能聊天機器人。

## 🚀 專案概述
本專案支援從 Google Colab 或在地環境輕鬆啟動，能夠快速對企業內部產品手冊、技術文件或提案進行索引。透過結合免費的高性能大語言模型（Groq）與在地嵌入式向量資料庫（ChromaDB），在實現零成本運行的同時，保障了文件檢索與生成（RAG）的高速與高精準度。

## ✨ 核心功能
- **增量索引（極低啟動成本）**：自動檢測 `docs/` 資料夾內檔案的增加、修改或刪除，僅對發生變化的文件進行重新嵌入（Embedding）處理。
- **嚴控幻覺（基於事實回答）**：透過嚴格的系統提示詞（System Prompt）進行約束，確保 AI 僅根據現有文件內容提供簡明扼要的回答，杜絕憑空捏造。
- **來源文件追溯（視覺化引用）**：在 Streamlit 聊天畫面上，使用者可以直觀地查看 AI 生成回答時所引用的文件名稱及具體的文字片段（Chunks）。
- **透過 ngrok 快速一鍵外網公開**：自動為在地或 Colab 上運行的 Streamlit 服務（預設連接埠 8501）生成安全的公共存取連結。

## 🛠️ 技術棧 (Tech Stack)

### AI / RAG 框架
- **Python 3**
- **LangChain / LangChain Community**：RAG 鏈構建及文件處理
- **Groq (llama-3.3-70b-versatile)**：高速且提供免費額度的高性能 LLM
- **HuggingFaceEmbeddings (intfloat/multilingual-e5-small)**：支援多語言的高效免費嵌入模型

### 資料 / 向量資料庫
- **ChromaDB (langchain-chroma)**：支援增量更新的在地持久化向量資料庫
- **PyMuPDF (fitz)**：從 PDF 文件中進行高精度文字擷取

### 前端 UI / 基礎設施
- **Streamlit**：提供直觀、響應式的聊天互動介面
- **pyngrok**：為在地伺服器（Port: 8501）提供安全隧道及外網對映

## 💡 專案亮點與優化
- **智能增量資料導入 (`ingest.py`)**
  透過 `ingested.json` 記錄和管理文件狀態。無需在每次啟動時重新對所有文件進行向量化，大幅縮短啟動時間，同時避免了不必要的 API 消耗。
- **設定參數統一管理 (`config.yaml`)**
  將 LLM 模型名稱、Temperature、RAG 切片大小（預設：600，Overlap：100）等核心參數抽離至 `config.yaml`。無需修改任何核心程式碼即可輕鬆進行調優和實驗。
- **使用者友好的 UI/UX 設計**
  側邊欄一目了然地展示目前已建索引的文件。當使用者往目錄添加新文件後，只需在 Streamlit 畫面上點擊按鈕即可一鍵更新向量資料庫。

## ⚙️ 在地運行指南

### 1. 複製專案並安裝依賴
```bash
git clone [https://github.com/Yyuiiu/knowledge_bot.git](https://github.com/Yyuiiu/knowledge_bot.git)
cd knowledge_bot
pip install -r requirements.txt