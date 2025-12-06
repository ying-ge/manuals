# 如何运行 medRxiv AI 文章收集系统

## 首次运行 - 提取2025年全部文章

### 方法1：使用 GitHub Actions（推荐）

1. **前往 GitHub Actions 页面**
   - 打开仓库：https://github.com/ying-ge/manuals
   - 点击 "Actions" 标签
   - 选择 "Scrape medRxiv AI Articles" 工作流

2. **手动触发工作流**
   - 点击 "Run workflow" 按钮
   - 设置参数：
     - **Search keyword**: `artificial intelligence` (默认)
     - **Days to look back**: `365` (获取2025年全部文章)
   - 点击 "Run workflow" 开始运行

3. **查看结果**
   - 工作流运行完成后会自动创建一个 Pull Request
   - PR 中包含提取的所有文章数据
   - 检查并合并 PR

### 方法2：本地运行

1. **设置环境**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   
   # 创建 .env 文件（如果还没有）
   cp .env.example .env
   ```

2. **配置 API Key**
   编辑 `.env` 文件，添加：
   ```
   GLM_API_KEY=your_glm_api_key_here
   GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
   GLM_MODEL_NAME=glm-4.6
   ```

3. **运行收集（2025年全部文章）**
   ```bash
   # 提取2025年全部文章（365天）
   DAYS_BACK=365 python tools/run_once.py
   ```

4. **查看结果**
   ```bash
   # 查看生成的文件
   ls -lh data/medrxiv-ai-*.json
   ls -lh data/medrxiv-ai-*.md
   ```

---

## 定期运行 - 每周更新

### GitHub Actions 自动运行

工作流已配置为**每周一凌晨2点 UTC** 自动运行，无需手动操作。

- **运行时间**：每周一 02:00 UTC
- **默认参数**：
  - Search keyword: "artificial intelligence"
  - Days back: 30 (最近30天的文章)
- **输出**：自动创建 PR 包含新文章

### 修改运行频率（可选）

如需修改运行频率，编辑 `.github/workflows/scrape.yml`：

```yaml
on:
  schedule:
    # 当前：每周一运行
    - cron: '0 2 * * 1'
    
    # 改为每日运行：
    # - cron: '0 2 * * *'
    
    # 改为每月1号运行：
    # - cron: '0 2 1 * *'
```

---

## 参数说明

### SEARCH_KEYWORD
搜索关键词，默认 "artificial intelligence"

**示例：**
```bash
# 搜索 "machine learning"
SEARCH_KEYWORD="machine learning" python tools/run_once.py

# 搜索 "deep learning"
SEARCH_KEYWORD="deep learning" DAYS_BACK=365 python tools/run_once.py
```

### DAYS_BACK
回溯天数，默认 30 天

**常用设置：**
- `7` - 最近一周
- `30` - 最近一个月（默认）
- `90` - 最近三个月
- `365` - 整年（首次运行推荐）

**示例：**
```bash
# 最近7天
DAYS_BACK=7 python tools/run_once.py

# 最近90天
DAYS_BACK=90 python tools/run_once.py

# 2025年全部
DAYS_BACK=365 python tools/run_once.py
```

---

## 输出文件说明

每次运行生成3个文件（带时间戳）：

### 1. JSON 文件
`data/medrxiv-ai-{timestamp}.json`

完整结构化数据，包含：
- 文章元数据（标题、作者、DOI等）
- 提取的信息（what_done、ai_role、models等）
- **what_done** 和 **ai_role** 为中文
- **models**、**data_sources**、**metrics** 为英文

### 2. Markdown 文件
`data/medrxiv-ai-{timestamp}.md`

人类可读的报告格式，便于快速浏览

### 3. Summary 文件
`data/medrxiv-ai-{timestamp}-summary.json`

统计摘要：
- 总文章数
- 来源分布
- 需要人工审核的文章列表

---

## 检查运行状态

### GitHub Actions

1. 访问 Actions 页面
2. 查看最近的工作流运行
3. 绿色勾号 = 成功
4. 红色叉号 = 失败（查看日志排查问题）

### 本地运行

成功标志：
```
✓ Harvest completed successfully!
Check the data/ directory for output files
```

失败排查：
- 检查 `logs/harvest.log` 获取详细错误信息
- 确认 GLM_API_KEY 设置正确
- 确认网络连接正常

---

## 常见问题

### Q: 如何获取 GLM API Key？
A: 访问 [BigModel](https://open.bigmodel.cn/) 注册并获取 API key

### Q: 首次运行应该设置多少天？
A: 建议设置 `DAYS_BACK=365` 获取2025年所有文章

### Q: 如何只获取新文章？
A: 系统有缓存机制，会自动跳过已处理的文章。每周运行使用默认30天即可。

### Q: 可以搜索其他关键词吗？
A: 可以，设置 `SEARCH_KEYWORD` 环境变量即可

### Q: 提取的中文内容准确吗？
A: 使用 GLM4.6 提取质量很高。如有问题，检查 `needs_manual_review` 标记的文章。

---

## 快速命令参考

```bash
# 首次运行 - 2025年全部文章
DAYS_BACK=365 python tools/run_once.py

# 每周更新 - 最近30天
python tools/run_once.py

# 自定义搜索
SEARCH_KEYWORD="neural network" DAYS_BACK=90 python tools/run_once.py

# 检查最新结果
ls -lht data/*.json | head -3
cat data/medrxiv-ai-*-summary.json | tail -1 | jq
```

---

## 技术支持

如遇问题，请检查：
1. `logs/harvest.log` - 详细运行日志
2. GitHub Actions 日志 - 工作流运行详情
3. 确保 API key 正确配置
4. 网络连接正常

---

*最后更新：2025-10-31*
