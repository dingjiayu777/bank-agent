# 银行智能体系统

一个基于 Streamlit 和 LangChain 的银行智能助手，支持余额查询和转账功能。

## 功能特性

- 💰 **余额查询**：查询指定账户的余额
- 🔄 **转账功能**：在账户之间执行转账操作
- 📋 **账户列表**：查看所有可用账户
- 💬 **自然语言交互**：使用自然语言与智能体对话

## 安装步骤

1. 克隆或下载项目到本地

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 设置 API Key（通过环境变量）：
   - **DeepSeek**: 设置环境变量 `DEEPSEEK_API_KEY=your_api_key_here`
   - **OpenAI**: 设置环境变量 `OPENAI_API_KEY=your_api_key_here`
   
   **Windows (PowerShell):**
   ```powershell
   $env:DEEPSEEK_API_KEY="your_api_key_here"
   ```
   
   **Windows (CMD):**
   ```cmd
   set DEEPSEEK_API_KEY=your_api_key_here
   ```
   
   **Mac/Linux:**
   ```bash
   export DEEPSEEK_API_KEY=your_api_key_here
   ```
   
   **可选环境变量：**
   - `API_PROVIDER`: API 提供商，可选 "deepseek" 或 "openai"（默认: "deepseek"）
   - `MODEL_NAME`: 模型名称（默认: "deepseek-chat"）

## 运行应用

### 方法 1: 使用启动脚本（推荐）

**Windows 用户：**
双击运行 `run.bat` 文件

**Mac/Linux 用户：**
```bash
chmod +x run.sh
./run.sh
```

### 方法 2: 手动启动

```bash
streamlit run app.py
```

或

```bash
python -m streamlit run app.py
```

应用将在浏览器中自动打开，默认地址为 `http://localhost:8501`

**注意：** 应用启动时会自动从环境变量读取 API Key。如果没有设置环境变量，应用会显示错误提示，无法使用智能体功能。

## 使用示例

### 查询余额
```
查询账户1001的余额
```

### 转账操作
```
从账户1001向账户1002转账500元
```

### 列出账户
```
显示所有账户
```

## 项目结构

```
bank-agents/
├── app.py              # Streamlit 前端应用
├── bank_agent.py       # LangChain 智能体后端
├── bank_data.py        # 银行数据存储模块
├── requirements.txt    # Python 依赖包
└── README.md          # 项目说明文档
```

## 技术栈

- **前端**：Streamlit
- **后端**：LangChain
- **LLM**：OpenAI GPT-3.5-turbo / GPT-4
- **语言**：Python 3.8+

## Zeabur 部署

1. **连接 GitHub 仓库**到 Zeabur
2. **配置环境变量**：
   - 在 Zeabur 项目设置中添加以下环境变量：
     - `DEEPSEEK_API_KEY`: 您的 DeepSeek API Key（如果使用 DeepSeek）
     - `OPENAI_API_KEY`: 您的 OpenAI API Key（如果使用 OpenAI）
     - `API_PROVIDER`: 可选，设置为 "deepseek" 或 "openai"（默认: "deepseek"）
     - `MODEL_NAME`: 可选，模型名称（默认: "deepseek-chat"）
3. **部署**：Zeabur 会自动检测 Python 项目并部署

## 注意事项

- 本项目使用内存存储，重启应用后数据会重置
- 需要有效的 API Key（通过环境变量配置）才能使用
- 账户数据为示例数据，可根据需要修改 `bank_data.py` 中的初始化数据
- **重要**：API Key 现在只能通过环境变量配置，不再支持在网页上输入

## 许可证

MIT License

