import argparse
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random
import sys
from typing import List, Dict
import json
from datetime import datetime
import os
import time
from colorama import init, Fore, Style
from tqdm import tqdm

# 初始化colorama
init()

# ASCII艺术字
BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║                                                                  ║
║  {Fore.YELLOW}██╗    ██╗███████╗██████╗     ██████╗  █████╗ ███╗   ██╗{Fore.CYAN}  ║
║  {Fore.YELLOW}██║    ██║██╔════╝██╔══██╗   ██╔════╝ ██╔══██╗████╗  ██║{Fore.CYAN}  ║
║  {Fore.YELLOW}██║ █╗ ██║█████╗  ██████╔╝   ██║  ███╗███████║██╔██╗ ██║{Fore.CYAN}  ║
║  {Fore.YELLOW}██║███╗██║██╔══╝  ██╔══██╗   ██║   ██║██╔══██║██║╚██╗██║{Fore.CYAN}  ║
║  {Fore.YELLOW}╚███╔███╔╝███████╗██║  ██║   ╚██████╔╝██║  ██║██║ ╚████║{Fore.CYAN}  ║
║  {Fore.YELLOW} ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝{Fore.CYAN}  ║
║                                                                  ║
║  {Fore.GREEN}Web Directory Scanner v1.0{Fore.CYAN}                                  ║
║  {Fore.MAGENTA}Author: dazhi{Fore.CYAN}                                        ║
║  {Fore.MAGENTA}GitHub: https://github.com/sunhuiHi666/dirscan{Fore.CYAN}          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

def print_banner():
    """打印启动画面"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(f"{Fore.CYAN}[*] 正在初始化扫描器...{Style.RESET_ALL}")
    time.sleep(1)
    print(f"{Fore.GREEN}[+] 加载代理池...{Style.RESET_ALL}")
    time.sleep(0.5)
    print(f"{Fore.YELLOW}[!] 准备就绪！{Style.RESET_ALL}\n")

class ProxyPool:
    def __init__(self):
        self.proxies = []
        self.failed_proxies = set()  # 记录失败的代理
        self.max_retries = 3  # 最大重试次数
        self.load_proxies()
    
    def load_proxies(self):
        """加载代理列表"""
        try:
            with open('proxies.json', 'r') as f:
                self.proxies = json.load(f)
                print(f"{Fore.GREEN}[+] 成功加载 {len(self.proxies)} 个代理{Style.RESET_ALL}")
        except FileNotFoundError:
            self.proxies = []
            print(f"{Fore.YELLOW}[!] 未找到代理配置文件{Style.RESET_ALL}")
        except json.JSONDecodeError:
            print(f"{Fore.RED}[!] 代理配置文件格式错误{Style.RESET_ALL}")
            self.proxies = []
    
    def save_proxies(self):
        """保存代理列表"""
        try:
            with open('proxies.json', 'w') as f:
                json.dump(self.proxies, f, indent=2)
        except Exception as e:
            print(f"{Fore.RED}[!] 保存代理配置失败: {str(e)}{Style.RESET_ALL}")
    
    def add_proxy(self, proxy: Dict):
        """添加新代理"""
        if not self._validate_proxy_format(proxy):
            print(f"{Fore.RED}[!] 代理格式无效: {proxy}{Style.RESET_ALL}")
            return False
            
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.save_proxies()
            print(f"{Fore.GREEN}[+] 成功添加代理: {proxy['protocol']}://{proxy['ip']}:{proxy['port']}{Style.RESET_ALL}")
            return True
        return False
    
    def _validate_proxy_format(self, proxy: Dict) -> bool:
        """验证代理格式"""
        required_fields = ['protocol', 'ip', 'port']
        return all(field in proxy for field in required_fields)
    
    def get_random_proxy(self) -> Dict:
        """获取随机代理"""
        if not self.proxies:
            return None
            
        # 过滤掉失败的代理
        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        if not available_proxies:
            # 如果所有代理都失败，重置失败记录
            self.failed_proxies.clear()
            available_proxies = self.proxies
            
        return random.choice(available_proxies)
    
    def remove_proxy(self, proxy: Dict):
        """移除代理"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.save_proxies()
            print(f"{Fore.YELLOW}[!] 已移除无效代理: {proxy['protocol']}://{proxy['ip']}:{proxy['port']}{Style.RESET_ALL}")
    
    def mark_proxy_failed(self, proxy: Dict):
        """标记代理失败"""
        if proxy:
            self.failed_proxies.add(proxy)
            if len(self.failed_proxies) >= len(self.proxies) * 0.8:  # 如果80%的代理都失败
                print(f"{Fore.YELLOW}[!] 警告: 大量代理失效，正在重置代理池...{Style.RESET_ALL}")
                self.failed_proxies.clear()

