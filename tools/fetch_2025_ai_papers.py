#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取2025年发表的包含"artificial intelligence"关键词的生物和医学类研究论文。

提取信息：
- 标题
- 最后一位通讯作者及其单位
- 用API key从摘要中提取：论文做了什么、用AI做了什么、用了哪个模型、数据资源
"""
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from harvest_medrxiv import MedRxivHarvester

def main():
    """主函数：获取2025年的AI生物医学论文"""
    print("=" * 100)
    print("获取2025年AI生物医学研究论文")
    print("=" * 100)
    print()
    print("此脚本将：")
    print("1. 从多个数据源获取论文（medRxiv, bioRxiv, PubMed, arXiv）")
    print("2. 筛选2025年发表的论文")
    print("3. 过滤包含'artificial intelligence'关键词的生物和医学类研究")
    print("4. 提取最后一位通讯作者及其单位")
    print("5. 使用API key从摘要中提取：论文做了什么、用AI做了什么、用了哪个模型、数据资源")
    print()
    print("=" * 100)
    print()
    
    # 确保日志目录存在
    Path('logs').mkdir(exist_ok=True)
    
    # 检查API key
    if not os.getenv('GLM_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        print("[警告] 未检测到GLM_API_KEY或OPENAI_API_KEY")
        print("   将使用启发式方法提取，结果可能不准确")
        print()
        print("提示：要获得更好的提取效果，请设置API密钥（安全方式）：")
        print("  临时设置环境变量（推荐，不保存到文件）：")
        print("    export GLM_API_KEY='your_key_here'")
        print("    python3 tools/fetch_2025_ai_papers.py")
        print()
        print("  或在同一行运行：")
        print("    GLM_API_KEY='your_key_here' python3 tools/fetch_2025_ai_papers.py")
        print()
        import sys
        response = input("是否继续使用启发式方法？(y/n，默认y): ").strip().lower()
        if response and response != 'y':
            print("已取消")
            return 0
        print()
    
    # 创建harvester，指定2025年
    harvester = MedRxivHarvester(
        keyword="artificial intelligence",  # 搜索关键词
        year=2025,                          # 筛选2025年
        max_articles=200,                   # 最多获取200篇
        llm_delay=0.5                       # API调用延迟
    )
    
    print("开始获取论文...")
    print()
    
    try:
        # 执行获取
        results = harvester.harvest()
        
        # 显示结果摘要
        print()
        print("=" * 100)
        print("获取完成！")
        print("=" * 100)
        print()
        print("统计信息：")
        print(f"   - 总论文数: {results['statistics']['total_articles']}")
        print(f"   - 数据源分布:")
        for source, count in results['statistics']['source_breakdown'].items():
            print(f"     - {source}: {count} 篇")
        print(f"   - 需要人工审核: {results['statistics']['needs_manual_review']['count']} 篇")
        print()
        print("输出文件：")
        for key, path in results['output_files'].items():
            print(f"   - {key}: {path}")
        print()
        print("=" * 100)
        print()
        print("[完成] 所有论文信息已保存到 data/ 目录")
        print()
        
        # 显示前几篇论文的示例
        if results['articles']:
            print("示例论文（前3篇）：")
            print()
            for i, article in enumerate(results['articles'][:3], 1):
                print(f"{i}. {article.get('title', 'Untitled')[:80]}...")
                print(f"   最后通讯作者: {article.get('last_corresponding_author', 'N/A')}")
                print(f"   单位: {article.get('last_corresponding_affiliation', 'N/A')}")
                print(f"   数据源: {article.get('source', 'unknown')}")
                if article.get('what_done'):
                    print(f"   研究内容: {article.get('what_done', '')[:100]}...")
                print()
        
        return 0
    
    except Exception as e:
        print(f"[错误] 获取失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

