import streamlit as st
import requests
from typing import Dict, Any
import time

# 配置
API_BASE_URL = "http://localhost:8000/api/v1"


def init_session_state():
    """初始化会话状态"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(int(time.time()))


def upload_file(file) -> Dict[str, Any]:
    """上传文件到后端"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        return response.json()
    except Exception as e:
        return {"error": f"上传失败: {str(e)}"}


def query_documents(question: str, session_id: str) -> Dict[str, Any]:
    """查询文档"""
    try:
        data = {
            "question": question,
            "session_id": session_id,
            "max_results": 5
        }
        response = requests.post(f"{API_BASE_URL}/query", json=data)
        return response.json()
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}


def get_document_info() -> Dict[str, Any]:
    """获取文档信息"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents")
        return response.json()
    except Exception as e:
        return {"error": f"获取信息失败: {str(e)}"}


def clear_documents() -> Dict[str, Any]:
    """清空所有文档"""
    try:
        response = requests.delete(f"{API_BASE_URL}/documents")
        return response.json()
    except Exception as e:
        return {"error": f"清空失败: {str(e)}"}


def clear_memory() -> Dict[str, Any]:
    """清空对话记忆"""
    try:
        response = requests.post(f"{API_BASE_URL}/memory/clear")
        return response.json()
    except Exception as e:
        return {"error": f"清空记忆失败: {str(e)}"}


def main():
    st.set_page_config(
        page_title="智能文档问答系统",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()

    st.title("🤖 智能文档问答系统")
    st.markdown("基于大模型的Agent+RAG应用")

    # 侧边栏
    with st.sidebar:
        st.header("📁 文档管理")

        # 文件上传
        uploaded_file = st.file_uploader(
            "选择文档",
            type=['pdf', 'docx', 'txt'],
            help="支持PDF、Word和文本文件"
        )

        if uploaded_file is not None:
            if st.button("上传文档", type="primary"):
                with st.spinner("正在处理文档..."):
                    result = upload_file(uploaded_file)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(f"文档上传成功！生成了 {result.get('chunks_count', 0)} 个文档块")

        st.divider()

        # 文档信息
        if st.button("查看文档信息"):
            with st.spinner("获取文档信息..."):
                info = get_document_info()
                if "error" in info:
                    st.error(info["error"])
                else:
                    st.info(f"已存储文档数量: {info.get('total_documents', 0)}")

        # 清空操作
        st.header("🗑️ 清空操作")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("清空文档", type="secondary"):
                result = clear_documents()
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("所有文档已清空")

        with col2:
            if st.button("清空记忆", type="secondary"):
                result = clear_memory()
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("对话记忆已清空")
                    st.session_state.messages = []

    # 主界面
    st.header("💬 对话界面")

    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

            # 显示源信息
            if message["role"] == "assistant" and "sources" in message:
                if message["sources"]:
                    with st.expander("查看引用来源"):
                        for i, source in enumerate(message["sources"]):
                            st.write(f"**来源 {i + 1}:** {source['source']}")
                            st.write(f"**相似度:** {source['score']:.3f}")
                            st.write(f"**内容预览:** {source['content_preview']}")
                            st.divider()

    # 用户输入
    if prompt := st.chat_input("请输入您的问题"):
        # 显示用户消息
        with st.chat_message("user"):
            st.write(prompt)

        # 添加到会话状态
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 查询并显示回答
        with st.chat_message("assistant"):
            with st.spinner("正在思考..."):
                response = query_documents(prompt, st.session_state.session_id)

                if "error" in response:
                    st.error(f"查询失败: {response['error']}")
                else:
                    st.write(response["answer"])

                    # 显示元信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("置信度", f"{response['confidence']:.3f}")
                    with col2:
                        st.metric("检索文档数", response['retrieved_count'])
                    with col3:
                        st.metric("处理时间", f"{response['processing_time']:.2f}s")

                    # 添加到会话状态
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response["sources"],
                        "confidence": response["confidence"]
                    })