class DirectoryScanner:
    def __init__(self, proxy_pool: ProxyPool, verbose: bool = False):
        self.proxy_pool = proxy_pool
        self.verbose = verbose
        self.results = []
        self.visited = set()
        self.total_paths = 0
        self.scanned_paths = 0
        self.failed_paths = 0
        self.success_paths = 0
        self.start_time = None
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=5, connect=3)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.lock = asyncio.Lock()  # 添加锁来保护计数器
    
    async def init_session(self):
        """初始化aiohttp会话"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.headers
            )
    
    async def close_session(self):
        """关闭aiohttp会话"""
        if self.session:
            await self.session.close()
            self.session = None

    async def show_progress(self):
        """显示实时进度"""
        while self.scanned_paths < self.total_paths:
            elapsed_time = time.time() - self.start_time
            speed = self.scanned_paths / elapsed_time if elapsed_time > 0 else 0
            percent = (self.scanned_paths / self.total_paths) * 100 if self.total_paths > 0 else 0
            
            status = f'\r{Fore.CYAN}[*] 进度: {percent:.1f}% ({self.scanned_paths}/{self.total_paths})'
            status += f' | 速度: {speed:.1f} 请求/秒'
            status += f' | 成功: {self.success_paths} | 失败: {self.failed_paths}'
            status += f' | 耗时: {elapsed_time:.1f}秒{Style.RESET_ALL}'
            
            sys.stdout.write(status)
            sys.stdout.flush()
            await asyncio.sleep(0.2)
        
        # 显示最终进度
        elapsed_time = time.time() - self.start_time
        speed = self.scanned_paths / elapsed_time if elapsed_time > 0 else 0
        sys.stdout.write(f'\r{Fore.CYAN}[*] 扫描完成! 总计: {self.total_paths} | 成功: {self.success_paths} | 失败: {self.failed_paths} | 速度: {speed:.1f} 请求/秒 | 耗时: {elapsed_time:.1f}秒{Style.RESET_ALL}\n')
        sys.stdout.flush()

    def print_progress(self, url: str, status: int = None, error: str = None):
        """打印单个URL的扫描进度"""
        if status:
            if status == 200:
                status_color = Fore.GREEN
                status_text = "成功"
            elif status == 404:
                status_color = Fore.RED
                status_text = "未找到"
            elif status >= 500:
                status_color = Fore.YELLOW
                status_text = "服务器错误"
            else:
                status_color = Fore.WHITE
                status_text = "其他"
            print(f"{Fore.CYAN}[+] 扫描: {url}")
            print(f"{status_color}    └─ 状态: {status} ({status_text}){Style.RESET_ALL}")
        elif error:
            print(f"{Fore.RED}[!] 扫描: {url}")
            print(f"    └─ 错误: {error}{Style.RESET_ALL}")
        if status == 200:
            print(f"{Fore.GREEN}    └─ 发现有效路径！{Style.RESET_ALL}")

    async def update_counters(self, success: bool = False):
        """更新计数器"""
        async with self.lock:
            self.scanned_paths += 1
            if success:
                self.success_paths += 1
            else:
                self.failed_paths += 1
            # 确保不会超过总数
            if self.scanned_paths > self.total_paths:
                self.scanned_paths = self.total_paths

    async def check_url(self, url: str):
        """检查单个URL"""
        try:
            await self.init_session()
            async with self.session.get(
                url, 
                ssl=False,
                allow_redirects=True,
                timeout=self.timeout
            ) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                title = soup.title.string if soup.title else 'No Title'
                
                result = {
                    'url': url,
                    'status': response.status,
                    'title': title,
                    'size': len(content),
                    'headers': dict(response.headers)
                }
                
                if response.status == 200:
                    self.results.append(result)
                    await self.update_counters(success=True)
                else:
                    await self.update_counters(success=False)
                
                self.print_progress(url, response.status)
                
        except Exception as e:
            await self.update_counters(success=False)
            self.print_progress(url, error=str(e))

    async def scan(self, base_url: str, wordlist: str) -> List[Dict]:
        """开始扫描"""
        self.results = []
        self.visited = set()
        self.scanned_paths = 0
        self.failed_paths = 0
        self.success_paths = 0
        self.start_time = time.time()
        
        try:
            with open(wordlist, 'r', encoding='utf-8') as f:
                paths = [line.strip() for line in f if line.strip()]
        except UnicodeDecodeError:
            try:
                with open(wordlist, 'r', encoding='gbk') as f:
                    paths = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"{Fore.RED}[!] 无法读取字典文件 {wordlist}: {str(e)}{Style.RESET_ALL}")
                return []
        except Exception as e:
            print(f"{Fore.RED}[!] 读取字典文件时发生错误: {str(e)}{Style.RESET_ALL}")
            return []
        
        # 移除不再使用的路径数量打印
        print(f"{Fore.GREEN}[+] 开始扫描 {base_url}{Style.RESET_ALL}")
        
        # 创建信号量来限制并发数
        semaphore = asyncio.Semaphore(20)
        
        async def bounded_check_url(url: str):
            try:
                async with semaphore:
                    await self.check_url(url)
            except Exception as e:
                print(f"\n{Fore.RED}[!] 扫描URL时发生错误: {url} - {str(e)}{Style.RESET_ALL}")
        
        # 移除进度任务创建
        # progress_task = asyncio.create_task(self.show_progress())
        
        try:
            batch_size = 50
            for i in range(0, len(paths), batch_size):
                batch_paths = paths[i:i + batch_size]
                tasks = []
                for path in batch_paths:
                    url = urljoin(base_url, path)
                    if url not in self.visited:
                        self.visited.add(url)
                        tasks.append(bounded_check_url(url))
                
                if tasks:
                    await asyncio.gather(*tasks)
                    await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"\n{Fore.RED}[!] 扫描过程中发生错误: {str(e)}{Style.RESET_ALL}")
        finally:
            try:
                await self.close_session()
                # 移除所有与进度任务相关的代码
            except Exception as e:
                print(f"\n{Fore.RED}[!] 关闭会话时发生错误: {str(e)}{Style.RESET_ALL}")
        
        return self.results

def generate_html(results: List[Dict], base_url: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>目录扫描结果 - {base_url}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .result-item {{
            border: 1px solid #ddd;
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 4px;
            background-color: white;
        }}
        .result-item:hover {{
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .url {{
            color: #007bff;
            text-decoration: none;
            font-weight: bold;
        }}
        .url:hover {{
            text-decoration: underline;
        }}
        .status-200 {{
            color: #28a745;
        }}
        .status-other {{
            color: #dc3545;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .timestamp {{
            color: #999;
            font-size: 0.8em;
            text-align: right;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>目录扫描结果</h1>
        <div class="summary">
            <p><strong>目标URL:</strong> {base_url}</p>
            <p><strong>扫描时间:</strong> {timestamp}</p>
            <p><strong>发现路径数:</strong> {len(results)}</p>
        </div>
        <div class="results">
"""
    
    for result in results:
        status_class = "status-200" if result['status'] == 200 else "status-other"
        html += f"""
            <div class="result-item">
                <a href="{result['url']}" class="url" target="_blank">{result['url']}</a>
                <div class="meta">
                    <span class="{status_class}">状态码: {result['status']}</span>
                    <br>
                    标题: {result['title']}
                    <br>
                    大小: {result['size']} 字节
                </div>
            </div>
"""
    
    html += """
        </div>
        <div class="timestamp">
            扫描完成时间: """ + timestamp + """
        </div>
    </div>
</body>
</html>
"""
    return html

