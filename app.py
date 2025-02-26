import streamlit as st
from modules.auth import login_page, check_authentication
from modules.data_manager import init_session_state
from modules.ui import render_main_ui

# 设置页面配置
st.set_page_config(
    page_title="智能数据分析系统",
    page_icon="📊",
    layout="wide"
)

def main():
    # 创建必要的目录结构
    from modules.utils import create_directories
    create_directories()
    
    # 检查用户是否已登录
    if not check_authentication():
        login_page()
    else:
        # 初始化会话状态
        init_session_state()
        
        # 渲染主界面
        render_main_ui()

if __name__ == "__main__":
    main()
