import streamlit as st
from utils.api_client import call_api

def render_qa_tab():
    # 显示历史消息
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # 输入框
    if prompt := st.chat_input("输入你的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        if st.session_state.api_key:
            with st.spinner("思考中..."):
                try:
                    response = call_api(
                        "qa",
                        {"question": prompt},
                        st.session_state.api_key
                    )
                    answer = response["answer"]
                    
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    with st.chat_message("assistant"):
                        st.write(answer)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("请先设置API Key") 