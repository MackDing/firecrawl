#!/bin/bash

if [ -z "$1" ]; then
    echo "用法: $0 <crawl_id>"
    echo "例如: $0 abc123def456"
    exit 1
fi

CRAWL_ID=$1

echo "查询爬取状态: $CRAWL_ID"

curl -X GET "http://localhost:3002/v1/crawl/$CRAWL_ID" \
    -H 'Accept: application/json' \
    | jq '.'