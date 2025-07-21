#!/bin/bash

echo "=== TalkEnglish.com 优化爬取脚本 ==="
echo ""

# 检查配置文件是否存在
if [ ! -f "talkenglish_optimized.json" ]; then
    echo "❌ 配置文件 talkenglish_optimized.json 不存在"
    echo "请确保配置文件在当前目录中"
    exit 1
fi

echo "✅ 找到配置文件: talkenglish_optimized.json"
echo ""

# 显示配置概览
echo "📊 配置概览:"
echo "URL: $(jq -r '.url' talkenglish_optimized.json)"
echo "页面限制: $(jq -r '.limit' talkenglish_optimized.json)"
echo "最大深度: $(jq -r '.maxDepth' talkenglish_optimized.json)"
echo "等待时间: $(jq -r '.scrapeOptions.waitFor' talkenglish_optimized.json)ms"
echo "包含路径数: $(jq '.includePaths | length' talkenglish_optimized.json)"
echo "排除路径数: $(jq '.excludePaths | length' talkenglish_optimized.json)"
echo ""

read -p "是否继续执行爬取? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "取消执行"
    exit 0
fi

echo ""
echo "🚀 开始执行优化爬取..."

# 执行爬取
curl -X POST http://localhost:3002/v1/crawl \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -d @talkenglish_optimized.json | jq '.' | tee talkenglish_optimized_result.json

echo ""
echo "✅ 爬取任务已提交"
echo "📄 结果保存到: talkenglish_optimized_result.json"

# 提取crawl ID
CRAWL_ID=$(jq -r '.id' talkenglish_optimized_result.json 2>/dev/null)

if [ "$CRAWL_ID" != "null" ] && [ -n "$CRAWL_ID" ]; then
    echo "🆔 Crawl ID: $CRAWL_ID"
    echo ""
    echo "💡 使用以下命令查询进度:"
    echo "   bash check_crawl_status.sh $CRAWL_ID"
    echo ""
    echo "或者运行 Python 监控脚本:"
    echo "   python crawl_with_optimized_config.py"
else
    echo "⚠️  无法提取 Crawl ID，请检查返回结果"
fi