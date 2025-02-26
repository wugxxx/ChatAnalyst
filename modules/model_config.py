import os
import streamlit as st
import json

# 默认模型配置
DEFAULT_CONFIG = {
    "provider": "openai",
    "base_url": "https://api.openai.com/v1",
    "api_key": "",
    "model_name": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 2000,
    "system_prompt": "你是一个专业的数据分析助手，擅长解读数据并生成Python代码进行数据分析。请根据用户的需求，生成相应的分析代码。"
}

# 配置文件路径
CONFIG_FILE = "config/model_config.json"

# 确保配置目录存在
def ensure_config_dir():
    os.makedirs("config", exist_ok=True)

# 加载模型配置
def load_model_config():
    ensure_config_dir()
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG
    else:
        # 如果配置文件不存在，创建默认配置
        save_model_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

# 保存模型配置
def save_model_config(config):
    ensure_config_dir()
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# 显示模型配置界面
def show_model_config():
    st.sidebar.subheader("模型配置")
    
    # 加载当前配置
    if 'model_config' not in st.session_state:
        st.session_state.model_config = load_model_config()
    
    config = st.session_state.model_config
    
    # 创建配置表单
    with st.sidebar.expander("模型设置", expanded=False):
        # 服务提供商选择
        provider = st.selectbox(
            "服务提供商",
            ["openai", "azure", "自定义"],
            index=["openai", "azure", "自定义"].index(config.get("provider", "openai"))
        )
        
        # 根据提供商显示不同的配置项
        if provider == "openai":
            base_url = st.text_input("API基础URL", value=config.get("base_url", "https://api.openai.com/v1"))
            api_key = st.text_input("API密钥", value=config.get("api_key", ""), type="password")
            model_name = st.selectbox(
                "模型名称", 
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                index=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"].index(config.get("model_name", "gpt-3.5-turbo"))
            )
        elif provider == "azure":
            base_url = st.text_input("Azure端点", value=config.get("base_url", ""))
            api_key = st.text_input("API密钥", value=config.get("api_key", ""), type="password")
            model_name = st.text_input("部署名称", value=config.get("model_name", ""))
        else:  # 自定义
            base_url = st.text_input("API基础URL", value=config.get("base_url", ""))
            api_key = st.text_input("API密钥", value=config.get("api_key", ""), type="password")
            model_name = st.text_input("模型名称", value=config.get("model_name", ""))
        
        # 通用配置项
        temperature = st.slider("温度", min_value=0.0, max_value=1.0, value=config.get("temperature", 0.7), step=0.1)
        max_tokens = st.number_input("最大生成长度", min_value=100, max_value=8000, value=config.get("max_tokens", 2000), step=100)
        system_prompt = st.text_area("系统提示词", value=config.get("system_prompt", DEFAULT_CONFIG["system_prompt"]), height=100)
        
        # 保存按钮
        if st.button("保存配置"):
            new_config = {
                "provider": provider,
                "base_url": base_url,
                "api_key": api_key,
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "system_prompt": system_prompt
            }
            
            # 更新会话状态和保存到文件
            st.session_state.model_config = new_config
            save_model_config(new_config)
            st.success("配置已保存!")
    
    return st.session_state.model_config 