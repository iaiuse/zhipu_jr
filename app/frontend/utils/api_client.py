import json
from typing import Dict, Any
from openai import OpenAI
import streamlit as st

def call_api(endpoint: str, params: Dict, api_key: str) -> Any:
    """统一的API调用入口"""
    # 添加调试信息展示区
    debug_container = st.expander("Debug Info", expanded=False)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key, base_url=st.session_state.base_url)
    model = st.session_state.model

    if endpoint == "analyze_tables":
        with debug_container:
            st.write(f"Analyzing tables with params: {params}")
            st.write(f"Using model: {model}")
            messages = [
                {"role": "system", "content": "你是一个金融数据分析助手，帮助分析SQL查询需要用到的表。"},
                {"role": "user", "content": params["prompt"]}
            ]
            st.write(f"Constructed messages: {messages}")
            
            st.write(f"Calling OpenAI API with model: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7
            )
            st.write(f"Got API response: {response}")
            
            try:
                content = response.choices[0].message.content
                st.write(f"Extracted content: {content}")
                tables = json.loads(content)
                st.write(f"Parsed tables: {tables}")
                return {"tables": tables}
            except Exception as e:
                st.write(f"Error parsing response: {str(e)}")
                raise Exception(f"解析API响应失败: {str(e)}")
            
    elif endpoint == "get_fields":
        # 调用后端API获取字段信息
        response = client.post(
            "fields",
            json=params
        )
        return response.json()
        
    elif endpoint == "generate_sql":
        messages = [
            {"role": "system", "content": "你是一个SQL专家，帮助生成准确的SQL查询语句。"},
            {"role": "user", "content": f"""
根据以下信息生成SQL查询语句:
问题: {params['question']}
可用的表: {params['tables']}
字段信息: {params['fields']}

只返回SQL语句，不需要其他解释。
            """}
        ]
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    elif endpoint == "execute_sql":
        # 调用后端API执行SQL
        response = client.post(
            "query",
            json=params
        )
        return response.json()
        
    else:
        raise Exception(f"未知的endpoint: {endpoint}")