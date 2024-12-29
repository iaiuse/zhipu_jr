from utils.api_client import call_api
from typing import List, Dict
import json
from pathlib import Path
import streamlit as st

class QuestionService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.table_descriptions = self._load_table_metadata()
        
    def _load_table_metadata(self) -> dict:
        """加载表的元数据信息"""
        config_path = Path(__file__).parent.parent / "config" / "table_metadata.json"
        with open(config_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            return {
                table_name: f"{meta['chinese_name']}，{meta['description']}"
                for table_name, meta in metadata["tables"].items()
            }
        
    def analyze_tables(self, question: str) -> List[str]:
        """分析问题需要用到的表"""
        # 添加调试信息展示区
        debug_container = st.expander("Question Analysis Debug", expanded=False)
        
        prompt = self._generate_table_analysis_prompt(question)
        with debug_container:
            st.write(f"Generated prompt: {prompt}")
            
            params = {
                "prompt": prompt,
                "question": question
            }
            st.write(f"Calling API with params: {params}")
            
            response = call_api(
                "analyze_tables",
                params,
                self.api_key
            )
            st.write(f"API response: {response}")
            
            tables = response.get("tables", [])
            st.write(f"Extracted tables: {tables}")
        
        return tables
    
    def _generate_table_analysis_prompt(self, question: str) -> str:
        """生成用于分析表的prompt"""
        # 构建表描述文本
        table_descriptions = "\n".join([
            f"- {table}: {desc}"
            for table, desc in self.table_descriptions.items()
        ])
        
        return f"""作为一个金融数据分析助手，请帮我分析以下问题需要用到哪些数据表：

问题：{question}

可用的数据表及其描述：
{table_descriptions}

请分析这个问题需要查询哪些表，只返回表名列表，不需要其他解释。例如：
["constantdb.secumain", "astockmarketquotesdb.qt_dailyquote"]

注意：
1. 只返回必要的表
2. 如果需要关联查询，要返回所有相关的表
3. 如果问题信息不足，返回空列表 []
"""
    
    def get_fields(self, tables: List[str]) -> Dict:
        """获取表字段信息"""
        return call_api(
            "get_fields",
            {"tables": tables},
            self.api_key
        )
    
    def generate_sql(self, question: str, tables: List[str], fields: Dict) -> str:
        """生成SQL语句"""
        return call_api(
            "generate_sql",
            {
                "question": question,
                "tables": tables,
                "fields": fields
            },
            self.api_key
        )
    
    def execute_sql(self, sql: str) -> Dict:
        """执行SQL语句"""
        return call_api(
            "execute_sql",
            {"sql": sql},
            self.api_key
        ) 