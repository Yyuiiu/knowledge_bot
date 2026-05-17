#質問を受け取って回答を返すファイル
#質問→ChromaDBでチャンク検索→チャンクと質問をLLMに質問を送る→回答チャンクを返す

import os, yaml
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# --- 設定読み込み ---
with open("config.yaml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

LLM_MODEL   = cfg["llm"]["model"]
TEMPERATURE = cfg["llm"]["temperature"]
MAX_TOKENS  = cfg["llm"]["max_tokens"]
TOP_K       = cfg["rag"]["top_k"]

# --- システムプロンプト ---
SYSTEM_PROMPT = """
あなたは社内ナレッジベースの検索アシスタントです。
以下の「参考ドキュメント」に基づいて、ユーザーの質問に日本語で回答してください。

ルール：
- 参考ドキュメントに記載のない情報は「ドキュメントに記載がありません」と答える
- 推測や憶測で回答しない
- 回答は簡潔かつ具体的に

参考ドキュメント：
{context}
"""

def build_rag_chain(vectorstore):
    # LLM（Groq）の初期化
    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        api_key=os.environ.get("GROQ_API_KEY")
    )

    # ChromaDBから類似チャンクを取得するRetriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K}
    )

    # プロンプトの組み立て
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

    return None, retriever  # chainはquery内で組み立てる

def query(chain, retriever, question):
    with open("config.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    llm = ChatGroq(
        model=cfg["llm"]["model"],
        temperature=cfg["llm"]["temperature"],
        max_tokens=cfg["llm"]["max_tokens"],
        api_key=os.environ.get("GROQ_API_KEY")
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

    # 関連チャンクを取得
    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)

    # LLMに送って回答取得
    messages = prompt.format_messages(context=context, input=question)
    response = llm.invoke(messages)

    # 根拠チャンクを整形
    sources, seen = [], set()
    for doc in docs:
        meta = doc.metadata
        key = (meta.get("filename"), meta.get("chunk_index"))
        if key not in seen:
            seen.add(key)
            sources.append({
                "filename": meta.get("filename", "不明"),
                "source": meta.get("source", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "content": doc.page_content
            })

    return {"answer": response.content, "sources": sources}