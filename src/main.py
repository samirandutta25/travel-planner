from dotenv import load_dotenv
from pprint import pprint
import logging

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from src.services import get_coordinates, get_weather

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an friendly weather forecaster.

You have access to two tools:
- get_weather: use this to get the weather for next 7 days using latitude and longitude
- get_coordinates: use this to get the location's latitude and longitude

Make sure location is mentioned in the prompt
"""

load_dotenv()
logger.info("Setting up model!")
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.5,
    timeout=None,
    max_retries=2,
    base_url="https://models.inference.ai.azure.com",  # GitHub Models endpoint
)
logger.info("preparing the agent")
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_coordinates, get_weather]
)

response = agent.invoke(
        {"messages": [{"role": "user", "content": "I prefer max temperatures lower than 30 degrees Celcius, "
        "which of these 3 Digha, Puri and Darjeeling will be better on 18th April."}]},
        config={"configurable": {"thread_id": "1"}}
    )
# pprint(response)

print(response["messages"][-1].content)