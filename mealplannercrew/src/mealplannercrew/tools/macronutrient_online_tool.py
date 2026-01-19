from crewai_tools import SerperDevTool
from crewai.tools import tool

@tool("macronutrient_online_searcher")
def nutrition_tool(ingredient: str) -> str:
    """
    Searches for the macronutrients (calories, protein, fats, carbs) 
    per 100g of a specific ingredient. 
    Input should be an ingredient name.
    """
    search = SerperDevTool()
    
    query = f"macronutrients per 100g {ingredient} nutrition facts table"
    
    return search.run(search_query=query)