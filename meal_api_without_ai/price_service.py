import requests

class PriceService:
    def __init__(self):
        # Base URL for the Open Food Facts Price API
        self.price_api_url = "https://prices.openfoodfacts.org/api/v1/prices"
        
        # Generic fallback prices (USD per standard unit) 
        # based on global cost-of-living averages
        self.generic_prices = {
            "chicken": 3.50,   # per lb
            "rice": 0.80,      # per lb
            "apple": 0.50,     # each
            "butter": 4.00,    # per pack
            "egg": 0.25,       # each
            "default": 1.50    # default per ingredient
        }

    def get_real_price(self, ingredient_name: str):
        """Attempts to fetch the latest crowdsourced price from Open Food Facts."""
        try:
            # We search for the product name in the price database
            params = {"product_name": ingredient_name, "size": 1}
            response = requests.get(self.price_api_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    # Return the most recent price found in the database
                    return data["items"][0].get("price")
        except Exception:
            pass # Fall back to generic if API is down
            
        return self.generic_prices.get(ingredient_name.lower(), self.generic_prices["default"])

    def estimate_cost(self, ingredients: list):
        total_cost = 0.0
        breakdown = []
        
        for item in ingredients:
            price = self.get_real_price(item)
            total_cost += float(price)
            breakdown.append({"item": item, "price": price})
            
        return {
            "total_estimated_cost": round(total_cost, 2),
            "currency": "USD",
            "breakdown": breakdown
        }