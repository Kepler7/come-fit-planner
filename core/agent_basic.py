# core/agent_basic.py
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat

from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    instructions=(
        "Eres un nutriólogo del restaurante Come Fit. "
        "Respondes en español, de forma clara y breve."
    ),
    markdown=True,
)

def test_agent():
    # Mensaje de prueba
    prompt = (
        "Imagina que soy un cliente de Come Fit y quiero un menú de ejemplo "
        "para déficit calórico de unas 1600 kcal en 3 comidas."
    )
    run = agent.run(prompt)
    # Según la versión de agno, run puede devolver un objeto o string.
    # Lo más común es que tenga .content:
    try:
        print(run.content)
    except AttributeError:
        print(run)


if __name__ == "__main__":
    test_agent()