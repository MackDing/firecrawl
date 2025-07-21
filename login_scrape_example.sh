curl -X POST http://localhost:3002/v1/scrape \
    -H 'Content-Type: application/json' \
    -d '{
        "url": "https://protected-site.com/dashboard",
        "formats": ["markdown"],
        "headers": {
            "Cookie": "session_id=abc123; auth_token=xyz789"
        }
    }'