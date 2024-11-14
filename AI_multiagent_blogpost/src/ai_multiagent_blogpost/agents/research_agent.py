# agents/research_agent.py

import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def research_topic(outline):
    """
    Gathers detailed information, data, and references based on the provided content outline.
    
    Parameters:
        outline (str): The structured content outline of the blog post.
    
    Returns:
        str: Comprehensive research data aligned with the content outline.
    """
    prompt = (
        f"Based on the following content outline, gather detailed information, data, and references for each section. "
        "Ensure that the information is accurate, up-to-date, and relevant to the topic.\n\n"
        f"Content Outline:\n{outline}\n\n"
        "Provide the research data in a structured format aligned with the outline."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a comprehensive research assistant."},
            {"role": "user", "content": prompt}
        ],
    )
    research_data = response['choices'][0]['message']['content']
    return research_data.strip()
