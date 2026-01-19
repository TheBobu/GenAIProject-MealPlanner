from crewai.tools import tool
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import os

class RecipeSearcher:
    """Singleton class to handle recipe searching with sentence transformers."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RecipeSearcher, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.csv_path = "./knowledge/13k-recipes.csv"
        self.cache_path = "./knowledge/recipe_embeddings_cached.npy"
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self._model = None
        self._df = None
        self._embeddings = None
        self._initialize()
        self._initialized = True
    
    def _initialize(self):
        """Load model, CSV, and create embeddings."""
        print("Initializing Recipe Search Tool...")
        
        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self._model = SentenceTransformer(self.model_name, device=device)
        print(f"Loaded model: {self.model_name} on {device.upper()}")
        
        # Load CSV
        self._df = pd.read_csv(self.csv_path)
        print(f"Loaded {len(self._df)} recipes from CSV")
        
        # Create combined text for search using your CSV columns
        self._df['search_text'] = (
            self._df['Title'].fillna('') + ' ' + 
            self._df['Ingredients'].fillna('') + ' ' + 
            self._df['Instructions'].fillna('')
        )
        
        # Create embeddings
        if os.path.exists(self.cache_path):
            print(f"Loading cached embeddings from {self.cache_path}...")
            self._embeddings = np.load(self.cache_path)
            print(f"Loaded {len(self._embeddings)} cached embeddings!")
        else:
            print("Creating embeddings...")
            texts = self._df['search_text'].tolist()
            self._embeddings = self._model.encode(texts, show_progress_bar=True)
            np.save(self.cache_path, self._embeddings)
            print(f"Emeddings cached at {self.cache_path}.")
        print("Recipe Search Tool ready!")
    
    def search(self, query: str, top_k: int = 5) -> str:
        """
        Search recipes using semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            Formatted string with search results
        """
        # Encode query
        query_embedding = self._model.encode([query])[0]
        
        # Calculate cosine similarity
        similarities = np.dot(self._embeddings, query_embedding) / (
            np.linalg.norm(self._embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Format results
        results = [f"🔍 Search Results for: '{query}'\n{'='*80}\n"]
        
        for rank, idx in enumerate(top_indices, 1):
            row = self._df.iloc[idx]
            score = similarities[idx]
            
            results.append(f"\n📊 Rank {rank} | Relevance: {score:.2%}")
            results.append("-" * 80)
            
            # Display recipe details matching your CSV structure
            results.append(f"ID: {row['Id']}")
            results.append(f"Title: {row['Title']}")
            results.append(f"Ingredients: {row['Ingredients'][:300]}...")
            results.append(f"Instructions: {row['Instructions'][:300]}...")
            
            # Optional: include cleaned ingredients if useful
            if pd.notna(row['Cleaned_Ingredients']):
                results.append(f"Cleaned Ingredients: {row['Cleaned_Ingredients'][:200]}...")
        
        return "\n".join(results)


# Initialize the searcher (will only happen once due to singleton pattern)
_searcher = RecipeSearcher()


@tool("search_recipes")
def search_recipes(query: str) -> str:
    """
    Search for recipes based on ingredients, dish names, or cooking methods.
    
    This tool searches through a database of 13,000 recipes using semantic similarity
    to find the most relevant recipes based on your query.
    
    Args:
        query: A natural language query describing what you're looking for.
               Examples: 'healthy chicken dinner', 'vegan dessert', 'pasta with tomatoes',
               'low carb breakfast', 'Italian cuisine'
    
    Returns:
        Top 5 most relevant recipes with their ID, title, ingredients, and instructions.
    """
    return _searcher.search(query, top_k=5)