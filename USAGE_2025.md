# 获取2025年AI生物医学论文使用指南

## 功能概述

本系统可以从多个数据源获取2025年发表的包含"artificial intelligence"关键词的生物和医学类研究论文，并提取以下信息：

1. **标题**
2. **最后一位通讯作者及其单位**
3. **用API key从摘要中提取**：
   - 论文做了什么
   - 用AI做了什么
   - 用了哪个模型
   - 数据资源

## 支持的数据源

- **medRxiv** - 医学预印本服务器
- **bioRxiv** - 生物学预印本服务器
- **PubMed** - 生物医学文献数据库
- **arXiv** - 预印本服务器（仅生物医学相关分类）

## 快速开始

### 1. 设置环境变量

确保设置了GLM API密钥（推荐）或OpenAI API密钥：

```bash
export GLM_API_KEY="your_glm_api_key"
# 或
export OPENAI_API_KEY="your_openai_api_key"
```

### 2. 运行脚本

```bash
# 使用专用脚本获取2025年的论文
python tools/fetch_2025_ai_papers.py
```

或使用环境变量：

```bash
# 设置年份
export YEAR=2025
export SEARCH_KEYWORD="artificial intelligence"

# 运行主程序
python src/harvest_medrxiv.py
```

## 使用方法

### 方法1：使用专用脚本（推荐）

```bash
python tools/fetch_2025_ai_papers.py
```

这个脚本会自动：
- 筛选2025年发表的论文
- 搜索包含"artificial intelligence"关键词的论文
- 过滤生物和医学类研究
- 提取最后一位通讯作者及其单位
- 使用API从摘要中提取结构化信息

### 方法2：使用Python代码

```python
from src.harvest_medrxiv import MedRxivHarvester

# 创建harvester，指定2025年
harvester = MedRxivHarvester(
    keyword="artificial intelligence",
    year=2025,
    max_articles=200
)

# 执行获取
results = harvester.harvest()

# 查看结果
print(f"获取了 {results['statistics']['total_articles']} 篇论文")
for article in results['articles']:
    print(f"标题: {article['title']}")
    print(f"最后通讯作者: {article['last_corresponding_author']}")
    print(f"单位: {article['last_corresponding_affiliation']}")
    print(f"研究内容: {article['what_done']}")
    print(f"AI作用: {article['ai_role']}")
    print(f"模型: {article['models']}")
    print(f"数据资源: {article['data_sources']}")
    print("---")
```

## 输出文件

执行后会生成以下文件（在`data/`目录下）：

1. **`medrxiv-ai-{timestamp}.json`** - 完整的JSON数据，包含所有提取的信息
2. **`medrxiv-ai-{timestamp}.md`** - 人类可读的Markdown报告
3. **`medrxiv-ai-{timestamp}-summary.json`** - 统计摘要

## 输出字段说明

每篇论文包含以下字段：

- `title` - 论文标题
- `last_corresponding_author` - 最后一位通讯作者
- `last_corresponding_affiliation` - 最后一位通讯作者的单位
- `what_done` - 论文做了什么（从摘要提取）
- `ai_role` - 用AI做了什么（从摘要提取）
- `models` - 使用的模型（从摘要提取）
- `data_sources` - 数据资源（从摘要提取）
- `abstract` - 摘要原文
- `source` - 数据源（medrxiv/biorxiv/pubmed/arxiv）
- `published_at` - 发表时间
- `url` - 论文链接

## 配置选项

可以在代码或环境变量中配置：

```python
harvester = MedRxivHarvester(
    keyword="artificial intelligence",  # 搜索关键词
    year=2025,                          # 筛选年份
    max_articles=200,                   # 最大论文数
    llm_delay=0.5                       # API调用延迟（秒）
)
```

环境变量：
- `SEARCH_KEYWORD` - 搜索关键词（默认："artificial intelligence"）
- `YEAR` - 筛选年份（如：2025）
- `DAYS_BACK` - 如果未指定年份，则使用天数回退
- `GLM_API_KEY` - GLM API密钥
- `OPENAI_API_KEY` - OpenAI API密钥（备用）

## 注意事项

1. **API密钥**：建议使用GLM API密钥以获得更好的中文提取效果
2. **数据源限制**：某些数据源可能有请求频率限制
3. **年份筛选**：指定年份时会忽略`days`参数
4. **生物医学过滤**：PubMed和arXiv会自动过滤为生物医学相关研究

## 故障排除

### 没有找到论文

- 检查网络连接
- 确认数据源可访问
- 尝试调整搜索关键词
- 检查年份是否正确（2025）

### API提取失败

- 检查API密钥是否正确
- 确认API配额未用完
- 系统会自动回退到启发式提取

### 需要帮助

查看日志文件：`logs/harvest.log`

