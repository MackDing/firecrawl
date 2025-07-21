curl -X POST http://localhost:3002/v1/scrape \
    -H 'Content-Type: application/json' \
    -d '{
        "url": "https://api-protected-site.com/data",
        "formats": ["markdown"],
        "headers": {
            "Authorization": "Bearer your-jwt-token",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    }'