Generative AI Project 2025/2026 - Meal Planner Generator
---
Author: Andrei Florescu

# Table of Contents

- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
  - [Project Description](#project-description)
  - [Datasets and 3rd party APIs used](#datasets-and-3rd-party-apis-used)
- [Project Structure](#project-structure)
  - [Backend(mealplannercrew)](#backendmealplannercrew)
    - [API app.py](#api-apppy)
    - [Database service database-service](#database-service-database-service)
    - [Crew](#crew)
      - [LLMs](#llms)
      - [Agents and Tasks](#agents-and-tasks)
      - [Custom Tools](#custom-tools)
  - [Frontend(meal-planner-frontend)](#frontendmeal-planner-frontend)
  - [Backend without Generative AI(meal\_api\_without\_ai)](#backend-without-generative-aimeal_api_without_ai)
- [How to run](#how-to-run)
  - [Run the project using Docker](#run-the-project-using-docker)
    - [1. Create environment file](#1-create-environment-file)
    - [2. Docker instalation](#2-docker-instalation)
  - [(Optional) Run the project locally](#optional-run-the-project-locally)
- [Example runs](#example-runs)

---

# Introduction

## Project Description

This project aims to develop an interactive meal planner where users can achieve their dietary goals by generating personalized meal plans based on their preferences, as well as dietary restrictions and nutritional goals. The targeted users for this projects are home cooks, fitness enthusiasts, and individuals with specific dietary needs who are looking for fast meal planning ideas that align with their health goals. 

## Datasets and 3rd party APIs used 

The data used in this projects comes from the dataset available on [github](https://github.com/josephrmartinez/recipe-dataset). The original source of this dataset was created by scraping from the Epicurious Website. The content was uploaded to Kaggle as [Food Ingredients and Recipes Dataset with Images](https://www.kaggle.com/datasets/pes12017000148/food-ingredients-and-recipe-dataset-with-images). For the nutritional values the [openfoodfacts](https://openfoodfacts.github.io) API is used. For other information gathered the [Serper.Dev Tool](https://serper.dev) is used to scrape information from different google search queries.

---

# Project Structure

The project contains 3 applications: 
- **Backend**([mealplannercrew](./mealplannercrew/)): a crew and api application
- **Frontend**([meal-planner-frontend](./meal-planner-frontend/)): a vite react web application
- **Backend without generative AI**([meal_api_without_ai](./meal_api_without_ai/)): a simple backend that generates meals based on inputs on a form

## Backend([mealplannercrew](./mealplannercrew/))

The project contains an [env.example](./mealplannercrew/.env.example) file which contains an example of how the .env file should look like and what it needs to contain in order to run.

This project contains three parts:

### API [app.py](./mealplannercrew/app.py)

The API part of the app is created using the **fastapi** library. This projects parts are hardcoded for the moment (database path, app url, cors, etc.). Currently the api is served at the default port 8000. The API uses the [database service](#database-service) and [the crew](#crew) in order to provide the user with meal information. The crew is run asynchronously on a different thread in order to not block the API. The user can check the status of his requests at any given point to see if they are completed. The API contains the following endpoints:

- **GET /users** - returns the list of users and their information
- **GET /status/{username}** - returns the list of requests the user has made to the crew and their status as well as results
- **POST /generate-plan** - (username: str, prompt: str) starts the generation of a meal or a plan depending on the user prompt usint the crew
- **POST /users/profile** - (profile: UserProfile) saves a new user to the database which can further be used to make requests to the crew
- **GET /docs** - view the API Swagger page

The api can be run locally using the following command:

```sh
uv run uvicorn app:app --env-file .env
```

### Database service [database-service](./mealplannercrew/src/database_service/)

The project uses an SQLite database to store the users and the result of the requests done by the users to the crew. The database service contains the following features:

- **init_db**: creates a SQLite Database and its tables if it doesn't exist and creates a connection to it.
- **save_user_profile**: saves a new user
- **get_user**: returns a user by their username
- **get_all_users**: returns a list of all users
- **save_task_result**: saves the result of a prompt done by a user to the crew, as well as when the request was done and its current status (pending, success, fail)
- **get_task_result**: gets the contents of a task requested by a user
- **get_user_tasks**: gets a list of all the requests done by the user to the crew

This part needs to be developed further to accomodate update and delete operations.

### Crew

The generative AI logic of the project is done by using [crewai](https://www.crewai.com). The crew can be run using the [api](#api-apppy) or individually by running the commands described in the [pyproject.toml](./mealplannercrew/pyproject.toml) such as `crewai run`

#### LLMs

The crew uses the following LLMs:
- groq/llama-3.3-70b-versatile
- groq/meta-llama/llama-4-scout-17b-16e-instruct
- mistral/mistral-small-latest
- mistral/mistral-medium-latest
- mistral/mistral-large-latest

The reason for including this many LLMs is to split the tasks of the crew between smarter, faster or more balanced LLMs to increase efficiency as well as use the free plan of the [groq](https://groq.com) and [mistral](https://console.mistral.ai/home) services in full, and bypass quota limitations.

To use the LLMs from their respective APIs, the [.env.example](/mealplannercrew/.env.example) needs to be copied as an .env file and have each API key filled out in order for the crew to work properly.

#### Agents and Tasks

There are 5 agents (1 commented out) described in the crew configuration: 
- **recipe_researcher** - Finds the best meals from the recipe database that match the user's preferences.
- **nutritionist** - Calculates the exact nutritional breakdown for a given meal
- **cost_estimator** - Find the most current market prices for the ingredients and calculate the meal cost
- **plan_summarizer** - Synthesizes the meal choices, nutritional data, and cost estimates
- **creative_chef** (commented out) - used to create new recipes that don't appear in the dataset, currently excluded because it generated too many tokens and caused LLM errors in the crew.

Each agent uses an LLM according to their needs, for example the retrieval task of the researcher uses a fast LLM while the plan summarizer uses a smarter LLM with more params to generate a more accurate and appealing plan.
Currently all the agents have one task according to their description. The agent definitions can be found [here](./mealplannercrew/src/mealplannercrew/config/agents.yaml) and the task definitions can be found [here](./mealplannercrew/src/mealplannercrew/config/tasks.yaml).

The result of the crew is currently saved in the database and as a markdown file.

#### Custom Tools

The custom tools are created in order for the agents to be able to complete their tasks. The following tools were added:

- **recipe_tool**: user by the recipe researcher to search in the recipe dataset csv; initializes itself before the crew is run to create embeddings of the dataset and cache them to disk.
- **macronutrients_tool**: uses the [openfoodfacts](https://openfoodfacts.github.io) API to get ingredient macros; used by the nutritionist
- **macronutrient_tool_online**: uses the [Serper.Dev Tool](https://serper.dev) to search for an ingredient macronutrients in case the other macronutrient tool returned no results; used by the nutritionist
- **price_tool**: uses the [Serper.Dev Tool](https://serper.dev) to search for an ingredients price per 100g in Euro; used by the cost estimator
- **body_composition_energy**: a tool used by the plan summarizer to calculate the BMI of a person if they include that user information in their profile and their maintenance calories as well as weight loss/gain calories. 

The tools can be found in [this folder](./mealplannercrew/src/mealplannercrew/tools/)

## Frontend([meal-planner-frontend](./meal-planner-frontend/))

The frontend application is a **vite React** app which currently is created as a one file ([App.jsx](./meal-planner-frontend/src/App.jsx)) frontend app. It can be run using the `npm run dev` command and it's served by default on the port 5173. It contains the following sections: 

- User profile creation
- Generate plan
- View users
- View user requests to the crew

The frontend application calls the [Generative AI API](#backendmealplannercrew) in order to retrieve information from the database and display it.

## Backend without Generative AI([meal_api_without_ai](./meal_api_without_ai/))

An API application used for comparison to the [Generative AI API app](#backendmealplannercrew). This is not included in any docker definition and can be run only locally. To run it you need to install its [requirements](./meal_api_without_ai/requirements.txt) into a python environment and the run it using the following command: `python -m main`. The API is served on the default port 8000 which conflicts with the other API, so only one of them can be run at a time.

The api has the following endpoints: 
- **GET /generate-meal** - (params: max_calories, alergies, dietary pref) generate one meal by querying the database using a simple meal service and tries to match the meal to the parameters given by the user and then get its nutritional and price data by using the [openfoodfacts](https://openfoodfacts.github.io) API. At the end the result is generated as a hardcoded markdown.
- **GET /docs** - view the API Swagger page

---

# How to run

To run the Generative AI Backend and the associated Frontend up the following steps need to be completed: 

## Run the project using Docker

### 1. Create environment file

Copy the [`.env.example`](./env.example) from the root folder as `.env` and fill the variables with API Keys for each service.

### 2. Docker instalation

Make sure to have a running docker instance and then from the root folder run the following command

```sh
docker-compose up --build -d 
```

You can choose wether to attach or detach from the terminal by using the `-d` parameter

This command will create two containers and serve them by default at the [port 8000](http://localhost:8000/docs) for the backend app and [port 5173](http://localhost:5173) for the frontend app on the localhost.

## (Optional) Run the project locally

To run the project locally a conda environment is needed. The definition of the environment can be found in the [yaml file](./environment.yml) from the root folder which references the [requirements](./requirements.txt) file.

```sh
conda env create -f environment.yml
```

---

# Example runs

In the folder [result_examples](./result_examples/) a few example runs can be found to showcase each API's capabilities. The runs are represented as markdown files. For the [Generative AI API examples](./result_examples/results_with_gen_ai/) there are examples for one meal or for day plans and each time a different user is used with different dietary preferences, body compositions as well as nutritional goals. For the [results without generative AI](./result_examples/results_without_gen_ai/) there are a few example runs of the other API saved as markdown which showcase that the API can retrieve meals, but it's not as easy to include user preferences and accurate live data into the results.