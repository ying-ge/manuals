# 运行说明

## 重要提示

系统中有两个Python版本：
- `python` → 可能指向 Python 2.7（不兼容）
- `python3` → Python 3.14.0（正确）

## 正确的运行方式

### 方式1：使用 python3 命令（推荐）

```bash
python3 tools/fetch_2025_ai_papers.py
```

### 方式2：直接执行脚本

```bash
./tools/fetch_2025_ai_papers.py
```

### 方式3：使用主程序

```bash
python3 src/harvest_medrxiv.py
```

## 不要使用

❌ **不要使用** `python tools/fetch_2025_ai_papers.py` （这会使用Python 2.7）

## 验证

检查Python版本：
```bash
python3 --version  # 应该显示 Python 3.14.0
```

## 环境变量设置

在运行前，确保设置了API密钥（可选，但推荐）：

```bash
export GLM_API_KEY="your_glm_api_key"
# 或
export OPENAI_API_KEY="your_openai_api_key"
```

## 依赖安装

如果遇到模块缺失错误，安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

