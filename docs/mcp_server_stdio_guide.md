# MCP Server stdio 版本使用指南

## 概述

`mcp_server_stdio.py` 是基于标准输入输出(stdio)传输方式的 MCP 服务器实现，提供与现有 SSE 版本相同的功能，专门用于与 Claude Desktop 和其他支持 stdio 的 MCP 客户端集成。

## 主要特性

- **stdio 传输**: 使用标准输入输出与客户端通信，适合本地开发和桌面应用集成
- **完全兼容**: 提供与 SSE 版本相同的所有工具和资源
- **安全日志**: 所有日志输出到 stderr，避免干扰 stdio 通信
- **错误处理**: 完善的异常处理和重试机制

## 与 SSE 版本的主要区别

| 特性 | SSE 版本 | stdio 版本 |
|------|----------|------------|
| 传输方式 | HTTP Server-Sent Events | 标准输入输出 |
| 网络访问 | 需要网络端口 | 本地进程通信 |
| 客户端类型 | Web 客户端、HTTP 客户端 | Claude Desktop、本地 MCP 客户端 |
| 日志输出 | 可输出到 stdout | 必须输出到 stderr |
| 部署方式 | 独立 HTTP 服务 | 作为子进程启动 |

## 安装和运行

### 1. 直接运行 (测试用)

```bash
python mcp_server_stdio.py
```

### 2. 与 Claude Desktop 集成

编辑 Claude Desktop 的配置文件 `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "minecraft-wiki": {
      "command": "python",
      "args": ["E:\\Python_JavaScript\\mc-wiki-mcp\\mcp_server_stdio.py"],
      "env": {}
    }
  }
}
```

### 3. 配置文件位置

- Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/claude/claude_desktop_config.json`

## 可用工具

### 1. search_wiki
搜索 Minecraft Wiki 内容

**参数:**
- `query` (str): 搜索关键词
- `limit` (int, 可选): 结果数量限制
- `namespaces` (str, 可选): 命名空间过滤
- `format` (str, 可选): 响应格式

### 2. get_wiki_page
获取指定页面的完整内容

**参数:**
- `page_name` (str): 页面名称
- `format` (str, 可选): 输出格式 (html, markdown, both)
- `use_cache` (bool, 可选): 是否使用缓存
- `include_metadata` (bool, 可选): 是否包含元数据

### 3. get_wiki_pages_batch
批量获取多个页面内容

**参数:**
- `pages` (List[str]): 页面名称列表
- `format` (str, 可选): 输出格式
- `concurrency` (int, 可选): 并发请求数
- `use_cache` (bool, 可选): 是否使用缓存

### 4. check_page_exists
检查页面是否存在

**参数:**
- `page_name` (str): 页面名称

### 5. check_wiki_api_health
检查 Wiki API 服务健康状态

## 可用资源

### 1. minecraft://wiki/page/{page_name}
获取特定页面的资源表示

### 2. minecraft://wiki/search/{query}
获取搜索结果的资源表示

## stdio 特有的注意事项

### 1. 日志处理
stdio 版本的关键特点是所有日志都输出到 stderr，避免干扰与客户端的 stdio 通信:

```python
# 自定义 stderr 处理器
class StderrHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(sys.stderr)

# 配置日志输出到 stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[StderrHandler()]
)
```

### 2. 进程生命周期
- 服务器作为子进程由客户端启动
- 通过 stdin/stdout 进行 JSON-RPC 通信
- 当客户端断开连接时自动退出

### 3. 调试方法
由于 stdout 被用于 MCP 通信，调试时应该:
- 查看 stderr 输出获取日志信息
- 使用日志记录而不是 print() 语句
- 检查客户端日志了解连接状态

## 测试验证

### 1. 功能测试
启动服务器后，可以在 Claude Desktop 中测试以下查询:
- "搜索关于红石的信息"
- "获取钻石页面的内容"
- "检查'红石电路'页面是否存在"

### 2. 连接测试
在 Claude Desktop 中应该能看到:
- MCP 工具图标出现
- 可以列出所有可用工具
- 工具调用能正常执行

## 故障排除

### 1. 连接问题
- 确认 Python 路径正确
- 检查脚本路径是否为绝对路径
- 验证依赖是否已安装

### 2. Wiki API 问题
- 确认后端 Wiki API 服务正在运行
- 检查 `config.json` 中的 API 地址
- 测试网络连接

### 3. 日志分析
检查 stderr 输出了解详细错误信息:
```bash
python mcp_server_stdio.py 2>debug.log
```

## 开发建议

### 1. 本地开发
- 使用 stdio 版本进行本地测试
- 利用 Claude Desktop 快速验证功能
- 通过 stderr 日志调试问题

### 2. 生产部署
- 确保所有依赖正确安装
- 配置适当的日志级别
- 监控进程健康状态

### 3. 扩展功能
- 遵循现有工具的模式添加新功能
- 保持与 SSE 版本的功能一致性
- 注意 stdio 特有的约束条件

这个 stdio 版本为用户提供了一个更简单的方式来在本地环境中使用 Minecraft Wiki MCP 服务，特别适合与 Claude Desktop 等桌面应用的集成。