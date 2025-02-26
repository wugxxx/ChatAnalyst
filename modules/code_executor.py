import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import time
from contextlib import redirect_stdout
from modules.utils import get_user_id

# 执行代码并捕获输出
def execute_code(code, user_id):
    # 创建一个临时的输出缓冲区
    output_buffer = io.StringIO()
    result = None
    error = None
    
    # 准备执行环境
    local_vars = {
        'pd': pd,
        'np': np,
        'plt': plt,
        'sns': sns,
        'st': st,
        'df': st.session_state.current_df
    }
    
    # 重定向标准输出
    with redirect_stdout(output_buffer):
        try:
            # 执行代码
            exec(code, local_vars)
            # 检查是否有图表生成
            if 'plt' in local_vars and plt.get_fignums():
                fig_path = f"temp/{user_id}_{time.time()}.png"
                plt.savefig(fig_path)
                plt.close()
                result = {"type": "figure", "path": fig_path}
            # 检查是否有返回的DataFrame
            elif 'result_df' in local_vars and isinstance(local_vars['result_df'], pd.DataFrame):
                result = {"type": "dataframe", "data": local_vars['result_df']}
        except Exception as e:
            error = str(e)
    
    # 获取输出
    output = output_buffer.getvalue()
    
    return {
        "output": output,
        "result": result,
        "error": error
    }

# 根据用户输入生成分析代码
def generate_analysis_code(user_input):
    if "描述" in user_input or "统计" in user_input:
        code = """
# 生成数据描述统计
result_df = df.describe()
print("数据描述统计:")
print(result_df)
"""
    elif "相关" in user_input:
        code = """
# 计算相关性矩阵
result_df = df.corr()
print("相关性矩阵:")
print(result_df)

# 绘制热力图
plt.figure(figsize=(10, 8))
sns.heatmap(result_df, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('特征相关性热力图')
plt.tight_layout()
"""
    elif "直方图" in user_input or "分布" in user_input:
        code = """
# 选择数值列
numeric_cols = df.select_dtypes(include=['number']).columns[:4]  # 限制为前4列以避免图表过多

# 绘制直方图
plt.figure(figsize=(12, 10))
for i, col in enumerate(numeric_cols, 1):
    plt.subplot(2, 2, i)
    sns.histplot(df[col], kde=True)
    plt.title(f'{col} 分布')
plt.tight_layout()
"""
    else:
        code = """
# 基本数据信息
print("数据基本信息:")
print(f"行数: {df.shape[0]}, 列数: {df.shape[1]}")
print("\\n列名:", df.columns.tolist())
print("\\n数据类型:")
print(df.dtypes)
print("\\n缺失值统计:")
print(df.isnull().sum())

# 生成简单的数据摘要
result_df = df.describe().T
"""
    return code 