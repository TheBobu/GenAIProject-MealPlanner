import openfoodfacts

class NutritionService:
    def __init__(self):
        self.api = openfoodfacts.API(user_agent="MyMealApp/1.0", timeout=20)

    def get_macros_for_list(self, ingredients: list):
        results = []
        totals = {
            "total_kcal_100g_sum": 0,
            "total_protein_100g_sum": 0
        }
        # We only take the first 5 main ingredients to keep the API response fast
        for item in ingredients[:5]:
            search = self.api.product.text_search(item)
            if search['products']:
                prod = search['products'][0]
                nutri = prod.get('nutriments', {})
                results.append({
                    "ingredient": item,
                    "kcal_100g": nutri.get('energy-kcal_100g', 0),
                    "protein": nutri.get('proteins_100g', 0)
                })
                kcal = nutri.get('energy-kcal_100g', 0)
                protein = nutri.get('proteins_100g', 0)
                totals["total_kcal_100g_sum"] += kcal
                totals["total_protein_100g_sum"] += protein
        
        return {
            "individual_ingredients": results,
            "meal_totals": {
                "kcal": round(totals["total_kcal_100g_sum"], 2),
                "protein": round(totals["total_protein_100g_sum"], 2)
            }
        }