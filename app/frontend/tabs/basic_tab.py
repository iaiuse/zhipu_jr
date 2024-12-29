import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from datetime import datetime
import json
from services.question_service import QuestionService

def create_question_tree(questions):
    # 直接使用tid作为组ID，team作为问题列表
    groups = {}
    for group in questions:
        groups[group["tid"]] = group["team"]
    return groups

def execute_question(question: str, api_key: str) -> dict:
    """执行单个问题的处理流程"""
    service = QuestionService(api_key)
    result = {
        "status": "processing",
        "steps": [],
        "error": None,
        "answer": None
    }
    
    try:
        # 步骤1：分析所需表
        step1 = {
            "name": "分析所需表",
            "status": "processing",
            "start_time": datetime.now().strftime("%H:%M:%S")
        }
        tables = service.analyze_tables(question)
        step1["status"] = "completed"
        step1["result"] = tables
        result["steps"].append(step1)

        # 步骤2：获取字段信息
        step2 = {
            "name": "获取字段信息",
            "status": "processing",
            "start_time": datetime.now().strftime("%H:%M:%S")
        }
        fields = service.get_fields(tables)
        step2["status"] = "completed"
        step2["result"] = fields
        result["steps"].append(step2)

        # 步骤3：生成SQL
        step3 = {
            "name": "生成SQL",
            "status": "processing",
            "start_time": datetime.now().strftime("%H:%M:%S")
        }
        sql = service.generate_sql(question, tables, fields)
        step3["status"] = "completed"
        step3["result"] = sql
        result["steps"].append(step3)

        # 步骤4：执行SQL
        step4 = {
            "name": "执行SQL",
            "status": "processing",
            "start_time": datetime.now().strftime("%H:%M:%S")
        }
        answer = service.execute_sql(sql)
        step4["status"] = "completed"
        step4["result"] = answer
        result["steps"].append(step4)

        result["status"] = "completed"
        result["answer"] = answer

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        
    return result

def render_basic_tab():
    st.header("初级题目")
    
    if "execution_state" not in st.session_state:
        st.session_state.execution_state = {
            "is_running": False,
            "current_group": "",
            "current_question": "",
            "progress": 0,
            "results": None,
            "execution_log": []
        }
    
    # 添加文件上传功能
    uploaded_file = st.file_uploader("上传题目JSON文件", type=['json'])
    
    # 控制按钮行
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("开始执行", disabled=st.session_state.execution_state["is_running"]):
            st.session_state.execution_state["is_running"] = True
            st.session_state.execution_state["execution_log"] = []  # 清空执行日志
    with col2:
        if st.button("暂停执行", disabled=not st.session_state.execution_state["is_running"]):
            st.session_state.execution_state["is_running"] = False
    with col3:
        test_button_disabled = st.session_state.execution_state["is_running"] or uploaded_file is None
        if st.button("测试(仅第一题)", disabled=test_button_disabled):
            if uploaded_file is not None:
                questions = json.loads(uploaded_file.read())
                st.session_state.execution_state["results"] = questions
                # 只处理第一个组的第一个问题
                first_group = questions[0]
                first_question = first_group["team"][0]
                
                st.session_state.execution_state["current_group"] = first_group["tid"]
                st.session_state.execution_state["current_question"] = first_question["question"]
                
                # 执行问题处理流程
                result = execute_question(first_question["question"], st.session_state.api_key)
                
                # 更新问题状态和答案
                first_question["status"] = result["status"]
                if result["status"] == "completed":
                    first_question["answer"] = result["answer"]
                else:
                    first_question["answer"] = f"执行错误: {result['error']}"
                
                # 记录执行日志
                log_entry = {
                    "group": first_group["tid"],
                    "question": first_question["question"],
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "steps": result["steps"],
                    "status": result["status"]
                }
                st.session_state.execution_state["execution_log"].append(log_entry)
                st.session_state.execution_state["progress"] = 1
                # progress_bar.progress(1)
                # status_text.write("测试执行完成!")
    with col4:
        if st.session_state.execution_state["results"] is not None:
            result_json = json.dumps(st.session_state.execution_state["results"], 
                                   ensure_ascii=False, 
                                   indent=2)
            st.download_button(
                label="下载结果",
                data=result_json,
                file_name="results.json",
                mime="application/json"
            )
    
    # 进度显示
    progress_bar = st.progress(st.session_state.execution_state["progress"])
    status_text = st.empty()
    
    # 分成左右两列
    left_col, right_col = st.columns([1, 1])
    
    if uploaded_file is not None:
        try:
            questions = json.loads(uploaded_file.read())
            question_groups = create_question_tree(questions)
            
            # 如果正在执行
            if st.session_state.execution_state["is_running"]:
                st.session_state.execution_state["results"] = questions
                
                total_questions = sum(len(group["team"]) for group in questions)
                completed_questions = 0
                
                for group in questions:
                    if not st.session_state.execution_state["is_running"]:
                        break
                        
                    st.session_state.execution_state["current_group"] = group["tid"]
                    
                    for q in group["team"]:
                        if not st.session_state.execution_state["is_running"]:
                            break
                            
                        st.session_state.execution_state["current_question"] = q["question"]
                        current_status = f"正在处理: 组 {group['tid']} - {q['question'][:30]}..."
                        status_text.write(current_status)
                        
                        # 执行问题处理流程
                        result = execute_question(q["question"], st.session_state.api_key)
                        
                        # 更新问题状态和答案
                        q["status"] = result["status"]
                        if result["status"] == "completed":
                            q["answer"] = result["answer"]
                        else:
                            q["answer"] = f"执行错误: {result['error']}"
                        
                        # 记录执行日志
                        log_entry = {
                            "group": group["tid"],
                            "question": q["question"],
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "steps": result["steps"],
                            "status": result["status"]
                        }
                        st.session_state.execution_state["execution_log"].append(log_entry)
                        
                        completed_questions += 1
                        progress = completed_questions / total_questions
                        progress_bar.progress(progress)
                        st.session_state.execution_state["progress"] = progress
                
                st.session_state.execution_state["is_running"] = False
                status_text.write("执行完成!")
            
            # 显示问题和结果
            with left_col:
                for group_id, group_questions in question_groups.items():
                    with st.expander(f"问题组 {group_id}", expanded=True):
                        for q in group_questions:
                            st.write(f"问题：{q['question']}")
                            if 'answer' in q and q['answer']:
                                with st.expander("查看答案"):
                                    st.write(q['answer'])
            
            # 显示执行过程
            with right_col:
                st.subheader("执行过程")
                st.write(f"当前状态: {'执行中' if st.session_state.execution_state['is_running'] else '已暂停'}")
                st.write(f"当前组: {st.session_state.execution_state['current_group']}")
                st.write(f"当前问题: {st.session_state.execution_state['current_question']}")
                
                # 显示执行日志
                for log in st.session_state.execution_state["execution_log"]:
                    with st.expander(f"[{log['timestamp']}] 组 {log['group']} - {log['question'][:30]}...", expanded=True):
                        if "error" in log:
                            st.error(log["error"])
                        else:
                            st.write("使用的表：", log["tables"])
                            st.write("相关字段：", log["fields"])
                            st.write("执行结果：", log["result"])
                
        except Exception as e:
            st.error(f"Error: {str(e)}") 