"""
银行智能体 Streamlit 前端
"""
import streamlit as st
import os
import sys
import json

# 延迟导入，避免在没有 API Key 时出错
try:
    from bank_agent import create_bank_agent
    from bank_data import bank_db
except Exception as e:
    st.error(f"导入模块时出错: {str(e)}")
    st.stop()

# 页面配置
st.set_page_config(
    page_title="银行智能助手",
    page_icon="🏦",
    layout="wide"
)

# 初始化 session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "api_key_set" not in st.session_state:
    st.session_state.api_key_set = False
if "api_provider" not in st.session_state:
    # 从环境变量读取 API 提供商，默认为 deepseek
    st.session_state.api_provider = os.getenv("API_PROVIDER", "deepseek").lower()
if "model_name" not in st.session_state:
    # 从环境变量读取模型名称，默认为 deepseek-chat
    st.session_state.model_name = os.getenv("MODEL_NAME", "deepseek-chat")

def extract_agent_response(response):
    """
    从 AgentExecutor 响应中提取最终答案
    优先从工具执行结果中提取，如果不存在则从 output 中提取
    """
    # 优先从中间步骤中提取工具执行结果
    if "intermediate_steps" in response:
        intermediate_steps = response.get("intermediate_steps", [])
        if intermediate_steps:
            # 获取最后一个工具的执行结果
            last_step = intermediate_steps[-1]
            if len(last_step) >= 2:
                tool_result = last_step[1]
                if isinstance(tool_result, str) and tool_result.strip():
                    return tool_result
                elif tool_result:
                    return str(tool_result)
    
    # 如果没有从中间步骤获取到，尝试从 output 获取
    answer = response.get("output", "")
    
    # 检查是否是 JSON 格式的工具调用
    if answer and answer.strip().startswith("{"):
        try:
            parsed = json.loads(answer)
            # 如果是工具调用的 JSON，尝试从中间步骤获取结果
            if "action" in parsed or "action_input" in parsed:
                if "intermediate_steps" in response:
                    intermediate_steps = response.get("intermediate_steps", [])
                    if intermediate_steps:
                        last_step = intermediate_steps[-1]
                        if len(last_step) >= 2:
                            tool_result = last_step[1]
                            if isinstance(tool_result, str) and tool_result.strip():
                                return tool_result
                            elif tool_result:
                                return str(tool_result)
                # 如果仍然没有结果，返回 None 让调用者处理
                return None
        except:
            pass
    
    return answer if answer else None

def initialize_agent(api_key: str, api_provider: str, model_name: str):
    """初始化智能体"""
    if not api_key or not api_key.strip():
        return False
    
    try:
        st.session_state.agent = create_bank_agent(
            api_key.strip(), 
            model_name=model_name,
            api_provider=api_provider
        )
        st.session_state.api_key_set = True
        st.session_state.api_provider = api_provider
        st.session_state.model_name = model_name
        return True
    except Exception as e:
        error_msg = str(e)
        if "api" in error_msg.lower() or "key" in error_msg.lower():
            st.error(f"API Key 无效或格式错误: {error_msg}")
        else:
            st.error(f"初始化智能体失败: {error_msg}")
        return False

# 从环境变量读取 API Key
def get_api_key_from_env():
    """从环境变量读取 API Key"""
    api_provider = st.session_state.api_provider
    
    if api_provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
    else:
        api_key = os.getenv("OPENAI_API_KEY", "")
    
    return api_key

# 自动初始化智能体（如果环境变量已设置）
if not st.session_state.api_key_set:
    api_key = get_api_key_from_env()
    if api_key:
        with st.spinner("正在初始化智能体..."):
            if initialize_agent(api_key, st.session_state.api_provider, st.session_state.model_name):
                st.session_state.api_key_set = True

# 侧边栏 - API 配置和账户信息
with st.sidebar:
    st.title("🏦 银行智能助手")
    st.divider()
    
    # API 配置信息显示
    st.subheader("API 配置")
    
    # 显示当前配置状态
    if st.session_state.api_key_set:
        provider_name = "DeepSeek" if st.session_state.api_provider == "deepseek" else "OpenAI"
        st.success(f"✅ {provider_name} API Key 已配置")
        st.info(f"当前模型: {st.session_state.model_name}")
        st.info(f"API 提供商: {provider_name}")
    else:
        st.error("⚠️ API Key 未配置")
        st.markdown("""
        **请在环境变量中设置 API Key：**
        
        - DeepSeek: `DEEPSEEK_API_KEY`
        - OpenAI: `OPENAI_API_KEY`
        
        在 Zeabur 部署时，请在项目设置中添加相应的环境变量。
        """)
    
    st.divider()
    
    # 账户信息
    st.subheader("账户信息")
    accounts = bank_db.list_accounts()
    for acc in accounts:
        st.info(f"**{acc['name']}** ({acc['account_id']})\n余额: ¥{acc['balance']:,.2f}")
    
    st.divider()
    
    # 快速操作示例
    st.subheader("💡 使用示例")
    st.markdown("""
    你可以尝试以下操作：
    
    - 查询余额：查询账户1001的余额
    - 转账：从账户1001向账户1002转账500元
    - 列出账户：显示所有账户
    """)

