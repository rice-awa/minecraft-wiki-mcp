# Minecraft Wiki MCP 使用指南

## 📋 概述

Minecraft Wiki MCP 是一个Model Context Protocol (MCP) 服务器，为大语言模型提供访问 Minecraft Wiki 内容的工具。通过集成 Minecraft Wiki API，可以搜索、获取和处理 Minecraft 相关知识。

## 🚀 快速开始

### 1. 环境准备

确保你的环境满足以下要求：
- Python 3.8+
- Minecraft Wiki API 服务运行在 `localhost:3000`

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务器

```bash
python mcp_only_server.py
```

服务器将在 `localhost:8000` 启动，使用 SSE (Server-Sent Events) 传输协议。

## 🔧 配置

### 配置文件 (config.json)

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

### 配置说明

- `wiki_api.base_url`: Wiki API 服务器地址
- `wiki_api.timeout`: HTTP 请求超时时间（秒）
- `wiki_api.max_retries`: 最大重试次数
- `wiki_api.default_format`: 默认输出格式 (html/markdown/both)
- `wiki_api.default_limit`: 默认搜索结果数量
- `mcp_server.port`: MCP 服务器端口
- `mcp_server.transport`: 传输协议 (sse/stdio)

## 🛠️ 可用工具

### 1. search_wiki

搜索 Minecraft Wiki 内容

**参数:**
- `query` (必需): 搜索关键词
- `limit` (可选): 结果数量限制，默认10，最大50
- `namespaces` (可选): 命名空间过滤，多个用逗号分隔
- `format` (可选): 响应格式，默认json

**示例:**
```python
# 搜索钻石相关内容
result = await search_wiki("钻石", limit=5)

# 搜索红石相关内容，限制在主命名空间
result = await search_wiki("红石", namespaces="0", limit=10)
```

**返回格式:**
```json
{
  "success": true,
  "query": "钻石",
  "results": [
    {
      "title": "钻石",
      "url": "https://zh.minecraft.wiki/w/钻石",
      "snippet": "钻石是游戏中最珍贵的材料之一...",
      "namespace": "主要",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ],
  "pagination": {
    "limit": 5,
    "totalHits": 25,
    "hasMore": true
  },
  "metadata": {
    "searchTime": 1234,
    "fromCache": false,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 2. get_wiki_page

获取指定页面的完整内容

**参数:**
- `page_name` (必需): 页面名称
- `format` (可选): 输出格式 - html/markdown/both，默认both
- `use_cache` (可选): 是否使用缓存，默认True
- `include_metadata` (可选): 是否包含元数据，默认True

**示例:**
```python
# 获取钻石页面内容（Markdown格式）
result = await get_wiki_page("钻石", format="markdown")

# 获取页面内容，不使用缓存
result = await get_wiki_page("红石", use_cache=False)

