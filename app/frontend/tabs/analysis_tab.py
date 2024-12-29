import streamlit as st
from utils.api_client import call_api

def render_analysis_tab():
    st.header("结果分析")
    st.write("分析金融数据并生成报告")

    # 分析选项
    analysis_type = st.selectbox(
        "选择分析类型",
        ["技术分析", "基本面分析", "情绪分析", "风险评估"]
    )

    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("股票代码")
    with col2:
        period = st.selectbox("分析周期", ["1周", "1月", "3月", "6月", "1年"])

    if st.button("开始分析"):
        if st.session_state.api_key:
            with st.spinner("分析中..."):
                try:
                    response = call_api(
                        "analyze",
                        {
                            "symbol": symbol,
                            "analysis_type": analysis_type,
                            "period": period
                        },
                        st.session_state.api_key
                    )
                    
                    # 显示分析结果
                    st.subheader("分析结果")
                    st.write(response["summary"])
                    
                    # 显示图表（如果有）
                    if "charts" in response:
                        st.plotly_chart(response["charts"])
                        
                    # 显示建议
                    with st.expander("投资建议"):
                        st.write(response["recommendations"])
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("请先设置API Key") 