def save_results(results: List[Dict], output_file: str, base_url: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not output_file:
        output_file = f"scan_results_{timestamp}.html"
    
    html_content = generate_html(results, base_url)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\n结果已保存到: {output_file}")

async def main():
    parser = argparse.ArgumentParser(description='Web目录扫描工具')
    parser.add_argument('url', help='目标URL')
    parser.add_argument('-w', '--wordlist', default='common.txt', help='字典文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细进度')
    parser.add_argument('-p', '--proxy', help='添加代理（格式：protocol://ip:port）')
    args = parser.parse_args()

    # 打印启动画面
    print_banner()

    # 设置输出文件
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'scan_results_{timestamp}.html'

    # 初始化代理池
    proxy_pool = ProxyPool()
    if args.proxy:
        try:
            protocol, rest = args.proxy.split('://')
            ip, port = rest.split(':')
            proxy = {
                'protocol': protocol,
                'ip': ip,
                'port': port
            }
            proxy_pool.add_proxy(proxy)
            print(f"已添加代理: {args.proxy}")
        except Exception as e:
            print(f"代理格式错误: {e}")
            return

    # 创建扫描器
    scanner = DirectoryScanner(proxy_pool, args.verbose)
    
    # 开始扫描
    results = await scanner.scan(args.url, args.wordlist)
    
    # 保存结果
    if results:
        save_results(results, args.output, args.url)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] 扫描已停止{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] 发生错误: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)