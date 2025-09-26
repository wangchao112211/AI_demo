# streamlit_app.py

import streamlit as st
import requests
import json
from typing import Dict, Any

# ---------- 页面配置 ----------
st.set_page_config(
    page_title="大模型 Playground",
    page_icon="🤖",
    layout="centered"
)

# ---------- 侧边栏 ----------
with st.sidebar:
    st.title("⚙️ 参数配置")
    api_url = st.text_input(
        "模型接口地址",
        value="https://api.openai.com/v1/chat/completions",
        help="支持任何兼容 OpenAI 格式的接口"
    )
    api_key = st.text_input(
        "API Key",
        type="password",
        help="留空则默认不携带 Authorization 头"
    )
    model_name = st.text_input(
        "模型名称",
        value="gpt-3.5-turbo"
    )
    max_tokens = st.slider("max_tokens", 0, 4096, 512)
    temperature = st.slider("temperature", 0.0, 2.0, 0.7)
    top_p = st.slider("top_p", 0.0, 1.0, 1.0)
    system_prompt = st.text_area(
        "System Prompt（可选）",
        value="You are a helpful assistant."
    )

# ---------- 主界面 ----------
st.title("🤖 大模型 Playground")
st.markdown("输入消息，点击发送即可调用大模型并获得回复。")

# 会话历史，使用 st.session_state 持久化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 展示历史对话
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入框
if prompt := st.chat_input("请输入你的问题…"):
    # 1. 先把用户消息写入会话
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 构造请求体
    headers = {"Content-Type": "application/json"}
    if api_key.strip():
        headers["Authorization"] = f"Bearer {api_key.strip()}"

    payload = {
        "model": model_name,
        "messages": [{"role": "system", "content": system_prompt}] +
                   st.session_state.messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "stream": False
    }

    # 3. 调用模型
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("🧠 *思考中…*")
        try:
            resp = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=60)
            resp.raise_for_status()
            answer = resp.json()["choices"][0]["message"]["content"]
            placeholder.markdown(answer)
            # 4. 把助手回复写入会话
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            placeholder.error(f"调用失败：{e}")

# 一键清空
if st.button("🗑️ 清空对话"):
    st.session_state.messages = []
    st.rerun()