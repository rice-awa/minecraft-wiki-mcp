# Minecraft Wiki MCP 项目开发任务清单

## 📋 项目概述

将现有的基础 MCP 服务器改造成一个功能完整的 Minecraft Wiki MCP 服务，通过集成 Wiki API 为大模型提供 Minecraft 相关知识参考。

## 🎯 核心目标

- 集成 Minecraft Wiki API（localhost:3000）
- 提供搜索、页面获取、批量处理等工具
- 为 LLM 提供结构化的 Minecraft 知识访问接口
- 支持多种输出格式（HTML、Markdown）

---

## ✅ 已完成任务

- [x] **分析现有API接口文档** - 理解Wiki API的功能和数据结构
- [x] **创建详细的todolist.md文档** - 本文档

---

## 🚧 进行中任务

无

---

## 📝 待完成任务

### 🔥 高优先级任务

#### 1. 设计MCP工具架构
- [ ] 定义需要的工具和资源
- [ ] 设计工具参数和返回值结构
- [ ] 制定错误处理策略

#### 2. 实现Wiki搜索工具（search_wiki）
- [ ] 集成 `/api/search` 端点
- [ ] 支持搜索关键词、结果限制、命名空间过滤
- [ ] 处理搜索结果分页
- [ ] 添加相关度排序和结果预览

#### 3. 实现获取Wiki页面内容工具（get_wiki_page）
- [ ] 集成 `/api/page/:pageName` 端点
- [ ] 支持多种输出格式（HTML、Markdown、both）
- [ ] 处理页面不存在、重定向等情况
- [ ] 包含页面元数据（分类、图片、表格等）

#### 4. 添加Wiki API HTTP客户端配置和错误处理
- [ ] 创建 HTTP 客户端类
- [ ] 配置请求超时和重试机制
- [ ] 统一错误处理和日志记录
- [ ] 支持缓存控制

### 🔶 中优先级任务

#### 5. 实现批量获取Wiki页面工具（get_wiki_pages_batch）
- [ ] 集成 `/api/pages` 端点
- [ ] 支持并发请求控制
- [ ] 批量处理结果汇总
- [ ] 错误恢复和部分成功处理

#### 6. 实现检查页面存在性工具（check_page_exists）
- [ ] 集成 `/api/page/:pageName/exists` 端点
- [ ] 快速验证页面存在性
- [ ] 处理重定向信息

#### 7. 创建Wiki资源定义
- [ ] 定义 `minecraft://wiki/page/{pageName}` 资源
- [ ] 定义 `minecraft://wiki/search/{query}` 资源
- [ ] 实现资源的懒加载和缓存

#### 8. 完善MCP服务器配置和元数据
- [ ] 更新服务器名称和描述
- [ ] 添加依赖项列表
- [ ] 配置服务器运行参数

#### 9. 添加配置文件支持
- [ ] 创建配置文件（config.json 或 .env）
- [ ] 支持 API base URL 配置
- [ ] 支持缓存设置
- [ ] 支持请求限制设置

### 🔵 低优先级任务

#### 10. 编写测试用例和文档
- [ ] 编写单元测试
- [ ] 创建使用示例
- [ ] 编写 README.md
- [ ] 添加 API 文档

#### 11. 优化错误处理和日志记录
- [ ] 完善日志格式
- [ ] 添加性能监控
- [ ] 优化错误消息

---

## 🛠️ 技术实现细节

### MCP 工具设计

#### 1. search_wiki
```python
@mcp_server.tool()
async def search_wiki(
    query: str,
    limit: int = 10,
    namespaces: str = None,
    format: str = "json"
) -> dict
```

#### 2. get_wiki_page
```python
@mcp_server.tool()
async def get_wiki_page(
    page_name: str,
    format: str = "both",
    use_cache: bool = True,
    include_metadata: bool = True
) -> dict
```

#### 3. get_wiki_pages_batch
```python
@mcp_server.tool()
async def get_wiki_pages_batch(
    pages: list[str],
    format: str = "markdown",
    concurrency: int = 3,
    use_cache: bool = True
) -> dict
```

#### 4. check_page_exists
```python
@mcp_server.tool()
async def check_page_exists(page_name: str) -> dict
```

### 资源设计

#### 1. Wiki页面资源
```python
@mcp_server.resource("minecraft://wiki/page/{page_name}")
async def get_wiki_page_resource(page_name: str) -> dict
```

#### 2. Wiki搜索资源
```python
@mcp_server.resource("minecraft://wiki/search/{query}")
async def get_wiki_search_resource(query: str) -> dict
```

---

## 📊 项目里程碑

### 阶段1：核心功能实现（当前）
- [ ] 基础工具实现
- [ ] HTTP客户端集成
- [ ] 错误处理机制

### 阶段2：功能增强
- [ ] 批量处理
- [ ] 资源定义
- [ ] 配置管理

### 阶段3：完善和优化
- [ ] 测试和文档
- [ ] 性能优化
- [ ] 错误处理优化

---

## 🚀 开发环境要求

- Python 3.8+
- FastMCP
- aiohttp/httpx（HTTP客户端）
- pydantic（数据验证）
- Minecraft Wiki API 服务运行在 localhost:3000

---

## 📝 注意事项

1. **版权遵循**：所有Wiki内容遵循 CC BY-NC-SA 3.0 协议
2. **请求限制**：遵循API的频率限制（100次/分钟）
3. **错误处理**：优雅处理网络错误、API错误和数据解析错误
4. **缓存机制**：合理利用API的缓存功能提升性能
5. **数据格式**：支持多种输出格式以适应不同使用场景

---

*最后更新：2025-08-01*