import json
import logging
import html
import re
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ProductDataExtractor:
    """Utility class to extract and format product data from Woolworths API response."""
    
    @staticmethod
    def clean_html(text: str) -> str:
        """Remove HTML tags and decode HTML entities from text."""
        if not text:
            return ""
        
        # Simple HTML tag removal (for basic cases)
        # For more complex HTML, consider using a library like BeautifulSoup
        text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        text = text.replace("<div>", "").replace("</div>", "\n")
        text = text.replace("<p>", "").replace("</p>", "\n")
        
        # Decode HTML entities
        return html.unescape(text).strip()
    
    @staticmethod
    def extract_list_from_comma_string(text: str) -> List[str]:
        """Extract a list of items from a comma-separated string."""
        if not text:
            return []
        
        items = [item.strip() for item in text.split(",")]
        return [item for item in items if item]
    
    @staticmethod
    def extract_json_from_string(json_str: str) -> Dict[str, Any]:
        """Extract JSON from a string."""
        if not json_str:
            return {}
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {}
    
    @staticmethod
    def extract_package_size(product: Dict[str, Any], display_name: str) -> str:
        """Extract package size from product data or name.
        
        First tries to find explicit PackageSize field, then tries to extract
        from the display name using regex patterns for common formats.
        """
        # Try to get the explicit package size first
        if "PackageSize" in product and product["PackageSize"]:
            return product["PackageSize"]
            
        # If not found, try to extract from the display name
        # Look for common patterns like "500g", "1kg", "750ml", "2L" etc.
        patterns = [
            r'(\d+(?:\.\d+)?\s*(?:kg|g|ml|l|oz|lb))\b',  # Regular formats like 500g, 1.5kg, 750ml
            r'(\d+(?:\.\d+)?\s*(?:KG|G|ML|L|OZ|LB))\b',  # Uppercase formats
            r'(\d+(?:\.\d+)?\s*(?:kilogram|gram|milliliter|liter))[s]?\b',  # Full word formats
            r'(\d+\s*(?:pk|pack|piece|pcs))s?\b',  # Pack quantities
        ]
        
        for pattern in patterns:
            match = re.search(pattern, display_name, re.IGNORECASE)
            if match:
                return match.group(1)
                
        return ""
    
    def extract_product_data(self, product_details: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant product data from Woolworths API response.
        
        Args:
            product_details: Raw product details from Woolworths API
            
        Returns:
            Dictionary with formatted product data
        """
        if not isinstance(product_details, dict) or "Product" not in product_details:
            logger.error("Invalid product details format")
            return {}
        
        product = product_details.get("Product", {})
        additional_attrs = product.get("AdditionalAttributes", {})
        
        # Extract basic product info
        display_name = product.get("DisplayName", "")
        description = self.clean_html(product.get("RichDescription") or additional_attrs.get("description", ""))
        ingredients = additional_attrs.get("ingredients", "")
        
        # Extract package size
        package_size = self.extract_package_size(product, display_name)
        
        # Extract dietary information
        dietary_info = additional_attrs.get("lifestyleanddietarystatement", "")
        allergy_info = additional_attrs.get("allergystatement", "")
        
        # Extract department and category information
        sap_categories = product.get("SapCategories", {})
        department = sap_categories.get("SapDepartmentName", "")
        category = sap_categories.get("SapCategoryName", "")
        subcategory = sap_categories.get("SapSubCategoryName", "")
        segment = sap_categories.get("SapSegmentName", "")
        
        # Combine category information
        department_category = f"{department} > {category} > {subcategory} > {segment}"
        
        # Extract available departments from JSON
        try:
            departments_json = additional_attrs.get("piesdepartmentnamesjson", "[]")
            departments = json.loads(departments_json)
            departments_str = ", ".join([d for d in departments if isinstance(d, str)])
            if not departments_str and isinstance(departments, list):
                departments_str = ", ".join([d.get("Description", "") for d in departments if isinstance(d, dict)])
            
            if departments_str:
                department_category += f" | Departments: {departments_str}"
        except Exception as e:
            logger.warning(f"Error parsing departments JSON: {e}")
        
        # Get subcategories if available
        try:
            subcategories_json = additional_attrs.get("piessubcategorynamesjson", "[]")
            subcategories = json.loads(subcategories_json)
            if isinstance(subcategories, list) and subcategories:
                subcategories_str = ", ".join(subcategories)
                department_category += f" | Subcategories: {subcategories_str}"
        except Exception as e:
            logger.warning(f"Error parsing subcategories JSON: {e}")
        
        return {
            "product_name": display_name,
            "product_description": description,
            "ingredients": ingredients,
            "package_size": package_size,
            "dietary_info": f"{dietary_info} | Allergy info: {allergy_info}",
            "department_category": department_category
        }
