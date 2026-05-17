import os
from dotenv import load_dotenv
load_dotenv()

#チャットとUIの表示操作、ブラウザ上で動く画面
#
#
#


import streamlit as st
import os

from ingest import get_vectorstore
from rag import build_rag_chain, query

# --- ページ設定 ---
st.set_page_config(
    page_title="社内ナレッジ検索ボット",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 書類検索ボット")
st.caption("PDF・Markdownに基づいてAIが回答します")

# --- 初期化（起動時に1回だけ実行） ---
@st.cache_resource #一度この関数(initialize)が実行されたら結果を保存しておく
def initialize():
    # vectorstoreとRAGチェーンをキャッシュして毎回の初期化を防ぐ
    vectorstore = get_vectorstore()
    chain, retriever = build_rag_chain(vectorstore)
    return chain, retriever

# APIキーチェック
if not os.environ.get("GROQ_API_KEY"):
    st.error("⚠️ GROQ_API_KEY が設定されていません。.envファイルを確認してください。")
    st.stop()

# サイドバーに再読み込みボタン
with st.sidebar:
    st.header("⚙️ 設定")
    if st.button("🔄 ドキュメントを再読み込み"):
        st.cache_resource.clear()
        st.rerun()
        
chain, retriever = initialize()

# --- チャット履歴の管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去のチャット履歴を表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- チャット入力 ---
if prompt := st.chat_input("質問を入力してください..."):

    # ユーザーメッセージを表示・保存
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AIの回答を生成
    with st.chat_message("assistant"):
        with st.spinner("検索中..."):
            result = query(chain, retriever, prompt)

        st.markdown(result["answer"])

        # 根拠チャンクを折りたたみで表示
        if result["sources"]:
            with st.expander("📄 参考にしたドキュメント"):
                for src in result["sources"]:
                    st.markdown(f"**{src['filename']}**（チャンク {src['chunk_index']}）")
                    st.caption(src["content"])
                    st.divider()

    # アシスタントの回答を履歴に保存
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"]
    })