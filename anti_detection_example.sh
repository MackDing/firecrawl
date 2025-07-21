curl -X POST http://localhost:3002/v1/scrape \
    -H 'Content-Type: application/json' \
    -d '{
        "url": "https://target-site.com",
        "formats": ["markdown"],
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://google.com"
        },
        "waitFor": 3000,
        "timeout": 30000
    }'