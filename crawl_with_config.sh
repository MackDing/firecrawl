#!/bin/bash

echo "使用优化配置爬取 TalkEnglish.com..."

curl -X POST http://localhost:3002/v1/crawl \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -d @talkenglish_optimized.json | jq '.' | tee talkenglish_crawl_result.json

echo ""
echo "爬取任务已提交，结果保存到 talkenglish_crawl_result.json"
echo "请使用返回的 crawl ID 查询进度"