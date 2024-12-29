import streamlit as st
from utils.api_client import call_api

def render_advanced_tab():
    st.header("高级题目")
    st.write("这里是复杂的金融策略题目")
    
    if st.button("生成高级题目"):
        if st.session_state.api_key:
            with st.spinner("生成题目中..."):
                try:
                    question = call_api(
                        "generate_question",
                        {"level": "advanced"},
                        st.session_state.api_key
                    )
                    st.write("问题：", question["question"])
                    with st.expander("查看答案"):
                        st.write(question["answer"])
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("请先设置API Key") 