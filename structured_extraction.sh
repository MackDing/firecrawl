curl -X POST http://localhost:3002/v1/scrape \
    -H 'Content-Type: application/json' \
    -d '{
        "url": "https://news-site.com",
        "formats": ["json"],
        "extract": {
            "prompt": "Extract article title, author, publish date, and main content"
        }
    }'