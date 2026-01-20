from fastapi import FastAPI, HTTPException
from meal_service import MealService
from nutrition_service import NutritionService
from price_service import PriceService
import os

app = FastAPI()

# Initialize services
meal_svc = MealService("./data./13k-recipes.csv")
nutri_svc = NutritionService()
price_svc = PriceService()


def save_to_markdown(data: dict):
    # Ensure the results directory exists
    if not os.path.exists("results"):
        os.makedirs("results")
    
    # Create a safe filename from the title
    safe_title = "".join([c for c in data['title'] if c.isalnum() or c==' ']).rstrip()
    filename = f"results/{safe_title.replace(' ', '_').lower()}.md"
    
    # Accessing the specific keys from your result dictionary
    ingredients_md = "\n".join([f"- {i}" for i in data['ingredients_list']])
    
    # Extract nutrition totals from the nutrition_snapshot dictionary
    # This assumes nutrition_snapshot has the 'meal_totals' key from the previous step
    totals = data['nutrition_snapshot'].get('meal_totals', {"kcal": 0, "protein": 0})
    
    content = f"""# {data['title']}

## 📝 Instructions
{data['instructions']}

## 🥗 Ingredients
{ingredients_md}

---

## 📊 Summary
- **Calorie Limit Set:** {data['calories_limit']} kcal
- **Estimated Total Cost:** ${data['pricing'].get('total_estimated_cost', 0)} {data['pricing'].get('currency', 'USD')}
- **Total Calculated Energy:** {totals.get('kcal')} kcal
- **Total Calculated Protein:** {totals.get('protein')} g

> *Note: Pricing and nutrition are estimates based on the top ingredients.*
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename


@app.get("/generate-meal")
async def generate_meal(max_calories: int = 800):
    print("Step 1/3: Get meal from dataset.")
    meal = meal_svc.get_random_meal(max_calories)
    if not meal:
        raise HTTPException(status_code=404, detail="No meals found")

    print("Step 2/3: Estimate meal cost.")
    price_info = price_svc.estimate_cost(meal["search_ingredients"])

    print("Step 3/3: Get macros list for meal.")
    main_ingredient_macros = nutri_svc.get_macros_for_list(meal["search_ingredients"])

    result = {
        "title": meal["title"],
        "calories_limit": max_calories,
        "ingredients_list": meal["display_ingredients"],  # What the user sees
        "instructions": meal["instructions"],
        "pricing": price_info,
        "nutrition_snapshot": main_ingredient_macros,
    }
    save_to_markdown(result)

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
