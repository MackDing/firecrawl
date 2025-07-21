import requests
import json

def extract_and_view():
    url = "http://localhost:3002/v1/scrape"
    
    payload = {
        "url": "https://news-site.com",
        "formats": ["json"],
        "extract": {
            "prompt": "Extract article title, author, publish date, and main content"
        }
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        
        # 打印完整结果
        print("=== 完整结果 ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 提取AI处理的结构化数据
        if result.get("success") and "json" in result.get("data", {}):
            extracted_data = result["data"]["json"]
            print("\n=== AI提取的结构化数据 ===")
            print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
            
            # 保存到文件
            with open("extracted_data.json", "w", encoding="utf-8") as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            print("\n结果已保存到 extracted_data.json")
        else:
            print("提取失败或无结构化数据")
    else:
        print(f"请求失败: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    extract_and_view()