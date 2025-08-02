# Minecraft Wiki MCP Server

## 项目简介

一个基于 **MCP** 的 **Minecraft Wiki** 后端服务器，提供了对 Minecraft Wiki 内容的便捷访问。项目支持两种通信方式：**SSE (Server-Sent Events)** 和 **stdio (标准输入输出)**，可以满足不同场景的使用需求。

注意：本项目仅提供了一个简单的 mcp-server 实现，需要mc wiki api才能正常使用，请前往[此项目](https://github.com/rice-awa/minecraft-wiki-fetch-api)获取。
### 功能特性

- 🔍 **Wiki 内容搜索**: 支持关键词搜索 Minecraft Wiki 页面
- 📄 **页面内容获取**: 获取完整的页面内容，支持 HTML 和 Markdown 格式
- 📚 **批量页面获取**: 高效地批量获取多个页面内容
- ✅ **页面存在性检查**: 快速检查页面是否存在
- 🏥 **健康状态监控**: 监控后端 Wiki API 服务状态
- 🌐 **多种传输方式**: 支持 SSE 和 stdio 两种通信协议

## 项目结构

```
mc-wiki-mcp/
├── mcp_server_sse.py          # SSE 版本服务器
├── mcp_server_stdio.py        # stdio 版本服务器
├── config.json               # 配置文件
├── requirements.txt          # Python 依赖
├── docs/                     # 文档目录
│   ├── API_DOCUMENTATION.md
│   ├── USAGE_GUIDE.md
│   └── PROJECT_COMPLETION_SUMMARY.md
└── README.md                 # 本文件
```

## 安装配置

### 环境要求

- Python 3.8+
- pip 或 pipenv
- 运行中的 Wiki API 后端服务

### 依赖安装

```bash
# 克隆项目
git clone <repository-url>
cd mc-wiki-mcp

# 安装依赖
pip install -r requirements.txt
```

### 配置文件

编辑 `config.json` 文件：
> 注意：请在配置文件把 `wiki_api.base_url` 改成真实的 wiki API 后端服务地址。

```json
{
  "wiki_api": {
    "base_url": "http://localhost:3000",
    "timeout": 30,
    "max_retries": 3,
    "default_format": "both",
    "default_limit": 10,
    "max_batch_size": 20,
    "max_concurrency": 5
  },
  "mcp_server": {
    "name": "Minecraft Wiki MCP",
    "description": "MCP服务器，提供Minecraft Wiki内容访问工具",
    "version": "1.0.0",
    "host": "0.0.0.0",
    "port": 8000,
    "transport": "sse"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

## 使用方式

本项目提供两种通信方式，适用于不同的使用场景：

### 🌐 方式一：SSE (Server-Sent Events) 版本

**适用场景**: Web 应用、远程客户端、HTTP API 集成

#### 启动服务器

```bash
python mcp_server_sse.py
```

服务器将在 `http://localhost:8000` 启动，支持 SSE 连接。

#### 客户端配置示例

**HTTP 客户端连接:**
```python
import asyncio
from mcp.client.sse import sse_client

async def connect_to_sse_server():
    async with sse_client("http://localhost:8000/sse") as (read, write):
        # 使用 MCP 客户端进行交互
        pass
```

**在 Web 应用中使用:**
```javascript
const eventSource = new EventSource('http://localhost:8000/sse');
eventSource.onmessage = function(event) {
    // 处理 MCP 消息
    console.log(JSON.parse(event.data));
};
```

#### SSE 版本特点

- ✅ 支持远程访问
- ✅ 适合 Web 应用集成
- ✅ 支持多个并发客户端
- ✅ 可通过 HTTP 代理访问
- ❌ 需要网络端口
- ❌ 需要额外的网络配置

---

### 💻 方式二：stdio (标准输入输出) 版本

**适用场景**: Claude Desktop、本地 MCP 客户端(如cherry stdio)、桌面应用集成

#### 与 Claude Desktop 集成

1. **找到配置文件位置:**
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

2. **编辑配置文件:**
   ```json
   {
     "mcpServers": {
       "minecraft-wiki": {
         "command": "python",
         "args": ["you-path\\mc-wiki-mcp\\mcp_server_stdio.py"],
         "env": {}
       }
     }
   }
   ```

   > **重要提示**: 
   > - 请将路径 `you-path\\mc-wiki-mcp\\mcp_server_stdio.py` 替换为您的实际文件路径
   > - Windows 系统请使用双反斜杠 `\\` 或正斜杠 `/`
   > - macOS/Linux 系统使用正斜杠 `/`

3. **重启 Claude Desktop**

#### 直接运行 (测试用)

```bash
python mcp_server_stdio.py
```

#### 其他 MCP 客户端配置

**Python MCP 客户端:**
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def connect_to_stdio_server():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_stdio.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 使用 session 进行交互
```

#### stdio 版本特点

- ✅ 无需网络端口
- ✅ 安全的本地通信
- ✅ 与 Claude Desktop 完美集成
- ✅ 进程级别的隔离
- ❌ 仅支持本地客户端
- ❌ 一对一通信

---

## 🛠️ 可用工具

无论使用哪种通信方式，都提供以下工具：

| 工具名称 | 功能描述 | 主要参数 |
|---------|----------|----------|
| `search_wiki` | 搜索 Wiki 内容 | `query`, `limit`, `namespaces` |
| `get_wiki_page` | 获取页面内容 | `page_name`, `format`, `use_cache` |
| `get_wiki_pages_batch` | 批量获取页面 | `pages`, `format`, `concurrency` |
| `check_page_exists` | 检查页面存在 | `page_name` |
| `check_wiki_api_health` | 健康检查 | 无参数 |

### 使用示例

#### 在 Claude Desktop 中使用

配置完成后，您可以在 Claude Desktop 中直接询问：

```
请帮我搜索关于红石的信息
获取钻石页面的详细内容
检查"红石电路"页面是否存在
批量获取"钻石"、"红石"、"附魔"三个页面的内容
```

#### 通过 API 使用 (SSE 版本)

```bash
# 搜索内容
curl -X POST http://localhost:8000/tool/search_wiki \
  -H "Content-Type: application/json" \
  -d '{"query": "红石", "limit": 5}'

# 获取页面
curl -X POST http://localhost:8000/tool/get_wiki_page \
  -H "Content-Type: application/json" \
  -d '{"page_name": "钻石", "format": "markdown"}'
```

## 🔧 高级配置

### 自定义配置参数

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `wiki_api.base_url` | Wiki API 地址 | `http://localhost:3000` | 任何有效 URL |
| `wiki_api.timeout` | 请求超时时间 | `30` | 秒数 |
| `wiki_api.max_retries` | 最大重试次数 | `3` | 正整数 |
| `wiki_api.default_format` | 默认输出格式 | `both` | `html`, `markdown`, `both` |
| `mcp_server.host` | 服务器主机 (仅 SSE) | `0.0.0.0` | IP 地址 |
| `mcp_server.port` | 服务器端口 (仅 SSE) | `8000` | 端口号 |

### 日志配置

```json
{
  "logging": {
    "level": "DEBUG",  // DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

## 🐛 故障排除

### 常见问题

#### 1. SSE 版本连接问题

**问题**: 无法连接到 SSE 服务器
```bash
# 检查服务器是否运行
curl http://localhost:8000/health

# 检查端口是否被占用
netstat -an | grep 8000  # Linux/macOS
netstat -an | findstr 8000  # Windows
```

**解决方案**:
- 确认服务器已启动
- 检查防火墙设置
- 尝试更换端口

#### 2. stdio 版本在 Claude Desktop 中不显示

**问题**: 配置后在 Claude Desktop 中看不到 MCP 工具

**解决方案**:
1. 检查 `claude_desktop_config.json` 语法是否正确
2. 确认文件路径是绝对路径
3. 检查 Python 环境和依赖
4. 查看 Claude Desktop 日志

**Claude Desktop 日志位置**:
- **Windows**: `%APPDATA%\Claude\logs\`
- **macOS**: `~/Library/Logs/Claude/`
- **Linux**: `~/.local/share/Claude/logs/`

#### 3. Wiki API 连接失败

**问题**: 工具调用返回连接错误

**解决方案**:
1. 确认后端 Wiki API 服务正在运行
2. 检查 `config.json` 中的 API 地址
3. 测试网络连接
4. 查看服务器日志

### 调试技巧

#### SSE 版本调试
```bash
# 启动服务器并查看详细日志
python mcp_server_sse.py

# 在另一个终端测试连接
curl -v http://localhost:8000/sse
```

#### stdio 版本调试
```bash
# 重定向错误输出到文件
python mcp_server_stdio.py 2>debug.log

# 查看日志
tail -f debug.log
```

## 📖 相关文档

- [API 文档](docs/API_DOCUMENTATION.md) - 详细的 API 接口说明
- [使用指南](docs/USAGE_GUIDE.md) - 深入的使用教程
- [项目完成总结](docs/PROJECT_COMPLETION_SUMMARY.md) - 项目开发总结

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进项目！

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](./LICENSE) 文件。

## 🆘 获取帮助

如果您遇到问题或需要帮助：

1. 查看本 README 的故障排除部分
2. 检查 [docs/](docs/) 目录中的详细文档
3. 提交 Issue 描述您的问题
4. 查看日志文件获取详细错误信息

---

**快速开始提示**: 
- 🌐 想要远程访问或集成到 Web 应用？选择 **SSE 版本**
- 💻 想要在 Claude Desktop 中使用？选择 **stdio 版本**