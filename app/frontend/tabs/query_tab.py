import streamlit as st
from utils.api_client import call_api

def render_query_tab():
    st.header("数据查询")
    st.write("在这里查询金融数据")

    # 添加查询参数
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("股票代码", key="query_symbol")
        start_date = st.date_input("开始日期", key="query_start_date")
    with col2:
        data_type = st.selectbox("数据类型", ["价格", "财务报表", "新闻"], key="query_data_type")
        end_date = st.date_input("结束日期", key="query_end_date")

    if st.button("查询", key="query_button"):
        if st.session_state.api_key:
            with st.spinner("查询中..."):
                try:
                    response = call_api(
                        "query",
                        {
                            "symbol": symbol,
                            "start_date": str(start_date),
                            "end_date": str(end_date),
                            "data_type": data_type
                        },
                        st.session_state.api_key
                    )
                    st.write(response["data"])
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("请先设置API Key") 