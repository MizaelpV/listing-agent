from crewai.tools import BaseTool
import httpx
from urllib.parse import quote
import os

class CategoryFinderTool(BaseTool):
    name: str = "MeLi Category Finder"
    description: str = "Use this tool to find the most appropriate MercadoLibre category for a product given its title."

    def _run(self, product_title: str) -> str:
        url = f"https://api.mercadolibre.com/sites/MLC/domain_discovery/search?limit=3&q={quote(product_title)}"
        
        with httpx.Client() as client:
            response =  client.get(url)
            response.raise_for_status()
            response_category = response.json()
        
        if not response_category:
            return ("Category not found")

        lines = []
        for i, category in enumerate(response_category):
            lines.append(f"{i+1}. {category['category_name']} ({category['category_id']}) — domain: {category['domain_id']}")
        return "\n".join(lines)






