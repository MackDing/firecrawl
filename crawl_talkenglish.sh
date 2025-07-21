#!/bin/bash

echo "开始爬取 TalkEnglish.com 全站内容..."

curl -X POST http://localhost:3002/v1/crawl \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -d '{
        "url": "https://www.talkenglish.com/",
        "limit": 1000,
        "scrapeOptions": {
            "formats": ["markdown", "html"],
            "onlyMainContent": true,
            "waitFor": 2000,
            "timeout": 30000
        },
        "maxDepth": 5,
        "allowBackwardLinks": false,
        "allowExternalLinks": false,
        "includePaths": [
            "/lessons/*",
            "/speaking/*", 
            "/listening/*",
            "/grammar/*",
            "/vocabulary/*",
            "/pronunciation/*"
        ]
    }' | jq '.' | tee talkenglish_crawl_result.json

echo ""
echo "爬取任务已提交，结果保存到 talkenglish_crawl_result.json"
echo "请使用返回的 crawl ID 查询进度"