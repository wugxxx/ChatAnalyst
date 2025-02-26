import openai
import json
import streamlit as st
from modules.model_config import load_model_config

# 初始化模型客户端
def get_model_client():
    # 获取模型配置
    config = st.session_state.get('model_config', load_model_config())
    
    # 检查API密钥是否存在
    if not config.get("api_key"):
        return None, "请先在模型配置中设置API密钥"
    
    try:
        # 创建OpenAI客户端
        client = openai.OpenAI(
            base_url=config.get("base_url"),
            api_key=config.get("api_key")
        )
        return client, None
    except Exception as e:
        return None, f"初始化模型客户端失败: {str(e)}"

# 生成分析代码
def generate_analysis_code(user_input, dataframe_info):
    # 获取模型客户端
    client, error = get_model_client()
    if error:
        return f"# 错误: {error}\nprint('无法连接到模型服务')"
    
    # 获取模型配置
    config = st.session_state.get('model_config', load_model_config())
    
    try:
        # 准备消息
        messages = [
            {"role": "system", "content": config.get("system_prompt")},
            {"role": "user", "content": f"""
我需要对以下数据进行分析:

数据信息:
{dataframe_info}

用户需求:
{user_input}

请生成Python代码来完成这个分析任务。代码应该使用pandas、numpy、matplotlib和seaborn库。
代码中应该使用变量名'df'来引用数据框。
只返回Python代码，不要有其他解释。
"""}
        ]
        
        # 调用模型API
        response = client.chat.completions.create(
            model=config.get("model_name"),
            messages=messages,
            temperature=config.get("temperature"),
            max_tokens=config.get("max_tokens")
        )
        
        # 提取代码
        code = response.choices[0].message.content.strip()
        
        # 如果代码被包裹在```python和```之间，提取出来
        if code.startswith("```python"):
            code = code.split("```python")[1]
        if code.startswith("```"):
            code = code.split("```")[1]
        if code.endswith("```"):
            code = code.split("```")[0]
            
        return code.strip()
        
    except Exception as e:
        return f"# 错误: {str(e)}\nprint('模型调用失败')"

# 生成对话回复
def generate_chat_response(conversation_history, dataframe_info=None):
    # 获取模型客户端
    client, error = get_model_client()
    if error:
        return f"错误: {error}。请检查模型配置。"
    
    # 获取模型配置
    config = st.session_state.get('model_config', load_model_config())
    
    try:
        # 准备消息
        messages = [{"role": "system", "content": config.get("system_prompt")}]
        
        # 如果有数据框信息，添加到系统消息
        if dataframe_info:
            messages[0]["content"] += f"\n\n当前数据信息:\n{dataframe_info}"
        
        # 添加对话历史
        for msg in conversation_history:
            if msg["role"] in ["user", "assistant", "system"]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # 调用模型API
        response = client.chat.completions.create(
            model=config.get("model_name"),
            messages=messages,
            temperature=config.get("temperature"),
            max_tokens=config.get("max_tokens")
        )
        
        # 返回回复内容
        return response.choices[0].message.content
        
    except Exception as e:
        return f"错误: {str(e)}。请检查网络连接或API密钥是否正确。"

# 获取数据框信息
def get_dataframe_info(df):
    if df is None:
        return "未加载数据"
    
    # 基本信息
    info = f"数据形状: {df.shape[0]} 行, {df.shape[1]} 列\n"
    
    # 列名和数据类型
    info += "列信息:\n"
    for col in df.columns:
        dtype = df[col].dtype
        info += f"- {col} ({dtype})\n"
    
    # 数值列的基本统计
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        info += "\n数值列统计:\n"
        stats = df[numeric_cols].describe().T
        for col in stats.index:
            info += f"- {col}: 均值={stats.loc[col, 'mean']:.2f}, 最小值={stats.loc[col, 'min']:.2f}, 最大值={stats.loc[col, 'max']:.2f}\n"
    
    # 缺失值信息
    missing = df.isnull().sum()
    if missing.sum() > 0:
        info += "\n缺失值信息:\n"
        for col in missing[missing > 0].index:
            info += f"- {col}: {missing[col]} 个缺失值 ({missing[col]/len(df)*100:.1f}%)\n"
    
    return info 