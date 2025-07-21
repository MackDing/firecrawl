#!/bin/bash

echo "开始AI结构化提取..."

curl -X POST http://localhost:3002/v1/scrape \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -v \
    -d '{
        "url": "https://news-site.com",
        "formats": ["json"],
        "extract": {
            "prompt": "Extract article title, author, publish date, and main content"
        }
    }' | jq '.' | tee extraction_result.json

echo ""
echo "结果已保存到 extraction_result.json"
echo "AI提取的数据位于 .data.json 字段中"