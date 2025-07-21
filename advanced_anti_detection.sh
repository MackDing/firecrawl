curl -X POST http://localhost:3002/v1/crawl \
    -H 'Content-Type: application/json' \
    -d '{
        "url": "https://target-site.com",
        "limit": 50,
        "scrapeOptions": {
            "formats": ["markdown"],
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            },
            "waitFor": 5000,
            "timeout": 45000
        },
        "maxDepth": 3,
        "allowBackwardLinks": false,
        "allowExternalLinks": false
    }'