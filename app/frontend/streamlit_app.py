# app/frontend/streamlit_app.py
import streamlit as st
import pandas as pd
import requests
from typing import Dict, Any

def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None

def main():
    st.set_page_config(page_title="Finance QA System", layout="wide")
    init_session_state()

    # 侧边栏设置
    with st.sidebar:
        st.title("设置")
        api_key = st.text_input("API Key", type="password")
        if api_key:
            st.session_state.api_key = api_key

    # 主界面
    st.title("金融问答系统")

    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["问答系统", "数据查询", "结果分析"])

    with tab1:
        # 显示历史消息
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # 输入框
        if prompt := st.chat_input("输入你的问题..."):
            # 添加用户消息
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # 调用API获取回答
            if st.session_state.api_key:
                with st.spinner("思考中..."):
                    try:
                        response = requests.post(
                            "https://api.example.com/qa",
                            json={"question": prompt},
                            headers={"Authorization": f"Bearer {st.session_state.api_key}"}
                        )
                        answer = response.json()["answer"]
                        
                        # 添加助手消息
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        with st.chat_message("assistant"):
                            st.write(answer)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("请先设置API Key")

    with tab2:
        st.header("SQL查询")
        sql_query = st.text_area("输入SQL查询语句")
        if st.button("执行查询"):
            if st.session_state.api_key and sql_query:
                with st.spinner("执行查询中..."):
                    try:
                        response = requests.post(
                            "https://api.example.com/query",
                            json={"sql": sql_query},
                            headers={"Authorization": f"Bearer {st.session_state.api_key}"}
                        )
                        results = response.json()
                        if results:
                            st.dataframe(pd.DataFrame(results))
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with tab3:
        st.header("结果分析")
        if st.session_state.messages:
            # 计算统计信息
            total_questions = len([m for m in st.session_state.messages if m["role"] == "user"])
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("总问题数", total_questions)
            with col2:
                st.metric("平均响应时间", "2.3s")
            with col3:
                st.metric("准确率", "85%")

            # 添加图表
            chart_data = pd.DataFrame({
                "类型": ["初级问题", "中级问题", "高级问题"],
                "准确率": [0.95, 0.85, 0.75]
            })
            st.bar_chart(chart_data.set_index("类型"))

if __name__ == "__main__":
    main()