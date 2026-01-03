"""
银行智能体后端 - 使用 LangChain 构建
"""
from langchain_classic.agents import AgentExecutor, create_openai_functions_agent
from langchain_classic.tools import tool
from langchain_openai import ChatOpenAI
from langchain_classic.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Optional
from bank_data import bank_db

# 定义余额查询工具
@tool
def check_balance(account_id: str) -> str:
    """
    查询账户余额
    
    Args:
        account_id: 账户ID，例如 "1001"
    
    Returns:
        账户余额信息字符串
    """
    account = bank_db.get_account(account_id)
    if not account:
        return f"账户 {account_id} 不存在"
    
    balance = bank_db.get_balance(account_id)
    return f"账户 {account_id} ({account.name}) 的当前余额为: {balance} 元"

# 定义转账工具
@tool
def transfer_money(from_account_id: str, to_account_id: str, amount: float) -> str:
    """
    执行转账操作
    
    Args:
        from_account_id: 源账户ID
        to_account_id: 目标账户ID
        amount: 转账金额（必须大于0）
    
    Returns:
        转账结果信息字符串
    """
    result = bank_db.transfer(from_account_id, to_account_id, amount)
    if result["success"]:
        return result["message"]
    else:
        return f"转账失败: {result['message']}"

# 定义账户列表工具
@tool
def list_accounts() -> str:
    """
    列出所有可用账户
    
    Returns:
        所有账户的列表信息
    """
    accounts = bank_db.list_accounts()
    if not accounts:
        return "没有可用账户"
    
    account_list = "\n".join([
        f"账户ID: {acc['account_id']}, 姓名: {acc['name']}, 余额: {acc['balance']} 元"
        for acc in accounts
    ])
    return f"可用账户列表:\n{account_list}"

def create_bank_agent(api_key: str, model_name: str = "gpt-3.5-turbo", api_provider: str = "openai"):
    """
    创建银行智能体
    
    Args:
        api_key: API 密钥（支持 OpenAI 或 DeepSeek）
        model_name: 使用的模型名称
            - OpenAI: gpt-3.5-turbo, gpt-4 等
            - DeepSeek: deepseek-chat, deepseek-chat-v2 等
        api_provider: API 提供商，可选 "openai" 或 "deepseek"
    
    Returns:
        AgentExecutor 实例
    """
    # 根据提供商配置 base_url
    if api_provider.lower() == "deepseek":
        base_url = "https://api.deepseek.com"
        # 如果未指定模型，使用 DeepSeek 默认模型
        if model_name == "gpt-3.5-turbo":
            model_name = "deepseek-chat"
    else:
        base_url = None  # OpenAI 使用默认 base_url
    
    # 初始化 LLM
    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        openai_api_key=api_key,
        base_url=base_url
    )
    
    # 定义工具列表
    tools = [check_balance, transfer_money, list_accounts]
    
    # 定义提示词模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的银行智能助手。你的职责是帮助用户查询账户余额和执行转账操作。

你可以使用的工具：
1. check_balance - 查询指定账户的余额
2. transfer_money - 执行转账操作
3. list_accounts - 列出所有可用账户

重要提示：
- 使用工具后，必须根据工具返回的结果，用自然、友好的中文向用户解释结果
- 不要直接返回工具调用的 JSON 格式，而是要用通俗易懂的语言告诉用户结果
- 使用友好的语气与用户交流
- 在执行转账前确认账户ID和金额
- 提供清晰的操作结果反馈
- 如果用户询问账户信息，可以使用 list_accounts 工具查看可用账户

当前可用账户示例：
- 账户ID: 1001, 姓名: 张三
- 账户ID: 1002, 姓名: 李四
- 账户ID: 1003, 姓名: 王五

请始终用中文回复用户，并在使用工具后提供清晰的解释。"""),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # 创建智能体
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # 创建执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,  # 关闭详细输出
        handle_parsing_errors=True
    )
    
    return agent_executor


