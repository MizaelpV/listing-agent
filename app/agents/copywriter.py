from crewai import Agent, Task, Crew, LLM
import asyncio
from dotenv import load_dotenv

load_dotenv()

import os

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

agent_goal = (
    "Generate high-converting, SEO-optimized product listings for MercadoLibre, "
    "crafting titles up to 60 characters—the platform's maximum title length—"
    "while maximizing relevance, clarity, and click-through rate."
)
agent_backstory = (
    "You are a senior e-commerce copywriter specialized in crafting high-converting product listings "
    "that blend SEO, persuasive storytelling, and marketplace best practices. "
    "You understand buyer psychology deeply and optimize titles, descriptions, and value propositions to maximize visibility, CTR, and conversions—especially on MercadoLibre."
)


agent = Agent(
    role="Expert Copywriter",
    goal=agent_goal,
    backstory=agent_backstory,
    llm=llm 
)

task = Task(
    description=(
        "Create a product listing for: {product_description}. "
        "Generate a title and description tailored to the marketplace constraints and best practices."
    ),
    expected_output=(
        'A valid JSON object: '
        '{"title": "<title>", "description": "<description>"}'
    ),
    agent=agent
)

crew = Crew(agents=[agent], tasks=[task])


async def generate_listing(description: str):
    result = await asyncio.to_thread(crew.kickoff, inputs={"product_description": description})
    return result

