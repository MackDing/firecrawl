#!/bin/bash

echo "🌐 TalkEnglish.com 全媒体爬取脚本"
echo "=================================="
echo "🎯 将爬取网站所有内容，包括:"
echo "   - 📄 所有页面内容 (HTML/Markdown)"
echo "   - 🎵 音频文件 (MP3, WAV, OGG等)"
echo "   - 🎬 视频文件 (MP4, WebM, AVI等)"
echo "   - 🖼️  图片文件 (JPG, PNG, GIF等)"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查并安装依赖
echo "📦 检查Python依赖..."
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装requests库..."
    pip3 install requests
fi

# 检查配置文件
if [ ! -f "talkenglish_full_media_config.json" ]; then
    echo "❌ 配置文件 talkenglish_full_media_config.json 不存在"
    echo "请确保配置文件在当前目录中"
    exit 1
fi

echo "✅ 环境检查完成"
echo ""

# 显示配置信息
echo "📊 爬取配置:"
echo "  - 目标网站: $(jq -r '.url' talkenglish_full_media_config.json)"
echo "  - 页面限制: $(jq -r '.limit' talkenglish_full_media_config.json)"
echo "  - 最大深度: $(jq -r '.maxDepth' talkenglish_full_media_config.json)"
echo "  - 等待时间: $(jq -r '.scrapeOptions.waitFor' talkenglish_full_media_config.json)ms"
echo "  - 超时时间: $(jq -r '.scrapeOptions.timeout' talkenglish_full_media_config.json)ms"
echo "  - 包含路径: $(jq '.includePaths | length' talkenglish_full_media_config.json) 个"
echo "  - 排除路径: $(jq '.excludePaths | length' talkenglish_full_media_config.json) 个"
echo ""

# 预估时间和空间
echo "⏱️  预估信息:"
echo "  - 预计爬取时间: 2-6小时 (取决于网站响应速度)"
echo "  - 预计存储空间: 1-5GB (包含所有媒体文件)"
echo "  - 结果目录: results/talkenglish_$(date +%Y%m%d_%H%M%S)/"
echo ""

read -p "⚠️  这将是一个长时间运行的任务，是否继续? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "❌ 取消执行"
    exit 0
fi

echo ""
echo "🚀 开始全媒体爬取..."
echo "📁 结果将按日期保存到 results/ 目录"
echo "⏳ 请耐心等待，这可能需要几个小时..."
echo ""

# 记录开始时间
START_TIME=$(date)
echo "🕐 开始时间: $START_TIME"
echo ""

# 运行Python脚本
python3 talkenglish_full_crawler.py

# 记录结束时间
END_TIME=$(date)
echo ""
echo "🕐 结束时间: $END_TIME"
echo "✅ 全媒体爬取完成！"
echo ""

# 显示结果目录
if [ -d "results" ]; then
    echo "📂 结果目录:"
    ls -la results/ | grep talkenglish
    echo ""
    echo "💡 查看详细结果:"
    echo "   cd results/talkenglish_*/"
    echo "   ls -la"
fi