# 主界面
st.title("🏦 银行智能助手")
st.markdown("---")

# 显示聊天历史
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("请输入您的问题..."):
    # 检查 API Key 是否已设置
    if not st.session_state.api_key_set:
        st.error("API Key 未配置。请在环境变量中设置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY")
        st.stop()
    
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 获取智能体响应
    with st.chat_message("assistant"):
        with st.spinner("正在思考..."):
            try:
                response = st.session_state.agent.invoke({"input": prompt})
                
                # 使用辅助函数提取答案
                answer = extract_agent_response(response)
                
                # 如果返回 None 或仍然是 JSON，说明是工具调用的中间状态
                if answer is None:
                    output = response.get("output", "")
                    if output and output.strip().startswith("{"):
                        try:
                            parsed = json.loads(output)
                            action = parsed.get("action", "")
                            action_input = parsed.get("action_input", {})
                            if action == "check_balance":
                                account_id = action_input.get("account_id", "")
                                answer = f"正在查询账户 {account_id} 的余额，请稍候..."
                            elif action == "transfer_money":
                                from_acc = action_input.get("from_account_id", "")
                                to_acc = action_input.get("to_account_id", "")
                                amount = action_input.get("amount", 0)
                                answer = f"正在处理从账户 {from_acc} 向账户 {to_acc} 转账 {amount} 元的请求..."
                            elif action == "list_accounts":
                                answer = "正在获取账户列表，请稍候..."
                            else:
                                answer = "正在处理您的请求，请稍候..."
                        except:
                            answer = "正在处理您的请求，请稍候..."
                    else:
                        answer = output if output else "正在处理您的请求，请稍候..."
                
                # 如果答案仍然是 JSON 格式，提供错误提示
                if answer and answer.strip().startswith("{") and ("action" in answer or "tool" in answer.lower()):
                    answer = "抱歉，系统返回了格式错误。请尝试重新提问，或检查 API 配置。"
                
                # 如果答案为空，使用默认消息
                if not answer or not answer.strip():
                    answer = "抱歉，我无法处理您的请求。请检查您的输入是否正确。"
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                error_str = str(e)
                error_msg = ""
                
                # 处理不同类型的错误
                if "402" in error_str or "Insufficient Balance" in error_str or "余额不足" in error_str:
                    error_msg = """**API 账户余额不足**

您的 API 账户余额不足，无法继续使用服务。

**解决方案：**
1. **DeepSeek 用户**：请访问 https://platform.deepseek.com 充值账户
2. **OpenAI 用户**：请访问 https://platform.openai.com 充值账户
3. 检查您的 API Key 是否正确
4. 确认账户是否有足够的余额

如果问题持续存在，请联系相应的 API 服务提供商。"""
                elif "401" in error_str or "Unauthorized" in error_str or "Invalid API Key" in error_str:
                    error_msg = """**API Key 无效或未授权**

您的 API Key 可能无效或已过期。

**解决方案：**
1. 检查环境变量中的 API Key 是否正确设置
2. 确认 API Key 是否已过期
3. 在 Zeabur 项目设置中更新环境变量
4. 如果使用 DeepSeek，请确认 API Key 格式正确
5. 重启应用以使环境变量生效"""
                elif "429" in error_str or "Rate limit" in error_str or "请求频率" in error_str:
                    error_msg = """**请求频率过高**

您已达到 API 的请求频率限制。

**解决方案：**
1. 请稍等片刻后重试
2. 如果是免费账户，可能需要升级到付费计划
3. 检查您的 API 使用配额"""
                elif "404" in error_str or "Model not found" in error_str:
                    error_msg = """**模型不存在**

您选择的模型可能不存在或不可用。

**解决方案：**
1. 检查模型名称是否正确
2. 确认您的 API 账户是否有权限使用该模型
3. 尝试切换到其他模型（如 deepseek-chat 或 gpt-3.5-turbo）"""
                else:
                    # 其他错误，显示原始错误信息
                    error_msg = f"""**发生错误**

错误信息：`{error_str}`

**可能的解决方案：**
1. 检查网络连接
2. 确认环境变量中的 API Key 和模型配置正确
3. 查看控制台获取更多错误详情
4. 在 Zeabur 项目设置中检查环境变量配置"""
                
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# 底部说明
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>银行智能助手 - 使用 LangChain 和 Streamlit 构建</small>
    </div>
    """,
    unsafe_allow_html=True
)

