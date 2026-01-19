from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from src.mealplannercrew.tools.price_tool import price_tool
from src.mealplannercrew.tools.recipe_tool import search_recipes
from src.mealplannercrew.tools.macronutrients_tool import fetch_ingredient_macros


@CrewBase
class Mealplannercrew:
    """Mealplannercrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def recipe_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["recipe_researcher"],
            tools=[search_recipes],
            verbose=True,
        )

    @agent
    def nutritionist(self) -> Agent:
        return Agent(
            config=self.agents_config["nutritionist"],
            tools=[fetch_ingredient_macros],
            verbose=True,
        )

    @agent
    def cost_estimator(self) -> Agent:
        return Agent(
            config=self.agents_config['cost_estimator'],
            tools=[price_tool],  # Uses the custom search tool
            verbose=True
    )

    @agent
    def creative_chef(self) -> Agent:
        return Agent(config=self.agents_config["creative_chef"], verbose=True)

    @agent
    def plan_summarizer(self) -> Agent:
        return Agent(config=self.agents_config["plan_summarizer"], verbose=True)

    @task
    def research_recipes_task(self) -> Task:
        return Task(config=self.tasks_config["research_recipes_task"])

    @task
    def invent_meal_task(self) -> Task:
        return Task(config=self.tasks_config["invent_meal_task"])

    @task
    def calculate_macros_task(self) -> Task:
        return Task(config=self.tasks_config["calculate_macros_task"])

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
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
