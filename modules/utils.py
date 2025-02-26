import os
import uuid
import json
import time
from datetime import datetime
import io
from contextlib import redirect_stdout
import streamlit as st

# 创建必要的目录结构
def create_directories():
    os.makedirs("data", exist_ok=True)
    os.makedirs("conversations", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    os.makedirs("users", exist_ok=True)

# 生成带日期的对话ID
def generate_conversation_id():
    """生成带日期标识的对话ID"""
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_str = str(uuid.uuid4())[:8]
    return f"{date_str}_{random_str}"

# 用户管理
def get_user_id():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = generate_conversation_id()
    return st.session_state.user_id

def get_user_data_dir(username, conversation_id=None):
    """获取用户数据目录，可选指定对话ID"""
    if conversation_id:
        # 按用户名和对话ID组织
        user_dir = f"data/{username}/{conversation_id}"
    else:
        # 仅按用户名组织
        user_dir = f"data/{username}"
    
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def get_user_conversation_dir(username):
    """获取用户对话历史目录"""
    user_conv_dir = f"conversations/{username}"
    os.makedirs(user_conv_dir, exist_ok=True)
    return user_conv_dir

def get_user_conversation_file(user_id):
    """获取用户对话历史文件路径"""
    if 'username' in st.session_state:
        username = st.session_state.username
        user_conv_dir = get_user_conversation_dir(username)
        return f"{user_conv_dir}/{user_id}.json"
    else:
        # 未登录用户或临时会话使用旧路径
        return f"conversations/{user_id}.json"

def get_file_path(username, conversation_id, filename):
    """获取文件存储路径"""
    user_data_dir = get_user_data_dir(username, conversation_id)
    return f"{user_data_dir}/{filename}" 