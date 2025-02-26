import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
import os
import shutil
from modules.utils import (
    get_user_id, get_user_data_dir, get_user_conversation_file, 
    get_user_conversation_dir, generate_conversation_id, get_file_path
)

# 对话历史管理
def load_conversation_history(user_id):
    file_path = get_user_conversation_file(user_id)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_conversation_history(user_id, history):
    file_path = get_user_conversation_file(user_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# 列出用户的所有对话历史
def list_user_conversations(username):
    conv_dir = get_user_conversation_dir(username)
    if not os.path.exists(conv_dir):
        return []
    
    conversations = []
    for filename in os.listdir(conv_dir):
        if filename.endswith('.json'):
            conv_id = filename[:-5]  # 移除 .json 后缀
            file_path = os.path.join(conv_dir, filename)
            
            # 获取文件修改时间
            mod_time = os.path.getmtime(file_path)
            mod_time_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
            
            # 读取对话内容获取第一条消息作为标题
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    conv_data = json.load(f)
                    title = "空对话"
                    if conv_data and len(conv_data) > 0:
                        for msg in conv_data:
                            if msg["role"] == "user":
                                title = msg["content"][:30] + ("..." if len(msg["content"]) > 30 else "")
                                break
            except:
                title = "无法读取"
            
            # 从对话ID中提取日期
            date_part = ""
            if "_" in conv_id and len(conv_id.split("_")[0]) == 8:
                date_str = conv_id.split("_")[0]
                try:
                    date_obj = datetime.strptime(date_str, "%Y%m%d")
                    date_part = date_obj.strftime("%Y-%m-%d")
                except:
                    date_part = ""
            
            conversations.append({
                "id": conv_id,
                "title": title,
                "date": date_part,
                "modified": mod_time_str,
                "modified_timestamp": mod_time
            })
    
    # 按修改时间排序，最新的在前
    conversations.sort(key=lambda x: x["modified_timestamp"], reverse=True)
    return conversations

# 初始化会话状态
def init_session_state():
    if 'conversation_history' not in st.session_state:
        user_id = get_user_id()
        st.session_state.conversation_history = load_conversation_history(user_id)
    
    if 'data_files' not in st.session_state:
        st.session_state.data_files = {}
    
    if 'current_df' not in st.session_state:
        st.session_state.current_df = None
    
    if 'current_file_name' not in st.session_state:
        st.session_state.current_file_name = None

# 创建新对话
def create_new_conversation():
    st.session_state.user_id = generate_conversation_id()
    st.session_state.conversation_history = []
    save_conversation_history(st.session_state.user_id, [])
    # 清空当前数据文件
    st.session_state.data_files = {}
    st.session_state.current_df = None
    st.session_state.current_file_name = None
    return st.session_state.user_id

# 加载指定对话
def load_conversation(conv_id):
    st.session_state.user_id = conv_id
    st.session_state.conversation_history = load_conversation_history(conv_id)
    
    # 加载该对话关联的数据文件
    username = st.session_state.username
    data_dir = get_user_data_dir(username, conv_id)
    
    # 重置数据文件状态
    st.session_state.data_files = {}
    st.session_state.current_df = None
    st.session_state.current_file_name = None
    
    # 如果目录存在，加载文件列表
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            file_path = os.path.join(data_dir, filename)
            if os.path.isfile(file_path):
                st.session_state.data_files[filename] = file_path

# 对话管理
def add_to_conversation(role, content, code=None, execution_result=None):
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if code:
        message["code"] = code
    
    if execution_result:
        message["execution_result"] = execution_result
    
    st.session_state.conversation_history.append(message)
    save_conversation_history(get_user_id(), st.session_state.conversation_history)

# 文件上传和处理
def handle_file_upload():
    uploaded_file = st.file_uploader("上传数据文件", type=["csv", "xlsx", "xls"], help="支持csv、xlsx、xls格式，文件大小限制：200MB")

    if uploaded_file is not None:
        try:
            file_name = uploaded_file.name
            username = st.session_state.username
            conversation_id = get_user_id()
            
            # 使用新的文件路径结构
            file_path = get_file_path(username, conversation_id, file_name)
            
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 根据文件类型读取数据
            if file_name.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            
            # 更新会话状态
            st.session_state.data_files[file_name] = file_path
            st.session_state.current_df = df
            st.session_state.current_file_name = file_name
            
            # 添加到对话历史
            add_to_conversation("system", f"已上传文件: {file_name}")
            
        except Exception as e:
            st.error(f"文件处理错误: {str(e)}")

# 文件选择器
def file_selector():
    if st.session_state.data_files:
        # 使用更简洁的选择器
        options = list(st.session_state.data_files.keys())
        
        # 如果只有一个文件，直接显示
        if len(options) == 1:
            selected_file = options[0]
        else:
            # 否则显示下拉选择框
            selected_file = st.selectbox(
                "选择文件",
                options,
                index=options.index(st.session_state.current_file_name) if st.session_state.current_file_name in options else 0,
                label_visibility="collapsed"
            )
        
        if selected_file:
            file_path = st.session_state.data_files[selected_file]
            if selected_file.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif selected_file.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
                
            st.session_state.current_df = df
            st.session_state.current_file_name = selected_file
            
            # 显示数据预览
            st.dataframe(df)
            st.write(f"数据形状: {df.shape[0]} 行, {df.shape[1]} 列") 