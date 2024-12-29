import streamlit as st
from utils.api_client import call_api

def render_intermediate_tab():
    st.header("中级题目")
    st.write("这里是进阶的金融分析题目")
    
    if st.button("生成中级题目"):
        if st.session_state.api_key:
            with st.spinner("生成题目中..."):
                try:
                    question = call_api(
                        "generate_question",
                        {"level": "intermediate"},
                        st.session_state.api_key
                    )
                    st.write("问题：", question["question"])
                    with st.expander("查看答案"):
                        st.write(question["answer"])
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("请先设置API Key") 