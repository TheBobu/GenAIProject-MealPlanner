from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from src.mealplannercrew.tools.body_composition_energy import health_calculator
from src.mealplannercrew.tools.price_tool import price_tool
from src.mealplannercrew.tools.recipe_tool import search_recipes
from src.mealplannercrew.tools.macronutrients_tool import fetch_ingredient_macros
from src.mealplannercrew.tools.macronutrient_online_tool import nutrition_tool
from src.mealplannercrew.settings import settings


@CrewBase
class Mealplannercrew:
    """Mealplannercrew crew"""

    smart_llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=settings.groq_api_key,
        max_tokens=1000
    )

    fast_llm = LLM(
        model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=settings.groq_api_key,
        max_tokens=1000,
    )

    backup_llm = LLM(
        model="gemini/gemma-3-12b-it",
        api_key=settings.google_api_key,
        max_tokens=1000,
    )

    mistral_llm = LLM(
        model="mistral/mistral-medium-latest",
        api_key=settings.mistral_api_key,
        max_tokens=1000,
    )


    agents: List[BaseAgent]
    tasks: List[Task]

    @before_kickoff
    def prepare_inputs(self, inputs):
        print(f"Starting crew with request: {inputs.get('user_request')}")

        return inputs

    @agent
    def recipe_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["recipe_researcher"],
            tools=[search_recipes],
            verbose=True,
            llm=self.mistral_llm,
        )

    @agent
    def nutritionist(self) -> Agent:
        return Agent(
            config=self.agents_config["nutritionist"],
            tools=[fetch_ingredient_macros, nutrition_tool],
            verbose=True,
            llm=self.mistral_llm,
        )

    @agent
    def cost_estimator(self) -> Agent:
        return Agent(
            config=self.agents_config["cost_estimator"],
            tools=[price_tool],
            verbose=True,
            llm = self.mistral_llm
        )

    # @agent
    # def creative_chef(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config["creative_chef"],
    #         tools=[fetch_ingredient_macros, search_recipes],
    #         verbose=True,
    #         llm=self.fast_llm,
    #     )

    @agent
    def plan_summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config["plan_summarizer"],
            verbose=True,
            llm=self.mistral_llm,
            tools=[search_recipes, health_calculator]
        )

    @task
    def research_recipes_task(self) -> Task:
        return Task(config=self.tasks_config["research_recipes_task"])

    # @task
    # def invent_meal_task(self) -> Task:
    #     return Task(config=self.tasks_config["invent_meal_task"])

    @task
    def calculate_macros_task(self) -> Task:
        return Task(config=self.tasks_config["calculate_macros_task"])

    @task
    def price_ingredients_task(self) -> Task:
        return Task(config=self.tasks_config["price_ingredients_task"])

    @task
    def summarize_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config["summarize_plan_task"],
            output_file="meal_plan_summary.md",  # Automatically saves the result here
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Mealplannercrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            max_rpm=15,
            planning_llm=self.smart_llm
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
