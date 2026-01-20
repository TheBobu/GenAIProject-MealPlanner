import pandas as pd
import ast
import re

class MealService:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)

    def clean_ingredient_name(self, raw_ingredient: str):
        # Regex to remove measurements like '2 Tbsp', '1 lb', '(3lb)', etc.
        # This is a simplified version; cleaning 13k rows perfectly is a common challenge.
        cleaned = re.sub(r'\d+\s*(tsp|Tbsp|lb|oz|cup|cups|medium|small|large|–)\.?\s*', '', raw_ingredient, flags=re.IGNORECASE)
        cleaned = re.sub(r'\(.*?\)', '', cleaned) # Remove anything in parentheses
        return cleaned.strip().split(',')[-1].strip() # Take the core noun

    def get_random_meal(self, max_kcals: float):
        # Since your CSV lacks a 'Calories' column, we will pick random 
        # or you can add a placeholder logic here.
        meal_row = self.df.sample(n=1).iloc[0]
        
        # Parse the string "['item1', 'item2']" into a real list
        raw_list = ast.literal_eval(meal_row['Cleaned_Ingredients'])
        
        # Create a search-friendly list for the APIs
        search_terms = [self.clean_ingredient_name(i) for i in raw_list]

        return {
            "title": meal_row['Title'],
            "display_ingredients": raw_list, # For the user to read
            "search_ingredients": search_terms, # For the APIs to use
            "instructions": meal_row['Instructions']
        }