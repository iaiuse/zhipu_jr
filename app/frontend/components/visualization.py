# app/frontend/components/visualization.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import pandas as pd

class DataVisualizer:
    @staticmethod
    def render_result(result: Dict[str, Any]):
        """根据结果类型渲染不同的可视化"""
        if result.get("type") == "basic":
            st.write(result["answer"])
            if "data" in result:
                st.dataframe(pd.DataFrame(result["data"]))
                
        elif result.get("type") == "statistical":
            DataVisualizer._render_statistical(result)
            
        elif result.get("type") == "complex":
            DataVisualizer._render_complex(result)
    
    @staticmethod
    def _render_statistical(result: Dict[str, Any]):
        """渲染统计类数据可视化"""
        st.write(result["answer"])
        
        if "data" in result:
            df = pd.DataFrame(result["data"])
            
            # 创建图表
            fig = go.Figure()
            
            # 根据数据类型添加不同的图表
            if "limit_up_count" in df.columns:
                # 柱状图
                fig.add_trace(go.Bar(
                    x=df['stock_names'].str.split(',').explode(),
                    y=df['limit_up_count'],
                    name="涨停次数"
                ))
                
            # 设置图表布局
            fig.update_layout(
                title="股票涨停统计",
                xaxis_title="股票名称",
                yaxis_title="次数",
                height=500
            )
            
            st.plotly_chart(fig)
            
            # 添加详细数据表格
            with st.expander("查看详细数据"):
                st.dataframe(df)

    @staticmethod
    def _render_complex(result: Dict[str, Any]):
        """渲染复杂分析的可视化"""
        st.write(result["answer"])
        
        if "data" in result and "analysis" in result:
            df = pd.DataFrame(result["data"])
            
            # 创建多个图表
            col1, col2 = st.columns(2)
            
            with col1:
                # 散点图展示公司分布
                fig_scatter = px.scatter(
                    df,
                    x="TotalAssets",
                    y="TotalLiability",
                    color="debt_ratio",
                    hover_data=["SecuAbbr"],
                    title="资产负债分布"
                )
                st.plotly_chart(fig_scatter)
                
            with col2:
                # 箱形图展示行业分布
                fig_box = go.Figure()
                fig_box.add_trace(go.Box(
                    y=df["debt_ratio"],
                    name="资产负债率分布"
                ))
                fig_box.update_layout(title="行业资产负债率分布")
                st.plotly_chart(fig_box)
            
            # 添加汇总统计
            cols = st.columns(3)
            with cols[0]:
                st.metric("平均资产负债率", 
                         f"{result['analysis']['avg_debt_ratio']:.2%}")
            with cols[1]:
                st.metric("最高资产负债率",
                         f"{result['analysis']['max_debt_ratio']:.2%}")
            with cols[2]:
                st.metric("最低资产负债率",
                         f"{result['analysis']['min_debt_ratio']:.2%}")
            
            # 添加详细数据表格
            with st.expander("查看详细数据"):
                st.dataframe(df)