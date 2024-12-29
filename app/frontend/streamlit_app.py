# app/frontend/streamlit_app.py
import streamlit as st
from tabs.qa_tab import render_qa_tab
from tabs.query_tab import render_query_tab
from tabs.analysis_tab import render_analysis_tab
from tabs.basic_tab import render_basic_tab
from tabs.intermediate_tab import render_intermediate_tab
from tabs.advanced_tab import render_advanced_tab

def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = "e887aa6e3e95a3ecb4b83b39f209fb36.v3bZo1pwyPrmajD3"
    if 'base_url' not in st.session_state:
        st.session_state.base_url = "https://open.bigmodel.cn/api/paas/v4/"
    if 'model' not in st.session_state:
        st.session_state.model = "glm-4-plus"

def main():
    st.set_page_config(page_title="Finance QA System", layout="wide")
    init_session_state()

    with st.sidebar:
        st.title("设置")
        # API设置
        st.subheader("API设置")
        api_key = st.text_input("API Key", type="password")
        base_url = st.text_input("API Base URL", value=st.session_state.base_url)
        model = st.text_input("模型", value=st.session_state.model)
        
        if api_key:
            st.session_state.api_key = api_key
        if base_url:
            st.session_state.base_url = base_url
        if model:
            st.session_state.model = model

    st.title("金融问答系统")

    tabs = st.tabs([
        "问答系统", "数据查询", "结果分析", 
        "初级题目", "中级题目", "高级题目"
    ])

    with tabs[0]: render_qa_tab()
    with tabs[1]: render_query_tab()
    with tabs[2]: render_analysis_tab()
    with tabs[3]: render_basic_tab()
    with tabs[4]: render_intermediate_tab()
    with tabs[5]: render_advanced_tab()

if __name__ == "__main__":
    main()