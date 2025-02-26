import streamlit as st
from modules.auth import logout
from modules.data_manager import (
    handle_file_upload, file_selector, add_to_conversation, 
    create_new_conversation, load_conversation
)
from modules.code_executor import execute_code
from modules.model_service import generate_analysis_code, generate_chat_response, get_dataframe_info
from modules.model_config import load_model_config
from modules.utils import get_user_id
from datetime import datetime
import pandas as pd
import os

# 显示对话历史
def display_conversation():
    # 创建聊天消息容器
    for message in st.session_state.conversation_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.chat_message("user").write(content)
        elif role == "assistant":
            with st.chat_message("assistant"):
                st.write(content)
                
                # 显示代码和执行结果
                # if "code" in message:
                #     with st.expander("查看代码"):
                #         st.code(message["code"], language="python")
                
                if "execution_result" in message:
                    result = message["execution_result"]
                    
                    if result["output"]:
                        with st.expander("查看输出"):
                            st.text(result["output"])
                    
                    if result["error"]:
                        st.error(f"错误: {result['error']}")
                    
                    if result["result"]:
                        if result["result"]["type"] == "figure":
                            st.image(result["result"]["path"])
                        elif result["result"]["type"] == "dataframe":
                            st.dataframe(result["result"]["data"])
        elif role == "system":
            st.chat_message("system", avatar="🔧").write(content)

# 用户输入处理
def handle_user_input():
    # 使用聊天输入替代文本框和提交按钮
    user_input = st.chat_input("请输入您的数据分析需求...")
    
    if user_input:
        # 添加用户消息到对话历史
        add_to_conversation("user", user_input)
        
        # 生成并执行代码
        if st.session_state.current_df is not None:
            # 创建占位符用于流式输出
            assistant_placeholder = st.chat_message("assistant")
            thinking_placeholder = assistant_placeholder.empty()
            thinking_placeholder.write("正在分析数据...")
            
            # 获取数据框信息
            df_info = get_dataframe_info(st.session_state.current_df)
            
            # 生成分析代码
            code = generate_analysis_code(user_input, df_info)
            
            # 执行代码
            execution_result = execute_code(code, get_user_id())
            
            # 生成助手回复
            assistant_response = generate_chat_response(
                st.session_state.conversation_history[-1:],  # 只传入最后一条用户消息
                df_info
            )
            
            # 使用占位符显示最终回复
            thinking_placeholder.empty()
            assistant_placeholder.write(assistant_response)
            
            # 显示执行结果
            if execution_result:
                if execution_result.get("error"):
                    assistant_placeholder.error(f"错误: {execution_result['error']}")
                if execution_result.get("result"):
                    result = execution_result["result"]
                    if result["type"] == "figure":
                        assistant_placeholder.image(result["path"])
                    elif result["type"] == "dataframe":
                        assistant_placeholder.dataframe(result["data"])
            
            # 添加助手消息到对话历史
            add_to_conversation("assistant", assistant_response, code, execution_result)
        else:
            # 创建占位符用于流式输出
            assistant_placeholder = st.chat_message("assistant")
            thinking_placeholder = assistant_placeholder.empty()
            thinking_placeholder.write("正在思考...")
            
            # 生成助手回复（无数据情况）
            assistant_response = generate_chat_response(
                st.session_state.conversation_history[-1:]  # 只传入最后一条用户消息
            )
            
            # 使用占位符显示最终回复
            thinking_placeholder.empty()
            assistant_placeholder.write(assistant_response)
            
            # 添加助手消息到对话历史
            add_to_conversation("assistant", assistant_response)
        
        # 刷新页面显示新消息
        st.rerun()

# 渲染主界面
def render_main_ui():
    # 设置侧边栏宽度和修复文件上传按钮样式
    st.markdown("""
    <style>
    .stFileUploader button {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 设置侧边栏内容
    with st.sidebar:
        # 用户信息和操作按钮
        st.markdown(f"用户: **{st.session_state.username}**")
        
        # 操作按钮区域
        col1, col2, col3 = st.columns(3)
        
        # 在每列中放置一个按钮
        if col1.button("退出登录"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        if col1.button("生成报告"):
            st.success("报告已生成!")
            st.rerun()
            
        if col2.button("新增对话"):
            create_new_conversation()
            st.rerun()

        if col2.button("保存对话"):
            st.success("对话已保存!")
            st.rerun()
            
        if col3.button("清空对话"):
            st.session_state.conversation_history = []
            from modules.data_manager import save_conversation_history
            save_conversation_history(get_user_id(), [])
            st.success("对话历史已清空!")
            st.rerun()

        if col3.button("保存笔记"):
            st.success("笔记已保存!")
            st.rerun()
        
        # 分隔线
        st.divider()
        
        # 文件上传和选择
        handle_file_upload()
        file_selector()
        
        # 确保模型配置已加载（但不在UI中显示）
        if 'model_config' not in st.session_state:
            st.session_state.model_config = load_model_config()
    
    # 主内容区域
    st.title("💬 智能数据分析系统")
    st.caption("🚀 基于大模型的智能数据分析系统")
    
    # 显示对话历史
    display_conversation()
    
    # 处理用户输入
    handle_user_input()