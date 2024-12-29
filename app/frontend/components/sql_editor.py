# app/frontend/components/sql_editor.py
import streamlit as st
from streamlit_ace import st_ace
import pandas as pd
import plotly.express as px
from typing import Dict, Any

class SQLEditor:
    def __init__(self):
        self.table_schema = self._load_table_schema()
        
    def _load_table_schema(self) -> Dict[str, Any]:
        """加载表结构信息"""
        # 这里应该从配置或API加载实际的表结构
        return {
            "tables": {
                "constantdb.secumain": {
                    "columns": ["InnerCode", "CompanyCode", "SecuCode", "ChiName", "SecuAbbr"]
                },
                "astockmarketquotesdb.qt_dailyquote": {
                    "columns": ["InnerCode", "TradingDay", "OpenPrice", "ClosePrice", "HighPrice", "LowPrice"]
                }
                # 添加更多表结构
            }
        }
    
    def render(self):
        """渲染SQL编辑器界面"""
        st.subheader("SQL查询")
        
        # 添加常用查询模板
        with st.expander("常用查询模板"):
            if st.button("查询股票基本信息"):
                self._insert_template("stock_basic")
            if st.button("查询日行情数据"):
                self._insert_template("daily_quote")
        
        # SQL编辑器
        query = st_ace(
            value=st.session_state.get("sql_query", ""),
            language="sql",
            theme="monokai",
            auto_update=True,
            key="sql_editor"
        )
        
        # 保存当前查询
        if query:
            st.session_state.sql_query = query
        
        # 执行按钮
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("执行查询", key="execute_sql"):
                self._execute_query(query)
        with col2:
            st.download_button(
                "下载结果",
                data=self._get_download_data(),
                file_name="query_result.csv",
                mime="text/csv",
                disabled=not st.session_state.get("query_result")
            )
    
    def _insert_template(self, template_name: str):
        """插入SQL模板"""
        templates = {
            "stock_basic": """
                SELECT SecuCode, ChiName, SecuAbbr
                FROM constantdb.secumain
                WHERE SecuMarket = 90
                LIMIT 10
            """,
            "daily_quote": """
                SELECT sm.SecuAbbr, qt.TradingDay, qt.OpenPrice, qt.ClosePrice
                FROM astockmarketquotesdb.qt_dailyquote qt
                JOIN constantdb.secumain sm ON qt.InnerCode = sm.InnerCode
                WHERE qt.TradingDay >= '2021-01-01'
                LIMIT 10
            """
        }
        st.session_state.sql_query = templates.get(template_name, "")
    
    def _execute_query(self, query: str):
        """执行SQL查询"""
        try:
            with st.spinner("执行查询中..."):
                # 这里应该调用实际的API
                # result = api.execute_query(query)
                # 示例数据
                result = pd.DataFrame({
                    "SecuCode": ["000001", "000002"],
                    "ChiName": ["平安银行", "万科A"],
                    "ClosePrice": [10.5, 15.2]
                })
                
                st.session_state.query_result = result
                
                # 显示结果
                self._display_result(result)
        except Exception as e:
            st.error(f"查询错误: {str(e)}")
    
    def _display_result(self, df: pd.DataFrame):
        """显示查询结果"""
        # 显示数据表格
        st.dataframe(df)
        
        # 如果有数值列，显示可视化选项
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            with st.expander("数据可视化"):
                # 选择图表类型
                chart_type = st.selectbox(
                    "选择图表类型",
                    ["折线图", "柱状图", "散点图"]
                )
                
                # 选择数据列
                x_col = st.selectbox("选择X轴", df.columns)
                y_col = st.selectbox("选择Y轴", numeric_cols)