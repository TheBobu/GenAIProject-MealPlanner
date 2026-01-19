import openfoodfacts
from crewai.tools import tool

@tool("fetch_ingredient_macros")
def fetch_ingredient_macros(ingredient_name: str) -> str:
    """
    Search for a food ingredient on Open Food Facts and return 
    its macronutrients (calories, proteins, carbs, fats) per 100g.
    """
    api = openfoodfacts.API(user_agent="MyMealPlannerApp/1.0",timeout=20)
    
    search_results = api.product.text_search(ingredient_name)
    
    if search_results.get('count', 0) > 0:
        product = search_results['products'][0]
        name = product.get('product_name', 'Unknown')
        nutriments = product.get('nutriments', {})
        
        macros = {
            "calories": nutriments.get('energy-kcal_100g', 'N/A'),
            "proteins": nutriments.get('proteins_100g', 'N/A'),
            "carbohydrates": nutriments.get('carbohydrates_100g', 'N/A'),
            "fat": nutriments.get('fat_100g', 'N/A'),
            "unit": "per 100g"
        }
        
        return f"Nutritional data for '{name}': {macros}"
    
    return f"No nutritional data found for '{ingredient_name}'."