from crewai_tools import SerperDevTool
from crewai.tools import tool

@tool("european_price_searcher")
def price_tool(ingredient: str) -> str:
    """
    Searches for the current price of a specific food ingredient in Europe.
    Input should be a single ingredient name (e.g., 'Chicken Breast').
    """
    search = SerperDevTool()
    # We add 'price in Euro' to the query to guide the search
    
    results = search.run(search_query=f"current price of {ingredient} in Euro supermarket")
    
    if isinstance(results, list):
        return "\n".join([str(item) for item in results])
    
    return str(results)
