import requests
import json
import time
from datetime import datetime

class OptimizedTalkEnglishCrawler:
    def __init__(self, base_url="http://localhost:3002", config_file="talkenglish_optimized.json"):
        self.base_url = base_url
        self.config_file = config_file
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def load_config(self):
        """加载优化配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ 已加载配置文件: {self.config_file}")
            return config
        except FileNotFoundError:
            print(f"❌ 配置文件未找到: {self.config_file}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            return None
    
    def start_crawl(self):
        """使用优化配置启动爬取"""
        config = self.load_config()
        if not config:
            return None
        
        print("🚀 使用优化配置启动 TalkEnglish.com 全站爬取...")
        print(f"📊 配置详情:")
        print(f"  - 页面限制: {config.get('limit', 'N/A')}")
        print(f"  - 最大深度: {config.get('maxDepth', 'N/A')}")
        print(f"  - 等待时间: {config.get('scrapeOptions', {}).get('waitFor', 'N/A')}ms")
        print(f"  - 超时时间: {config.get('scrapeOptions', {}).get('timeout', 'N/A')}ms")
        print(f"  - 包含路径: {len(config.get('includePaths', []))} 个")
        print(f"  - 排除路径: {len(config.get('excludePaths', []))} 个")
        
        response = requests.post(
            f"{self.base_url}/v1/crawl",
            headers=self.headers,
            json=config
        )
        
        if response.status_code == 200:
            result = response.json()
            crawl_id = result.get('id')
            print(f"✅ 爬取任务已启动，ID: {crawl_id}")
            
            # 保存初始响应
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"talkenglish_optimized_crawl_{timestamp}.json", "w", encoding="utf-8") as f:
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
    
    def monitor_crawl(self, crawl_id, check_interval=60):
        """监控爬取进度（优化配置可能需要更长时间）"""
        print(f"📊 开始监控爬取进度 (每{check_interval}秒检查一次)...")
        print("⚠️  由于使用了优化配置，爬取可能需要较长时间，请耐心等待...")
        
        start_time = datetime.now()
        
        while True:
            status = self.check_status(crawl_id)
            if not status:
                break
            
            current_time = datetime.now().strftime("%H:%M:%S")
            elapsed = datetime.now() - start_time
            
            if status.get('status') == 'completed':
                print(f"🎉 [{current_time}] 爬取完成! 总耗时: {elapsed}")
                print(f"📄 总页面数: {len(status.get('data', []))}")
                
                # 保存完整结果
                self.save_results(crawl_id, status)
                break
            
            elif status.get('status') == 'scraping':
                completed = len(status.get('data', []))
                print(f"⏳ [{current_time}] 爬取中... 已完成: {completed} 页面 (耗时: {elapsed})")
            
            elif status.get('status') == 'failed':
                print(f"❌ [{current_time}] 爬取失败 (耗时: {elapsed})")
                print(f"错误信息: {status.get('error', 'Unknown error')}")
                break
            
            time.sleep(check_interval)
    
    def save_results(self, crawl_id, status):
        """保存爬取结果并按类别分类"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存完整JSON结果
        filename = f"talkenglish_optimized_complete_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        print(f"💾 完整结果已保存到: {filename}")
        
        # 提取并保存页面内容
        if 'data' in status:
            self.extract_and_categorize_content(status['data'], timestamp)
    
    def extract_and_categorize_content(self, pages, timestamp):
        """提取和分类页面内容（基于优化配置的路径）"""
        categories = {
            'lessons': [],
            'speaking': [],
            'listening': [],
            'grammar': [],
            'vocabulary': [],
            'pronunciation': [],
            'beginner': [],
            'intermediate': [],
            'advanced': [],
            'business': [],
            'travel': [],
            'toefl': [],
            'ielts': [],
            'interview': [],
            'other': []
        }
        
        for page in pages:
            url = page.get('metadata', {}).get('url', '')
            title = page.get('metadata', {}).get('title', 'Untitled')
            content = page.get('markdown', '')
            
            # 分类页面（基于URL路径）
            category = 'other'
            for cat in categories.keys():
                if f"/{cat}/" in url.lower():
                    category = cat
                    break
            
            page_info = {
                'url': url,
                'title': title,
                'content': content,
                'word_count': len(content.split()) if content else 0,
                'char_count': len(content) if content else 0
            }
            
            categories[category].append(page_info)
        
        # 保存分类结果
        for category, pages_list in categories.items():
            if pages_list:
                filename = f"talkenglish_optimized_{category}_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(pages_list, f, indent=2, ensure_ascii=False)
                print(f"📚 {category.title()} 内容已保存到: {filename} ({len(pages_list)} 页面)")
        
        # 生成详细统计报告
        self.generate_detailed_report(categories, timestamp)
    
    def generate_detailed_report(self, categories, timestamp):
        """生成详细的爬取报告"""
        total_pages = sum(len(pages) for pages in categories.values())
        total_words = sum(sum(page['word_count'] for page in pages) for pages in categories.values())
        
        report = {
            'timestamp': timestamp,
            'config_file': self.config_file,
            'total_pages': total_pages,
            'total_words': total_words,
            'categories': {}
        }
        
        for category, pages in categories.items():
            if pages:
                category_words = sum(page['word_count'] for page in pages)
                category_chars = sum(page['char_count'] for page in pages)
                report['categories'][category] = {
                    'page_count': len(pages),
                    'total_words': category_words,
                    'total_chars': category_chars,
                    'avg_words_per_page': category_words // len(pages) if pages else 0,
                    'percentage_of_total': round((len(pages) / total_pages) * 100, 2) if total_pages > 0 else 0
                }
        
        filename = f"talkenglish_optimized_report_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 详细爬取报告:")
        print(f"配置文件: {self.config_file}")
        print(f"总页面数: {report['total_pages']}")
        print(f"总词数: {report['total_words']:,}")
        print(f"\n各类别统计:")
        for category, stats in report['categories'].items():
            print(f"  {category.title()}: {stats['page_count']} 页面 ({stats['percentage_of_total']}%), {stats['total_words']:,} 词")
        print(f"\n详细报告已保存到: {filename}")

def main():
    crawler = OptimizedTalkEnglishCrawler()
    
    # 启动爬取
    crawl_id = crawler.start_crawl()
    if crawl_id:
        # 监控进度（使用更长的检查间隔，因为优化配置可能需要更多时间）
        crawler.monitor_crawl(crawl_id, check_interval=60)

if __name__ == "__main__":
    main()