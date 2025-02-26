import streamlit as st
import hashlib
import json
import os
from datetime import datetime

# 用户数据文件
USER_DB_FILE = "users/users.json"

# 确保用户数据文件存在
def ensure_user_db():
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'w') as f:
            json.dump({}, f)

# 获取所有用户
def get_users():
    ensure_user_db()
    with open(USER_DB_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# 保存用户数据
def save_users(users):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# 密码哈希
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 注册新用户
def register_user(username, password):
    users = get_users()
    
    if username in users:
        return False, "用户名已存在"
    
    users[username] = {
        "password_hash": hash_password(password),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": None
    }
    
    save_users(users)
    return True, "注册成功"

# 验证用户登录
def authenticate_user(username, password):
    users = get_users()
    
    if username not in users:
        return False, "用户名不存在"
    
    if users[username]["password_hash"] != hash_password(password):
        return False, "密码错误"
    
    # 更新最后登录时间
    users[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_users(users)
    
    return True, "登录成功"

# 检查用户是否已登录
def check_authentication():
    return 'authenticated' in st.session_state and st.session_state.authenticated

# 登录页面
def login_page():
    st.title("多租户数据分析系统 - 用户登录")
    
    # 使用会话状态来控制当前显示的标签页
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "登录"
    
    # 创建标签页
    tab1, tab2 = st.tabs(["登录", "注册"])
    
    # 登录标签页
    with tab1:
        if st.session_state.active_tab == "登录":
            st.subheader("用户登录")
            username = st.text_input("用户名", key="login_username")
            password = st.text_input("密码", type="password", key="login_password")
            
            if st.button("登录", key="login_button"):
                success, message = authenticate_user(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error(message)
    
    # 注册标签页
    with tab2:
        if st.session_state.active_tab == "注册":
            st.subheader("新用户注册")
            new_username = st.text_input("用户名", key="register_username")
            new_password = st.text_input("密码", type="password", key="register_password")
            confirm_password = st.text_input("确认密码", type="password", key="confirm_password")
            
            if st.button("注册", key="register_button"):
                if new_password != confirm_password:
                    st.error("两次输入的密码不一致")
                else:
                    success, message = register_user(new_username, new_password)
                    if success:
                        st.success(message)
                        # 设置会话状态以切换到登录标签页
                        st.session_state.active_tab = "登录"
                        # 预填充登录表单
                        st.session_state.login_username = new_username
                        st.session_state.login_password = ""
                        st.rerun()
                    else:
                        st.error(message)

# 登出功能
def logout():
    if st.sidebar.button("退出登录"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun() 