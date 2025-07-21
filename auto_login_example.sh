curl -X POST http://localhost:3002/v1/scrape \
    -H 'Content-Type: application/json' \
    -d '{
        "url": "https://example.com/login",
        "formats": ["markdown"],
        "actions": [
            {"type": "wait", "milliseconds": 2000},
            {"type": "click", "selector": "input[name=\"username\"]"},
            {"type": "write", "text": "your-username"},
            {"type": "click", "selector": "input[name=\"password\"]"},
            {"type": "write", "text": "your-password"},
            {"type": "click", "selector": "button[type=\"submit\"]"},
            {"type": "wait", "milliseconds": 3000},
            {"type": "navigate", "url": "https://example.com/protected-page"}
        ]
    }'