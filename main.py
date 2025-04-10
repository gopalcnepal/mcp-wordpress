import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP(
    name="WordPress",
    instructions="This is a WordPress server. That will help you with getting information of given WordPress site.",
    )

# Constants
USER_AGENT = "wordpress-app/1.0"
WORDPRESS_URL = os.getenv("WORDPRESS_URL")


# Function to fetch post response data from provided url
async def fetch_post_response_data(url: str) -> dict:
    """
    Fetch post response data from the provided URL.
    Args:
        url (str): The URL to fetch the post response data from.
    Returns:
        dict: The dictionary of post response data.
    """
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        # Check if the response is valid JSON
        try:
            return response.json()
        except ValueError:
            raise httpx.HTTPStatusError(
                f"Invalid JSON response from {url}: {response.text}",
                request=response.request,
                response=response,
            )

# Function to format the post response data
def format_post_response_data(response: Any) -> dict:
    """
    Format the post response from the WordPress API.
    Args:
        response (Any): The response from the WordPress API.
    Returns:
        dic: The dictionary of formatted response.
    """
    response_text = {
                    "id": response["id"],
                    "date": response["date"],
                    "link": response["link"],
                    "title": response["title"]["rendered"],
                    "content": response["content"]["rendered"],
                    "featured_media": response["featured_media"]
                }
    return response_text

# Register the tool with FastMCP
@mcp.tool("fetch_wordpress_info")
async def fetch_wordpress_info_tool() -> dict[str, Any]:
    """
    Fetch WordPress site information.
    Returns:
        dict[str, Any]: The response from the WordPress API.
    """
    url = f"{WORDPRESS_URL}/wp-json"
    response_data = await fetch_post_response_data(url)
    
    response_text = {
        "name": response_data["name"],
        "description": response_data["description"],
        "url": response_data["url"],
    }
    return response_text


# Tool to fetch posts from a WordPress site
@mcp.tool("fetch_posts")
async def fetch_posts_tool(page: int = 1, per_page: int = 2) -> list[dict[str, Any]]:
    """
    Fetch posts from a WordPress site.
    Args:
        page (int): The page number to fetch.
        per_page (int): The number of posts per page.
    Returns:
        dict[str, Any]: The response from the WordPress API.
    """
    url = f"{WORDPRESS_URL}/wp-json/wp/v2/posts?page={page}&per_page={per_page}"
    response_data = await fetch_post_response_data(url)
    response_text = [format_post_response_data(post) for post in response_data]
    return response_text

# Tools to fetch posts by category
@mcp.tool("fetch_posts_by_category")
async def fetch_posts_by_category_tool(category: str, page: int = 1) -> dict[str, Any]:
    """
    Fetch posts by category name provided from a WordPress site.
    Args:
        category (str): The category name to filter posts by.
        page (int): The page number to fetch.
    Returns:
        dict[str, Any]: The response from the WordPress API.
    """
    url = f"{WORDPRESS_URL}/wp-json/wp/v2/posts?categories={category}&page={page}"
    response_data = await fetch_post_response_data(url)
    response_text = [format_post_response_data(post) for post in response_data]
    return response_text

# Tool to fect list of categories
@mcp.tool("fetch_categories")
async def fetch_categories_tool() -> dict[str, Any]:
    """
    Fetch list of categories from a WordPress site.
    Returns:
        dict[str, Any]: The response from the WordPress API.
    """
    url = f"{WORDPRESS_URL}/wp-json/wp/v2/categories"
    response_data = await fetch_post_response_data(url)
    response_text = [
        {
            "id": category["id"], 
            "name": category["name"],
            "count": category["count"],
            "link": category["link"]
        } for category in response_data
    ]
    return response_text


# Tool to fetch single post by ID
@mcp.tool("fetch_post_by_id")
async def fetch_post_by_id_tool(post_id: int) -> dict[str, Any]:
    """
    Fetch a single post by ID from a WordPress site.
    Args:
        post_id (int): The ID of the post to fetch.
    Returns:
        dict[str, Any]: The response from the WordPress API.
    """
    url = f"{WORDPRESS_URL}/wp-json/wp/v2/posts/{post_id}"
    response_data = await fetch_post_response_data(url)
    response_text = format_post_response_data(response_data)
    return response_text
   
# Tool to fetch pages of the wordpress site
@mcp.tool("fetch_pages")
async def fetch_pages_tool(page: int = 1, per_page: int = 2) -> dict[str, Any]:
    """
    Fetch pages from a WordPress site.
    Args:
        page (int): The page number to fetch.
        per_page (int): The number of pages per page.
    Returns:
        dict[str, Any]: The response from the WordPress API.
    """
    url = f"{WORDPRESS_URL}/wp-json/wp/v2/pages?page={page}&per_page={per_page}"
    response_data = await fetch_post_response_data(url)
    response_text = [format_post_response_data(post) for post in response_data]
    return response_text

# Tool to fetch single page by ID
@mcp.tool("fetch_page_by_id")
async def fetch_page_by_id_tool(page_id: int) -> dict[str, Any]:
    """
    Fetch a single page by ID from a WordPress site.
    Args:
        page_id (int): The ID of the page to fetch.
    Returns:
        dict[str, Any]: The response from the WordPress API.
    """
    url = f"{WORDPRESS_URL}/wp-json/wp/v2/pages/{page_id}"
    response_data = await fetch_post_response_data(url)
    response_text = format_post_response_data(response_data)
    return response_text


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
