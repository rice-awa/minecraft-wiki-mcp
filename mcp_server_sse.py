import json
import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import aiohttp
from mcp.server.fastmcp import FastMCP

# Load configuration
def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"配置文件未找到: {config_path}，使用默认配置")
        return {
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
    except json.JSONDecodeError as e:
        logger.error(f"配置文件格式错误: {e}，使用默认配置")
        return load_config()  # Recursive call to get default config

# Initialize configuration
config = load_config()

# Setup logging
log_level = getattr(logging, config["logging"]["level"], logging.INFO)
logging.basicConfig(
    level=log_level,
    format=config["logging"]["format"]
)
logger = logging.getLogger("mc-wiki-mcp-server")

# Configuration constants
WIKI_API_BASE_URL = config["wiki_api"]["base_url"]
DEFAULT_TIMEOUT = config["wiki_api"]["timeout"]
MAX_RETRIES = config["wiki_api"]["max_retries"]
DEFAULT_FORMAT = config["wiki_api"]["default_format"]
DEFAULT_LIMIT = config["wiki_api"]["default_limit"]
MAX_BATCH_SIZE = config["wiki_api"]["max_batch_size"]
MAX_CONCURRENCY = config["wiki_api"]["max_concurrency"]

# Create FastMCP server with configuration
mcp_server = FastMCP(
    name=config["mcp_server"]["name"],
    dependencies=["asyncio", "aiohttp", "mcp", "pydantic"]
)

# HTTP Client for Wiki API
class WikiAPIClient:
    def __init__(self, base_url: str = WIKI_API_BASE_URL, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make GET request to Wiki API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with WikiAPIClient()' pattern.")
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Making request to {url} with params: {params}")
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully received response from {url}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"API returned status {response.status}: {error_text}")
                        raise aiohttp.ClientResponseError(
                            response.request_info,
                            response.history,
                            status=response.status,
                            message=error_text
                        )
            except aiohttp.ClientError as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"Failed to connect to Wiki API after {MAX_RETRIES} attempts: {e}")
                    raise
                logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to Wiki API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with WikiAPIClient()' pattern.")
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Making POST request to {url} with data: {data}")
                async with self.session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Successfully received response from {url}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"API returned status {response.status}: {error_text}")
                        raise aiohttp.ClientResponseError(
                            response.request_info,
                            response.history,
                            status=response.status,
                            message=error_text
                        )
            except aiohttp.ClientError as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"Failed to connect to Wiki API after {MAX_RETRIES} attempts: {e}")
                    raise
                logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff

# Wiki MCP Tools
@mcp_server.tool()
async def search_wiki(
    query: str,
    limit: int = None,
    namespaces: Optional[str] = None,
    format: str = "json"
) -> dict:
    """搜索 Minecraft Wiki 内容
    
    Args:
        query: 搜索关键词(尽量使用中文)
        limit: 结果数量限制，默认使用配置文件设置，最大50
        namespaces: 命名空间，多个用逗号分隔（可选）
        format: 响应格式，默认json
    
    Returns:
        搜索结果字典，包含匹配页面列表和分页信息,返回的结果并不是详细信息，请使用该工具后接着使用pageAPI查看详细信息。
    Notes:
        此工具只能依照关键词匹配搜索描述，可能无法返回跟关键词完全匹配的内容，注意分辨
    """
    if limit is None:
        limit = DEFAULT_LIMIT
    
    try:
        params = {
            "q": query,
            "limit": min(limit, 50)  # API限制最大50
        }
        if namespaces:
            params["namespaces"] = namespaces
        if format != "json":
            params["format"] = format
        
        async with WikiAPIClient() as client:
            result = await client.get("/api/search", params)
            
        if result.get("success"):
            return {
                "success": True,
                "query": query,
                "results": result["data"]["results"],
                "pagination": result["data"]["pagination"],
                "metadata": result["data"]["metadata"]
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown search error"),
                "query": query
            }
    
    except Exception as e:
        logger.error(f"Error searching wiki: {e}")
        return {
            "success": False,
            "error": f"搜索失败: {str(e)}",
            "query": query
        }

@mcp_server.tool()
async def get_wiki_page(
    page_name: str,
    format: str = None,
    use_cache: bool = True,
    include_metadata: bool = True
) -> dict:
    """获取指定页面的完整内容
    
    Args:
        page_name: 页面名称
        format: 输出格式 - html, markdown, both (默认使用配置文件设置)
        use_cache: 是否使用缓存 (默认True)
        include_metadata: 是否包含元数据 (默认True)
    
    Returns:
        页面内容字典，包含HTML/Markdown内容、元数据等
    """
    if format is None:
        format = DEFAULT_FORMAT
    
    try:
        params = {
            "format": format,
            "useCache": str(use_cache).lower(),
            "includeMetadata": str(include_metadata).lower()
        }
        
        # URL encode the page name
        import urllib.parse
        encoded_page_name = urllib.parse.quote(page_name, safe='')
        
        async with WikiAPIClient() as client:
            result = await client.get(f"/api/page/{encoded_page_name}", params)
        
        if result.get("success"):
            return {
                "success": True,
                "page_name": page_name,
                "data": result["data"]
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown page error"),
                "page_name": page_name
            }
    
    except Exception as e:
        logger.error(f"Error getting wiki page '{page_name}': {e}")
        return {
            "success": False,
            "error": f"获取页面失败: {str(e)}",
            "page_name": page_name
        }

