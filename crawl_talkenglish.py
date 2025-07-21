import requests
import json
import time
import os
from datetime import datetime

class TalkEnglishCrawler:
    def __init__(self, base_url="http://localhost:3002"):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def start_crawl(self):
        """启动爬取任务"""
        crawl_config = {
            "url": "https://www.talkenglish.com/",
            "limit": 2000,  # 增加页面限制
            "scrapeOptions": {
                "formats": ["markdown", "html"],
                "onlyMainContent": True,
                "waitFor": 3000,
                "timeout": 45000,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            },
            "maxDepth": 6,
            "allowBackwardLinks": False,
            "allowExternalLinks": False,
            "includePaths": [
                "/lessons/*",
                "/speaking/*", 
                "/listening/*",
                "/grammar/*",
                "/vocabulary/*",
                "/pronunciation/*",
                "/beginner/*",
                "/intermediate/*",
                "/advanced/*",
                "/business/*",
                "/travel/*"
            ],
            "excludePaths": [
                "/admin/*",
                "/login/*",
                "/register/*",
                "*.pdf",
                "*.mp3",
                "*.wav"
            ]
        }
        
        print("🚀 启动 TalkEnglish.com 全站爬取...")
        response = requests.post(
            f"{self.base_url}/v1/crawl",
            headers=self.headers,
            json=crawl_config
        )
        
        if response.status_code == 200:
            result = response.json()
            crawl_id = result.get('id')
            print(f"✅ 爬取任务已启动，ID: {crawl_id}")
            
            # 保存初始响应
            with open(f"talkenglish_crawl_{crawl_id}.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return crawl_id
        else:
            print(f"❌ 启动爬取失败: {response.status_code}")
            print(response.text)
            return None
    
    def check_status(self, crawl_id):
        """检查爬取状态"""
        response = requests.get(
            f"{self.base_url}/v1/crawl/{crawl_id}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 检查状态失败: {response.status_code}")
            return None
    
    def monitor_crawl(self, crawl_id, check_interval=30):
        """监控爬取进度"""
        print(f"📊 开始监控爬取进度 (每{check_interval}秒检查一次)...")
        
        while True:
            status = self.check_status(crawl_id)
            if not status:
                break
            
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if status.get('status') == 'completed':
                print(f"🎉 [{current_time}] 爬取完成!")
                print(f"📄 总页面数: {len(status.get('data', []))}")
                
                # 保存完整结果
                self.save_results(crawl_id, status)
                break
            
            elif status.get('status') == 'scraping':
                completed = len(status.get('data', []))
                print(f"⏳ [{current_time}] 爬取中... 已完成: {completed} 页面")
            
            elif status.get('status') == 'failed':
                print(f"❌ [{current_time}] 爬取失败")
                print(f"错误信息: {status.get('error', 'Unknown error')}")
                break
            
            time.sleep(check_interval)
    
    def save_results(self, crawl_id, status):
        """保存爬取结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存完整JSON结果
        filename = f"talkenglish_complete_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        print(f"💾 完整结果已保存到: {filename}")
        
        # 提取并保存页面内容
        if 'data' in status:
            self.extract_content(status['data'], timestamp)
    
    def extract_content(self, pages, timestamp):
        """提取和分类页面内容"""
        categories = {
            'lessons': [],
            'speaking': [],
            'listening': [],
            'grammar': [],
            'vocabulary': [],
            'pronunciation': [],
            'other': []
        }
        
        for page in pages:
            url = page.get('metadata', {}).get('url', '')
            title = page.get('metadata', {}).get('title', 'Untitled')
            content = page.get('markdown', '')
            
            # 分类页面
            category = 'other'
            for cat in categories.keys():
                if cat in url.lower():
                    category = cat
                    break
            
            categories[category].append({
                'url': url,
                'title': title,
                'content': content,
                'word_count': len(content.split()) if content else 0
            })
        
        # 保存分类结果
        for category, pages in categories.items():
            if pages:
                filename = f"talkenglish_{category}_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(pages, f, indent=2, ensure_ascii=False)
                print(f"📚 {category.title()} 内容已保存到: {filename} ({len(pages)} 页面)")
        
        # 生成统计报告
        self.generate_report(categories, timestamp)
    
    def generate_report(self, categories, timestamp):
        """生成爬取报告"""
        report = {
            'timestamp': timestamp,
            'total_pages': sum(len(pages) for pages in categories.values()),
            'categories': {}
        }
        
        for category, pages in categories.items():
            if pages:
                total_words = sum(page['word_count'] for page in pages)
                report['categories'][category] = {
                    'page_count': len(pages),
                    'total_words': total_words,
                    'avg_words_per_page': total_words // len(pages) if pages else 0
                }
        
        filename = f"talkenglish_report_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 爬取报告:")
        print(f"总页面数: {report['total_pages']}")
        for category, stats in report['categories'].items():
            print(f"  {category.title()}: {stats['page_count']} 页面, {stats['total_words']} 词")
        print(f"详细报告已保存到: {filename}")

def main():
    crawler = TalkEnglishCrawler()
    
    # 启动爬取
    crawl_id = crawler.start_crawl()
    if crawl_id:
        # 监控进度
        crawler.monitor_crawl(crawl_id)

if __name__ == "__main__":
    main()