# 获取页面内容，包含所有格式
result = await get_wiki_page("末影龙", format="both", include_metadata=True)
```

**返回格式:**
```json
{
  "success": true,
  "page_name": "钻石",
  "data": {
    "page": {
      "pageName": "钻石",
      "url": "https://zh.minecraft.wiki/w/钻石",
      "title": "钻石",
      "subtitle": "来自Minecraft Wiki",
      "categories": [...],
      "content": {
        "html": "...",
        "markdown": "# 钻石\n\n**钻石**是游戏中最珍贵的材料之一。\n\n## 获取\n...",
        "text": "钻石是游戏中最珍贵的材料之一...",
        "components": {
          "sections": [...],
          "images": [...],
          "tables": [...],
          "infoboxes": [...],
          "toc": {...}
        }
      },
      "meta": {
        "wordCount": 1234,
        "imageCount": 5,
        "tableCount": 2,
        "sectionCount": 8,
        "processingTime": 1678901234
      }
    }
  }
}
```

### 3. get_wiki_pages_batch

批量获取多个页面内容

**参数:**
- `pages` (必需): 页面名称列表
- `format` (可选): 输出格式，默认markdown
- `concurrency` (可选): 并发请求数，默认3，最大5
- `use_cache` (可选): 是否使用缓存，默认True

**示例:**
```python
# 批量获取多个页面
pages = ["钻石", "金锭", "铁锭", "红石"]
result = await get_wiki_pages_batch(pages, format="markdown", concurrency=3)
```

**返回格式:**
```json
{
  "success": true,
  "results": {
    "钻石": {
      "success": true,
      "data": {...}
    },
    "金锭": {
      "success": true,
      "data": {...}
    }
  },
  "summary": {
    "totalPages": 4,
    "successCount": 3,
    "errorCount": 1
  },
  "metadata": {
    "requestTime": 3000,
    "format": "markdown",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 4. check_page_exists

检查页面是否存在

**参数:**
- `page_name` (必需): 页面名称

**示例:**
```python
# 检查页面是否存在
result = await check_page_exists("钻石")
result = await check_page_exists("不存在的页面")
```

**返回格式:**
```json
{
  "success": true,
  "page_name": "钻石",
  "exists": true,
  "page_info": {
    "title": "钻石",
    "pageid": 12345
  },
  "redirected": false
}
```

### 5. check_wiki_api_health

检查 Wiki API 服务健康状态

**示例:**
```python
# 检查API健康状态
result = await check_wiki_api_health()
```

**返回格式:**
```json
{
  "success": true,
  "api_status": "healthy",
  "health_data": {
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "uptime": {
      "seconds": 3600,
      "human": "1小时"
    }
  }
}
```

## 🌐 MCP 资源

### 1. Wiki 页面资源

- **URI**: `minecraft://wiki/page/{page_name}`
- **描述**: 提供指定Wiki页面的完整内容
- **内容类型**: `application/json`

**示例:**
```
minecraft://wiki/page/钻石
minecraft://wiki/page/红石电路
```

### 2. Wiki 搜索资源

- **URI**: `minecraft://wiki/search/{query}`
- **描述**: 提供搜索结果
- **内容类型**: `application/json`

**示例:**
```
minecraft://wiki/search/钻石
minecraft://wiki/search/附魔
```

## 🚨 错误处理

所有工具都包含完整的错误处理机制：

### 常见错误类型

1. **网络连接错误**: Wiki API 服务不可用
2. **页面不存在**: 请求的页面不存在
3. **参数错误**: 传入的参数格式错误
4. **API限制**: 超过API的请求限制
5. **超时错误**: 请求超时

### 错误响应格式

```json
{
  "success": false,
  "error": "错误描述",
  "page_name": "页面名称", // 如果适用
  "query": "搜索关键词"     // 如果适用
}
```

## 📚 使用场景

### 1. 游戏助手

```python
# 获取制作配方信息
recipe_info = await get_wiki_page("工作台", format="markdown")

# 搜索特定物品的用途
usage_info = await search_wiki("钻石剑", limit=5)
```

### 2. 知识问答

```python
# 回答关于游戏机制的问题
redstone_info = await get_wiki_page("红石电路", format="both")

# 批量获取相关页面进行对比
comparison_pages = await get_wiki_pages_batch(
    ["钻石", "下界合金", "金锭"], 
    format="markdown"
)
```

### 3. 内容生成

```python
# 为博客文章收集素材
mob_info = await search_wiki("敌对生物", limit=20)

# 获取详细的游戏指南内容
guide_content = await get_wiki_page("新手指南", format="markdown")
```

## ⚖️ 版权说明

本工具获取的所有内容均来自 [中文 Minecraft Wiki](https://zh.minecraft.wiki)，遵循 **CC BY-NC-SA 3.0** 协议。

**使用要求:**
- ✅ 必须署名来源为中文 Minecraft Wiki
- ❌ 不得用于商业目的
- 🔄 修改内容需采用相同许可协议

## 🔧 开发和扩展

### 添加新工具

1. 在 `mcp_only_server.py` 中定义新的工具函数
2. 使用 `@mcp_server.tool()` 装饰器
3. 实现错误处理和日志记录
4. 更新文档

### 修改配置

修改 `config.json` 文件中的相应配置项，重启服务器生效。

### 日志调试

设置日志级别为 `DEBUG` 可以看到更详细的调试信息：

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## 🆘 故障排除

### 常见问题

1. **服务器启动失败**
   - 检查端口是否被占用
   - 确认依赖包已正确安装

2. **Wiki API 连接失败**
   - 确认 Wiki API 服务运行在 localhost:3000
   - 检查防火墙设置

3. **页面获取失败**
   - 检查页面名称是否正确
   - 尝试禁用缓存 (`use_cache=False`)

4. **搜索无结果**
   - 尝试使用不同的关键词
   - 检查命名空间设置

### 获取帮助

如遇问题，请检查：
1. 日志输出中的错误信息
2. Wiki API 服务的健康状态
3. 网络连接和防火墙设置

---

*最后更新：2025-08-01*