@mcp_server.tool()
async def get_wiki_pages_batch(
    pages: List[str],
    format: str = "markdown",
    concurrency: int = None,
    use_cache: bool = True
) -> dict:
    """批量获取多个页面内容
    
    Args:
        pages: 页面名称列表
        format: 输出格式 - html, markdown, both (默认markdown)
        concurrency: 并发请求数 (默认使用配置文件设置)
        use_cache: 是否使用缓存 (默认True)
    
    Returns:
        批量获取结果字典，包含成功和失败的页面结果
    """
    if concurrency is None:
        concurrency = MAX_CONCURRENCY
    
    try:
        if len(pages) > MAX_BATCH_SIZE:  # 使用配置文件中的限制
            return {
                "success": False,
                "error": f"页面数量超过限制，最大支持{MAX_BATCH_SIZE}个页面",
                "pages": pages
            }
        
        data = {
            "pages": pages,
            "format": format,
            "concurrency": min(concurrency, MAX_CONCURRENCY),  # 使用配置文件限制
            "useCache": use_cache
        }
        
        async with WikiAPIClient() as client:
            result = await client.post("/api/pages", data)
        
        if result.get("success"):
            return {
                "success": True,
                "results": result["data"]["results"],
                "summary": result["data"]["summary"],
                "metadata": result["data"]["metadata"]
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown batch error"),
                "pages": pages
            }
    
    except Exception as e:
        logger.error(f"Error getting batch wiki pages: {e}")
        return {
            "success": False,
            "error": f"批量获取页面失败: {str(e)}",
            "pages": pages
        }

@mcp_server.tool()
async def check_page_exists(page_name: str) -> dict:
    """检查页面是否存在
    
    Args:
        page_name: 页面名称
    
    Returns:
        页面存在性检查结果
    """
    try:
        # URL encode the page name
        import urllib.parse
        encoded_page_name = urllib.parse.quote(page_name, safe='')
        
        async with WikiAPIClient() as client:
            result = await client.get(f"/api/page/{encoded_page_name}/exists")
        
        if result.get("success"):
            return {
                "success": True,
                "page_name": page_name,
                "exists": result["data"]["exists"],
                "page_info": result["data"].get("pageInfo"),
                "redirected": result["data"].get("redirected", False)
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "page_name": page_name,
                "exists": False
            }
    
    except Exception as e:
        logger.error(f"Error checking page existence '{page_name}': {e}")
        return {
            "success": False,
            "error": f"检查页面存在性失败: {str(e)}",
            "page_name": page_name,
            "exists": False
        }

# Wiki MCP Resources
@mcp_server.resource("minecraft://wiki/page/{page_name}")
async def get_wiki_page_resource(page_name: str) -> dict:
    """获取Wiki页面资源"""
    try:
        result = await get_wiki_page(page_name, format="both", use_cache=True, include_metadata=True)
        if result.get("success"):
            page_data = result["data"]["page"]
            return {
                "uri": f"minecraft://wiki/page/{page_name}",
                "name": page_data.get("title", page_name),
                "description": f"Minecraft Wiki 页面: {page_data.get('title', page_name)}",
                "mimeType": "application/json",
                "content": result
            }
        else:
            return {
                "uri": f"minecraft://wiki/page/{page_name}",
                "name": page_name,
                "description": f"Wiki页面不存在: {page_name}",
                "mimeType": "application/json",
                "content": result
            }
    except Exception as e:
        logger.error(f"Error getting wiki page resource '{page_name}': {e}")
        return {
            "uri": f"minecraft://wiki/page/{page_name}",
            "name": page_name,
            "description": f"获取Wiki页面资源失败: {page_name}",
            "mimeType": "application/json",
            "content": {
                "success": False,
                "error": str(e),
                "page_name": page_name
            }
        }

@mcp_server.resource("minecraft://wiki/search/{query}")
async def get_wiki_search_resource(query: str) -> dict:
    """获取Wiki搜索结果资源"""
    try:
        result = await search_wiki(query, limit=10)
        return {
            "uri": f"minecraft://wiki/search/{query}",
            "name": f"搜索: {query}",
            "description": f"Minecraft Wiki 搜索结果: {query}",
            "mimeType": "application/json",
            "content": result
        }
    except Exception as e:
        logger.error(f"Error getting wiki search resource '{query}': {e}")
        return {
            "uri": f"minecraft://wiki/search/{query}",
            "name": f"搜索: {query}",
            "description": f"Wiki搜索失败: {query}",
            "mimeType": "application/json",
            "content": {
                "success": False,
                "error": str(e),
                "query": query
            }
        }

# Health check tool for Wiki API
@mcp_server.tool()
async def check_wiki_api_health() -> dict:
    """检查Wiki API服务健康状态"""
    try:
        async with WikiAPIClient() as client:
            result = await client.get("/health")
        
        return {
            "success": True,
            "api_status": "healthy",
            "health_data": result
        }
    except Exception as e:
        logger.error(f"Wiki API health check failed: {e}")
        return {
            "success": False,
            "api_status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    # Run MCP server with configuration
    logger.info("Starting Minecraft Wiki MCP Server...")
    logger.info(f"Configuration: {config['mcp_server']}")
    logger.info(f"Wiki API Base URL: {WIKI_API_BASE_URL}")
    
    # Log copyright notice
    if "metadata" in config:
        logger.info(f"版权信息: {config['metadata'].get('copyright_notice', 'N/A')}")
    
    # Set server configuration from config file
    server_config = config["mcp_server"]
    mcp_server.settings.host = server_config.get("host", "0.0.0.0")
    mcp_server.settings.port = server_config.get("port", 8000)
    
    try:
        mcp_server.run(transport="sse")
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        raise 
