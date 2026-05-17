#主に知識のデータベースを構築、更新する.
#YAMLから読み込んだ設定を反映させる。
#ファイルが新しくなったり更新されたり消えたりがあるかを確認して処理する。
#文字をベクトルにデータ加工する

#標準ライブラリ
import json, os
from datetime import datetime
from pathlib import Path
#設定、ドキュメント操作（情報の抽出とルールの読み込み）
import fitz, yaml
#LangChain関連（バラバラの工程を一つのレールを敷いて進めるためのレール）
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
#AIモデル関連（ベクトルDBと通訳）
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- 設定読み込み ---
with open("config.yaml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

DOCS_DIR        = Path(cfg["paths"]["docs_dir"])
VECTORSTORE_DIR = cfg["paths"]["vectorstore_dir"]
INGESTED_LOG    = Path(cfg["paths"]["ingested_log"])
CHUNK_SIZE      = cfg["rag"]["chunk_size"]
CHUNK_OVERLAP   = cfg["rag"]["chunk_overlap"]
EMBED_MODEL     = cfg["embedding"]["model"]
SUPPORTED_EXT   = {".pdf", ".md", ".txt"}  # 対応ファイル形式(知らないファイル形式は無視する安全装置)

# --- 取り込み済みログの読み書き ---
def load_ingested_log():
    # 過去に処理したファイルの記録を読む
    if INGESTED_LOG.exists():
        with open(INGESTED_LOG, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_ingested_log(log):
    # 処理済みファイルの記録を保存
    INGESTED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(INGESTED_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def get_mtime(path):
    # ファイルの最終更新日時を取得
    return datetime.fromtimestamp(path.stat().st_mtime).isoformat()

# --- ファイル変更検知 ---

def get_all_docs():
    # docsフォルダ内の対応ファイルを全取得（対応してる拡張子以外のファイルは無視）
    return [p for p in DOCS_DIR.rglob("*") if p.suffix in SUPPORTED_EXT]

def get_changed_files(all_files, log):
    # 新規 or 更新されたファイルだけ返す
    return [f for f in all_files if str(f) not in log or log[str(f)] != get_mtime(f)]

def get_deleted_files(all_files, log):
    # docsから消えたファイルを検知
    current_keys = {str(f) for f in all_files}
    return [k for k in log if k not in current_keys]

# --- ドキュメント読み込み ---
#バラバラの形式（pdf,text,markdown）を文字列に揃える
def load_document(path):
    # PDF：pymupdfでテキスト抽出、MD/TXT：そのまま読む
    if path.suffix == ".pdf":
        doc = fitz.open(str(path))
        return "\n".join(page.get_text() for page in doc)
    elif path.suffix in {".md", ".txt"}:
        with open(path, encoding="utf-8") as f:
            return f.read()
    return ""

# --- メイン処理 ---
def build_vectorstore(force=False):
    print("🔍 Embeddingモデルを読み込み中...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = Chroma(persist_directory=VECTORSTORE_DIR, embedding_function=embeddings)
    log = {} if force else load_ingested_log()
    all_files = get_all_docs()

    # 削除されたファイルをDBからも消す　ids:ID番号
    for key in get_deleted_files(all_files, log):
        results = vectorstore.get(where={"source": key})
        if results["ids"]:
            vectorstore.delete(ids=results["ids"])
        del log[key]

    # 変更ファイルだけ再Embedding
    changed = all_files if force else get_changed_files(all_files, log)
    if not changed:
        print("✅ 変更なし。既存のインデックスを使用します。")
        return vectorstore
    
    print(f"📄 処理対象: {len(changed)}件")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "、", " ", ""],  # 日本語対応の区切り文字
    )

    for path in changed:
        print(f"   ⚙️  {path.name}")
        # 既存データを削除してから再登録
        existing = vectorstore.get(where={"source": str(path)})
        if existing["ids"]:
            vectorstore.delete(ids=existing["ids"])
        text = load_document(path)
        if not text.strip():
            continue
        chunks = splitter.split_text(text)
        docs = [
            Document(
                page_content=c,
                metadata={"source": str(path), "filename": path.name, "chunk_index": i}
            )
            for i, c in enumerate(chunks)
        ]
        vectorstore.add_documents(docs)
        log[str(path)] = get_mtime(path)
        print(f"   ✅ {path.name} → {len(chunks)}チャンク")

    save_ingested_log(log)
    print(f"\n🎉 完了。合計: {len(log)}件")
    return vectorstore

def get_vectorstore():
    return build_vectorstore(force=False)