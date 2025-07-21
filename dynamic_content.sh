curl -X POST http://localhost:3002/v1/scrape \
    -H 'Content-Type: application/json' \
    -d '{
        "url": "https://spa-site.com",
        "formats": ["markdown"],
        "waitFor": 5000,
        "actions": [
            {"type": "wait", "milliseconds": 3000},
            {"type": "scroll", "direction": "down"},
            {"type": "wait", "milliseconds": 2000}
        ]
    }'