# 安全的API密钥设置方法

⚠️ **重要**：这是公开仓库，**不要**将API密钥提交到代码中！

## 推荐方法：使用环境变量（不保存到文件）

### 方法1：临时设置（最安全，推荐）

在运行脚本时直接设置环境变量：

```bash
GLM_API_KEY='your_actual_api_key_here' python3 tools/fetch_2025_ai_papers.py
```

**优点**：
- ✅ 密钥只在当前终端会话中有效
- ✅ 不会保存到任何文件
- ✅ 关闭终端后自动失效
- ✅ 最安全的方式

### 方法2：在当前会话中设置

```bash
# 设置环境变量（仅当前终端会话有效）
export GLM_API_KEY='your_actual_api_key_here'

# 然后运行脚本
python3 tools/fetch_2025_ai_papers.py
```

**优点**：
- ✅ 可以在同一个终端中多次运行脚本
- ✅ 关闭终端后自动失效
- ⚠️ 注意：其他程序也能读取这个环境变量

### 方法3：使用系统密钥环（macOS）

使用 macOS 的 Keychain 存储密钥：

```bash
# 存储到 Keychain（只需设置一次）
security add-generic-password \
  -a GLM_API_KEY \
  -s "manuals_harvester" \
  -w "your_actual_api_key_here" \
  -U

# 从 Keychain 读取并设置为环境变量
export GLM_API_KEY=$(security find-generic-password -a GLM_API_KEY -s "manuals_harvester" -w)
python3 tools/fetch_2025_ai_papers.py
```

### 方法4：创建本地脚本（不提交到Git）

创建一个不被Git跟踪的本地脚本：

```bash
# 创建本地配置脚本（已在.gitignore中）
cat > .env.local << 'EOF'
#!/bin/bash
export GLM_API_KEY='your_actual_api_key_here'
EOF

chmod +x .env.local
source .env.local
python3 tools/fetch_2025_ai_papers.py
```

确保 `.env.local` 在 `.gitignore` 中（应该已经在里面了）。

## 验证设置

检查环境变量是否设置成功：

```bash
# 检查是否设置（不会显示完整密钥）
if [ -n "$GLM_API_KEY" ]; then
  echo "✓ GLM_API_KEY已设置（长度: ${#GLM_API_KEY} 字符）"
else
  echo "✗ GLM_API_KEY未设置"
fi
```

## 注意事项

1. ✅ **永远不要**将API密钥提交到Git
2. ✅ **永远不要**在代码中硬编码密钥
3. ✅ `.env` 文件已在 `.gitignore` 中（第40行）
4. ✅ 即使使用 `.env` 文件，也不要提交它
5. ✅ 使用环境变量是最安全的做法

## 快速开始

最简单的运行方式：

```bash
GLM_API_KEY='your_key' python3 tools/fetch_2025_ai_papers.py
```

这样就完全不会在文件中留下任何痕迹！

