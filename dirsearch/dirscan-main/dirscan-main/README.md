# dirscan# Web目录扫描工具

一个基于Python的Web目录扫描工具，支持代理池和异步并发扫描，可以快速发现网站中的敏感目录和文件。

## 功能特点

- 🚀 异步并发扫描，提高扫描效率
- 🔄 支持代理池功能，避免IP被封
- 📊 实时显示扫描进度
- 📝 支持自定义字典文件
- 🎨 美观的HTML格式报告
- 🔍 自动发现和扫描子目录
- 📈 显示详细的扫描统计信息
- 🎯 炫酷的启动画面和进度显示

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/dirscan.git
cd dirscan
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

### 依赖说明

- `aiohttp`: 异步HTTP客户端/服务器
- `beautifulsoup4`: HTML解析
- `colorama`: 终端彩色输出
- `tqdm`: 进度条显示
- `websockets`: WebSocket支持
- `flask`: Web界面
- `requests`: HTTP请求
- `argparse`: 命令行参数解析

## 使用方法

### 基本用法

```bash
python dirscan.py https://example.com
```

启动后会显示炫酷的启动画面，包括：

- ASCII艺术字标题
- 彩色边框装饰
- 初始化进度动画
- 实时状态提示

### 使用代理

```bash
python dirscan.py https://example.com -p http://127.0.0.1:8080
```

### 使用自定义字典

```bash
python dirscan.py https://example.com -w custom_wordlist.txt
```

### 显示详细进度

```bash
python dirscan.py https://example.com -v
```

### 指定输出文件

```bash
python dirscan.py https://example.com -o results.html
```

### 组合使用

```bash
python dirscan.py https://example.com -w custom_wordlist.txt -p http://127.0.0.1:8080 -v -o results.html
```

## 参数说明

- `url`: 目标URL（必需）
- `-w, --wordlist`: 字典文件路径（默认：common.txt）
- `-o, --output`: 输出文件路径（默认：scan_results_时间戳.html）
- `-v, --verbose`: 显示详细进度
- `-p, --proxy`: 添加代理（格式：protocol://ip:port）

## 字典文件格式

字典文件应为文本文件，每行一个路径，例如：

```
/admin
/login
/wp-admin
/backup
/config
```

## 输出结果

扫描结果将以HTML格式保存，包含以下信息：

- 目标URL
- 扫描时间
- 发现的路径数量
- 每个路径的详细信息：
  - URL（可点击）
  - 状态码
  - 页面标题
  - 响应大小
  - 使用的代理（如果有）

## 代理池功能

- 代理信息保存在 `proxies.json` 文件中
- 可以通过 `-p` 参数添加新代理
- 自动移除无效代理
- 支持HTTP和HTTPS代理

## 界面预览

### 启动画面

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  ██╗    ██╗███████╗██████╗     ██████╗  █████╗ ███╗   ██╗  ║
║  ██║    ██║██╔════╝██╔══██╗   ██╔════╝ ██╔══██╗████╗  ██║  ║
║  ██║ █╗ ██║█████╗  ██████╔╝   ██║  ███╗███████║██╔██╗ ██║  ║
║  ██║███╗██║██╔══╝  ██╔══██╗   ██║   ██║██╔══██║██║╚██╗██║  ║
║  ╚███╔███╔╝███████╗██║  ██║   ╚██████╔╝██║  ██║██║ ╚████║  ║
║   ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝  ║
║                                                          ║
║  Web Directory Scanner v1.0                              ║
║  Author: Your Name                                       ║
║  GitHub: https://github.com/yourusername/dirscan        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### 扫描进度

```
[*] 正在初始化扫描器...
[+] 加载代理池...
[+] 初始化WebSocket服务器...
[+] 启动Web界面...
[!] 准备就绪！

扫描进度: 45%|████████████████▌         | 450/1000 [00:30<00:37, 14.52it/s]
```

## 注意事项

1. 请仅在获得授权的目标上使用本工具
2. 建议使用代理池功能避免IP被封
3. 扫描大量目标时请注意控制并发数量
4. 建议定期更新字典文件以提高扫描效果
5. 确保终端支持ANSI颜色代码以显示彩色输出

## 常见问题

### Q: 为什么扫描速度很慢？

A: 可以尝试使用代理池功能，或者调整并发数量。

### Q: 如何添加更多代理？

A: 使用 `-p` 参数添加单个代理，或者直接编辑 `proxies.json` 文件。

### Q: 扫描结果在哪里？

A: 默认保存在当前目录下的 `scan_results_时间戳.html` 文件中。

### Q: 为什么看不到彩色输出？

A: 请确保您的终端支持ANSI颜色代码，Windows用户可能需要使用Windows Terminal或PowerShell。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 免责声明

本工具仅用于安全研究和授权的安全测试。使用本工具进行未授权的测试是违法的。作者不对使用本工具造成的任何损失负责。 
