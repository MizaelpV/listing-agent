from crewai import Agent, Task, Crew, LLM
import asyncio
from dotenv import load_dotenv
from app.tools.category_tool import CategoryFinderTool

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
    llm=llm,
    tools=[CategoryFinderTool()],
    verbose=True
)

task = Task(
      description=(
        "Create a product listing for: {product_description}. "
        "You MUST use the MeLi Category Finder tool first to find the correct category. "
        "Do not generate the listing without calling the tool. "
        "Steps: 1) Call the tool with the product title. 2) Pick the best category from the results. "
        "3) Generate title and description based on the category context."
    ),
    expected_output=(
        'A valid JSON object: '
        '{"title": "<title>", "description": "<description>", "category_id": "<category_id>", "category_name": "<category_name>"}'

    ),
    agent=agent
)

crew = Crew(agents=[agent], tasks=[task], verbose=True)




async def generate_listing(description: str):
    result = await asyncio.to_thread(crew.kickoff, inputs={"product_description": description})
    return result

