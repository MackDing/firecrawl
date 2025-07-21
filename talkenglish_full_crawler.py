import requests
import json
import time
import os
import re
import urllib.parse
from datetime import datetime
from pathlib import Path
import mimetypes
from urllib.parse import urljoin, urlparse

class TalkEnglishFullCrawler:
    def __init__(self, base_url="http://localhost:3002", config_file="talkenglish_full_media_config.json"):
        self.base_url = base_url
        self.config_file = config_file
        
        # 创建带日期的目录名
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = Path("results") / f"talkenglish_{self.timestamp}"
        
        # 子目录结构
        self.audio_dir = self.session_dir / "audio"
        self.video_dir = self.session_dir / "video"
        self.images_dir = self.session_dir / "images"
        self.content_dir = self.session_dir / "content"
        self.reports_dir = self.session_dir / "reports"
        self.raw_data_dir = self.session_dir / "raw_data"
        
        # 创建目录结构
        self.create_directories()
        
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # 媒体文件统计
        self.media_stats = {
            'audio': {'found': 0, 'downloaded': 0, 'failed': 0},
            'video': {'found': 0, 'downloaded': 0, 'failed': 0},
            'images': {'found': 0, 'downloaded': 0, 'failed': 0}
        }
    
    def create_directories(self):
        """创建完整的目录结构"""
        directories = [
            self.session_dir,
            self.audio_dir,
            self.video_dir,
            self.images_dir,
            self.content_dir,
            self.reports_dir,
            self.raw_data_dir,
            # 内容分类目录
            self.content_dir / "lessons",
            self.content_dir / "speaking",
            self.content_dir / "listening",
            self.content_dir / "grammar",
            self.content_dir / "vocabulary",
            self.content_dir / "pronunciation",
            self.content_dir / "beginner",
            self.content_dir / "intermediate",
            self.content_dir / "advanced",
            self.content_dir / "business",
            self.content_dir / "travel",
            self.content_dir / "toefl",
            self.content_dir / "ielts",
            self.content_dir / "interview",
            self.content_dir / "practice",
            self.content_dir / "other"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 已创建会话目录: {self.session_dir.absolute()}")
        print(f"📅 会话时间: {self.timestamp}")
    
    def load_config(self):
        """加载配置文件"""
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
        """启动全媒体爬取"""
        config = self.load_config()
        if not config:
            return None
        
        print("🚀 启动 TalkEnglish.com 全媒体爬取...")
        print(f"🎯 目标网站: {config.get('url')}")
        print(f"📊 配置详情:")
        print(f"  - 页面限制: {config.get('limit', 'N/A')}")
        print(f"  - 最大深度: {config.get('maxDepth', 'N/A')}")
        print(f"  - 等待时间: {config.get('scrapeOptions', {}).get('waitFor', 'N/A')}ms")
        print(f"  - 超时时间: {config.get('scrapeOptions', {}).get('timeout', 'N/A')}ms")
        print(f"  - 包含路径: {len(config.get('includePaths', []))} 个")
        print(f"  - 排除路径: {len(config.get('excludePaths', []))} 个")
        print(f"📁 结果保存到: {self.session_dir.absolute()}")
        
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
            initial_file = self.reports_dir / f"crawl_start.json"
            with open(initial_file, "w", encoding="utf-8") as f:
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
    
    def extract_media_urls(self, content, base_url="https://www.talkenglish.com"):
        """从内容中提取所有媒体文件URL"""
        media_urls = {
            'audio': set(),
            'video': set(),
            'images': set()
        }
        
        # 音频文件模式
        audio_patterns = [
            r'https?://[^\s\'")]+\.(?:mp3|wav|ogg|m4a|aac|flac)(?:\?[^\s\'")]*)?',
            r'src=["\']([^"\']*\.(?:mp3|wav|ogg|m4a|aac|flac)(?:\?[^"\']*)?)["\']',
            r'href=["\']([^"\']*\.(?:mp3|wav|ogg|m4a|aac|flac)(?:\?[^"\']*)?)["\']',
            r'data-src=["\']([^"\']*\.(?:mp3|wav|ogg|m4a|aac|flac)(?:\?[^"\']*)?)["\']',
            r'data-audio=["\']([^"\']*)["\']',
            r'audio-url=["\']([^"\']*)["\']'
        ]
        
        # 视频文件模式
        video_patterns = [
            r'https?://[^\s\'")]+\.(?:mp4|avi|mov|wmv|flv|webm|mkv|m4v)(?:\?[^\s\'")]*)?',
            r'src=["\']([^"\']*\.(?:mp4|avi|mov|wmv|flv|webm|mkv|m4v)(?:\?[^"\']*)?)["\']',
            r'data-src=["\']([^"\']*\.(?:mp4|avi|mov|wmv|flv|webm|mkv|m4v)(?:\?[^"\']*)?)["\']',
            r'data-video=["\']([^"\']*)["\']',
            r'video-url=["\']([^"\']*)["\']',
            # YouTube, Vimeo等嵌入视频
            r'https?://(?:www\.)?youtube\.com/embed/([^"\'?\s]+)',
            r'https?://(?:www\.)?youtube\.com/watch\?v=([^"\'&\s]+)',
            r'https?://(?:www\.)?vimeo\.com/(\d+)',
            r'https?://player\.vimeo\.com/video/(\d+)'
        ]
        
        # 图片文件模式
        image_patterns = [
            r'https?://[^\s\'")]+\.(?:jpg|jpeg|png|gif|bmp|svg|webp|ico)(?:\?[^\s\'")]*)?',
            r'src=["\']([^"\']*\.(?:jpg|jpeg|png|gif|bmp|svg|webp|ico)(?:\?[^"\']*)?)["\']',
            r'data-src=["\']([^"\']*\.(?:jpg|jpeg|png|gif|bmp|svg|webp|ico)(?:\?[^"\']*)?)["\']',
            r'background-image:\s*url\(["\']?([^"\')\s]*\.(?:jpg|jpeg|png|gif|bmp|svg|webp))(?:\?[^"\')\s]*)?["\']?\)'
        ]
        
        # 提取音频URL
        for pattern in audio_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else (match[1] if len(match) > 1 else '')
                if match:
                    # 处理相对URL
                    if match.startswith('/'):
                        match = urljoin(base_url, match)
                    elif not match.startswith('http'):
                        match = urljoin(base_url, match)
                    media_urls['audio'].add(match)
        
        # 提取视频URL
        for pattern in video_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else (match[1] if len(match) > 1 else '')
                if match:
                    # 处理YouTube/Vimeo ID
                    if 'youtube.com' in pattern or 'vimeo.com' in pattern:
                        if 'youtube' in pattern:
                            match = f"https://www.youtube.com/watch?v={match}"
                        elif 'vimeo' in pattern:
                            match = f"https://vimeo.com/{match}"
                    elif match.startswith('/'):
                        match = urljoin(base_url, match)
                    elif not match.startswith('http'):
                        match = urljoin(base_url, match)
                    media_urls['video'].add(match)
        
        # 提取图片URL
        for pattern in image_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else (match[1] if len(match) > 1 else '')
                if match:
                    if match.startswith('/'):
                        match = urljoin(base_url, match)
                    elif not match.startswith('http'):
                        match = urljoin(base_url, match)
                    media_urls['images'].add(match)
        
        # 转换为列表
        for media_type in media_urls:
            media_urls[media_type] = list(media_urls[media_type])
        
        return media_urls
    
    def download_media_file(self, url, media_type, filename=None):
        """下载媒体文件"""
        try:
            # 确定保存目录
            if media_type == 'audio':
                save_dir = self.audio_dir
            elif media_type == 'video':
                save_dir = self.video_dir
            elif media_type == 'images':
                save_dir = self.images_dir
            else:
                return None
            
            # 生成文件名
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    # 根据媒体类型生成默认文件名
                    ext_map = {
                        'audio': '.mp3',
                        'video': '.mp4',
                        'images': '.jpg'
                    }
                    timestamp = int(time.time())
                    filename = f"{media_type}_{timestamp}{ext_map.get(media_type, '')}"
            
            # 确保文件名唯一
            counter = 1
            original_filename = filename
            while (save_dir / filename).exists():
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                counter += 1
            
            # 下载文件
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.talkenglish.com/'
            }
            
            response = requests.get(url, stream=True, headers=headers, timeout=60)
            response.raise_for_status()
            
            file_path = save_dir / filename
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return {
                'filename': filename,
                'local_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'url': url
            }
            
        except Exception as e:
            print(f"❌ 下载{media_type}文件失败 {url}: {e}")
            return None
    
    def monitor_crawl(self, crawl_id, check_interval=90):
        """监控爬取进度"""
        print(f"📊 开始监控爬取进度 (每{check_interval}秒检查一次)...")
        print("⚠️  全媒体爬取可能需要较长时间，请耐心等待...")
        
        start_time = datetime.now()
        last_page_count = 0
        
        while True:
            status = self.check_status(crawl_id)
            if not status:
                break
            
            current_time = datetime.now().strftime("%H:%M:%S")
            elapsed = datetime.now() - start_time
            
            if status.get('status') == 'completed':
                print(f"🎉 [{current_time}] 爬取完成! 总耗时: {elapsed}")
                print(f"📄 总页面数: {len(status.get('data', []))}")
                
                # 保存完整结果并提取媒体
                self.save_results_and_extract_media(crawl_id, status)
                break
            
            elif status.get('status') == 'scraping':
                completed = len(status.get('data', []))
                new_pages = completed - last_page_count
                last_page_count = completed
                
                # 实时提取媒体URL统计
                if new_pages > 0:
                    recent_pages = status.get('data', [])[-new_pages:] if new_pages > 0 else []
                    self.update_media_stats(recent_pages)
                
                print(f"⏳ [{current_time}] 爬取中... 已完成: {completed} 页面 (+{new_pages}) | "
                      f"音频: {self.media_stats['audio']['found']} | "
                      f"视频: {self.media_stats['video']['found']} | "
                      f"图片: {self.media_stats['images']['found']} | "
                      f"耗时: {elapsed}")
            
            elif status.get('status') == 'failed':
                print(f"❌ [{current_time}] 爬取失败 (耗时: {elapsed})")
                print(f"错误信息: {status.get('error', 'Unknown error')}")
                break
            
            time.sleep(check_interval)
    
    def update_media_stats(self, pages):
        """更新媒体统计"""
        for page in pages:
            content = page.get('markdown', '') + page.get('html', '')
            media_urls = self.extract_media_urls(content)
            
            for media_type, urls in media_urls.items():
                self.media_stats[media_type]['found'] += len(urls)
    
    def save_results_and_extract_media(self, crawl_id, status):
        """保存结果并提取所有媒体文件"""
        print("\n" + "="*60)
        print("🎯 开始保存结果和提取媒体文件...")
        print("="*60)
        
        # 保存完整JSON结果
        complete_file = self.raw_data_dir / "complete_crawl_result.json"
        with open(complete_file, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        print(f"💾 完整爬取结果已保存: {complete_file}")
        
        # 提取并保存页面内容
        if 'data' in status:
            pages = status['data']
            print(f"📄 开始处理 {len(pages)} 个页面...")
            
            # 分类保存内容
            self.extract_and_categorize_content(pages)
            
            # 提取并下载所有媒体文件
            self.extract_and_download_all_media(pages)
            
            # 生成最终报告
            self.generate_final_report(pages)
    
    def extract_and_categorize_content(self, pages):
        """提取和分类页面内容"""
        print("📚 开始分类保存页面内容...")
        
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
            'practice': [],
            'other': []
        }
        
        for i, page in enumerate(pages, 1):
            if i % 100 == 0:
                print(f"  处理进度: {i}/{len(pages)} 页面")
            
            url = page.get('metadata', {}).get('url', '')
            title = page.get('metadata', {}).get('title', 'Untitled')
            content = page.get('markdown', '')
            html_content = page.get('html', '')
            
            # 分类页面
            category = 'other'
            for cat in categories.keys():
                if f"/{cat}/" in url.lower() or cat in url.lower():
                    category = cat
                    break
            
            # 提取媒体URL
            media_urls = self.extract_media_urls(content + html_content)
            
            page_info = {
                'url': url,
                'title': title,
                'markdown': content,
                'html': html_content,
                'word_count': len(content.split()) if content else 0,
                'char_count': len(content) if content else 0,
                'media_urls': media_urls,
                'media_count': {
                    'audio': len(media_urls['audio']),
                    'video': len(media_urls['video']),
                    'images': len(media_urls['images'])
                }
            }
            
            categories[category].append(page_info)
        
        # 保存分类结果
        for category, pages_list in categories.items():
            if pages_list:
                category_file = self.content_dir / category / f"{category}_content.json"
                with open(category_file, "w", encoding="utf-8") as f:
                    json.dump(pages_list, f, indent=2, ensure_ascii=False)
                
                total_media = sum(page['media_count']['audio'] + page['media_count']['video'] + page['media_count']['images'] 
                                for page in pages_list)
                print(f"  📂 {category.title()}: {len(pages_list)} 页面, {total_media} 个媒体文件")
        
        print("✅ 内容分类完成")
    
    def extract_and_download_all_media(self, pages):
        """提取并下载所有媒体文件"""
        print("\n🎵 开始提取和下载媒体文件...")
        
        all_media = {
            'audio': set(),
            'video': set(),
            'images': set()
        }
        
        media_info = {
            'audio': [],
            'video': [],
            'images': []
        }
        
        # 收集所有媒体URL
        for i, page in enumerate(pages, 1):
            if i % 100 == 0:
                print(f"  扫描进度: {i}/{len(pages)} 页面")
            
            url = page.get('metadata', {}).get('url', '')
            title = page.get('metadata', {}).get('title', 'Untitled')
            content = page.get('markdown', '') + page.get('html', '')
            
            media_urls = self.extract_media_urls(content)
            
            for media_type, urls in media_urls.items():
                for media_url in urls:
                    if media_url not in all_media[media_type]:
                        all_media[media_type].add(media_url)
                        media_info[media_type].append({
                            'url': media_url,
                            'source_page': url,
                            'source_title': title
                        })
        
        print(f"\n📊 媒体文件统计:")
        print(f"  🎵 音频文件: {len(all_media['audio'])} 个")
        print(f"  🎬 视频文件: {len(all_media['video'])} 个")
        print(f"  🖼️  图片文件: {len(all_media['images'])} 个")
        print(f"  📁 总计: {sum(len(urls) for urls in all_media.values())} 个媒体文件")
        
        # 下载所有媒体文件
        downloaded_media = {
            'audio': [],
            'video': [],
            'images': []
        }
        
        for media_type, media_list in media_info.items():
            if not media_list:
                continue
                
            print(f"\n⬇️  开始下载 {media_type} 文件 ({len(media_list)} 个)...")
            
            for i, info in enumerate(media_list, 1):
                media_url = info['url']
                
                print(f"  [{i}/{len(media_list)}] 下载 {media_type}: {os.path.basename(media_url)}")
                
                result = self.download_media_file(media_url, media_type)
                if result:
                    result.update({
                        'source_page': info['source_page'],
                        'source_title': info['source_title']
                    })
                    downloaded_media[media_type].append(result)
                    self.media_stats[media_type]['downloaded'] += 1
                    print(f"    ✅ 成功: {result['filename']} ({result['file_size']} bytes)")
                else:
                    self.media_stats[media_type]['failed'] += 1
                    print(f"    ❌ 失败: {media_url}")
                
                # 避免请求过于频繁
                time.sleep(0.5)
        
        # 保存媒体下载报告
        media_report = {
            'timestamp': self.timestamp,
            'total_found': {k: len(v) for k, v in all_media.items()},
            'download_stats': self.media_stats,
            'downloaded_files': downloaded_media
        }
        
        media_report_file = self.reports_dir / "media_download_report.json"
        with open(media_report_file, "w", encoding="utf-8") as f:
            json.dump(media_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 媒体下载完成!")
        for media_type, stats in self.media_stats.items():
            print(f"  {media_type.title()}: {stats['downloaded']}/{stats['found']} 成功, {stats['failed']} 失败")
    
    def generate_final_report(self, pages):
        """生成最终报告"""
        print("\n📊 生成最终报告...")
        
        # 统计信息
        total_pages = len(pages)
        total_words = sum(len(page.get('markdown', '').split()) for page in pages)
        total_chars = sum(len(page.get('markdown', '')) for page in pages)
        
        # 按域名统计
        domain_stats = {}
        for page in pages:
            url = page.get('metadata', {}).get('url', '')
            domain = urlparse(url).netloc
            if domain not in domain_stats:
                domain_stats[domain] = 0
            domain_stats[domain] += 1
        
        # 生成报告
        final_report = {
            'session_info': {
                'timestamp': self.timestamp,
                'session_directory': str(self.session_dir.absolute()),
                'config_file': self.config_file,
                'crawl_duration': str(datetime.now() - datetime.strptime(self.timestamp, "%Y%m%d_%H%M%S"))
            },
            'content_stats': {
                'total_pages': total_pages,
                'total_words': total_words,
                'total_characters': total_chars,
                'avg_words_per_page': total_words // total_pages if total_pages > 0 else 0,
                'domain_distribution': domain_stats
            },
            'media_stats': {
                'found': {k: v['found'] for k, v in self.media_stats.items()},
                'downloaded': {k: v['downloaded'] for k, v in self.media_stats.items()},
                'failed': {k: v['failed'] for k, v in self.media_stats.items()},
                'success_rate': {
                    k: round(v['downloaded'] / v['found'] * 100, 2) if v['found'] > 0 else 0 
                    for k, v in self.media_stats.items()
                }
            },
            'directory_structure': {
                'audio_files': len(list(self.audio_dir.glob('*'))),
                'video_files': len(list(self.video_dir.glob('*'))),
                'image_files': len(list(self.images_dir.glob('*'))),
                'content_categories': len(list(self.content_dir.glob('*')))
            }
        }
        
        # 保存最终报告
        final_report_file = self.reports_dir / "final_report.json"
        with open(final_report_file, "w", encoding="utf-8") as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        # 生成可读性报告
        readable_report = self.reports_dir / "summary_report.txt"
        with open(readable_report, "w", encoding="utf-8") as f:
            f.write(f"TalkEnglish.com 全媒体爬取报告\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"会话信息:\n")
            f.write(f"  时间戳: {self.timestamp}\n")
            f.write(f"  目录: {self.session_dir.absolute()}\n\n")
            f.write(f"内容统计:\n")
            f.write(f"  总页面数: {total_pages:,}\n")
            f.write(f"  总词数: {total_words:,}\n")
            f.write(f"  总字符数: {total_chars:,}\n")
            f.write(f"  平均每页词数: {total_words // total_pages if total_pages > 0 else 0}\n\n")
            f.write(f"媒体文件统计:\n")
            for media_type, stats in self.media_stats.items():
                f.write(f"  {media_type.title()}:\n")
                f.write(f"    发现: {stats['found']} 个\n")
                f.write(f"    下载成功: {stats['downloaded']} 个\n")
                f.write(f"    下载失败: {stats['failed']} 个\n")
                f.write(f"    成功率: {stats['downloaded'] / stats['found'] * 100 if stats['found'] > 0 else 0:.1f}%\n\n")
            f.write(f"目录结构:\n")
            f.write(f"  音频文件: {len(list(self.audio_dir.glob('*')))} 个\n")
            f.write(f"  视频文件: {len(list(self.video_dir.glob('*')))} 个\n")
            f.write(f"  图片文件: {len(list(self.images_dir.glob('*')))} 个\n")
            f.write(f"  内容分类: {len(list(self.content_dir.glob('*')))} 个\n")
        
        print(f"📋 最终报告已生成:")
        print(f"  - JSON报告: {final_report_file}")
        print(f"  - 文本摘要: {readable_report}")
        print(f"\n🎉 全媒体爬取完成!")
        print(f"📁 所有结果保存在: {self.session_dir.absolute()}")

def main():
    print("🌐 TalkEnglish.com 全媒体爬取器")
    print("=" * 60)
    print("🎯 功能: 爬取网站所有内容，包括音频、视频、图片")
    print("📁 结果: 按日期组织到 results/talkenglish_YYYYMMDD_HHMMSS/ 目录")
    print("=" * 60)
    
    crawler = TalkEnglishFullCrawler()
    
    print(f"\n📅 当前会话: {crawler.timestamp}")
    print(f"📁 结果目录: {crawler.session_dir.absolute()}")
    
    # 启动爬取
    crawl_id = crawler.start_crawl()
    if crawl_id:
        # 监控进度
        crawler.monitor_crawl(crawl_id, check_interval=90)
    
    print(f"\n📂 目录结构:")
    print(f"  {crawler.session_dir.name}/")
    print(f"  ├── audio/           # 音频文件 (MP3, WAV等)")
    print(f"  ├── video/           # 视频文件 (MP4, WebM等)")
    print(f"  ├── images/          # 图片文件 (JPG, PNG等)")
    print(f"  ├── content/         # 按类别分类的内容")
    print(f"  ├── reports/         # 爬取报告和统计")
    print(f"  └── raw_data/        # 原始爬取数据")

if __name__ == "__main__":
    main()