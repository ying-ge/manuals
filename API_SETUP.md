# API密钥设置指南

## 快速设置（3步）

### 1. 复制示例文件

```bash
cp .env.example .env
```

### 2. 编辑 .env 文件

使用文本编辑器打开 `.env` 文件，添加您的API密钥：

```bash
# GLM API密钥（推荐，支持中文提取）
GLM_API_KEY=your_glm_api_key_here
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
GLM_MODEL_NAME=glm-4.6

# OpenAI API密钥（可选，备用）
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 获取API密钥

#### GLM API密钥（推荐）

1. 访问 [BigModel开放平台](https://open.bigmodel.cn/)
2. 注册/登录账号
3. 进入"API密钥"页面
4. 创建新密钥
5. 复制密钥到 `.env` 文件

#### OpenAI API密钥（可选）

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账号
3. 进入"API Keys"页面
4. 创建新密钥
5. 复制密钥到 `.env` 文件

## 验证设置

运行脚本检查：

```bash
python3 tools/fetch_2025_ai_papers.py
```

如果看到：
- ✅ **"GLM client initialized successfully"** → 设置成功
- ⚠️ **"[警告] 未检测到API密钥"** → 需要检查`.env`文件

## 临时设置（不使用.env文件）

您也可以临时设置环境变量：

```bash
export GLM_API_KEY="your_api_key_here"
python3 tools/fetch_2025_ai_papers.py
```

## 不使用API密钥

如果没有API密钥，脚本会：
- ⚠️ 使用启发式方法提取信息
- ⚠️ 提取准确性较低
- ✅ 仍然可以获取论文元数据（标题、作者等）

直接按回车键继续即可。

## 提示

- `.env` 文件包含敏感信息，**不要**提交到Git仓库
- 如果使用Git，`.env` 应该在 `.gitignore` 中

