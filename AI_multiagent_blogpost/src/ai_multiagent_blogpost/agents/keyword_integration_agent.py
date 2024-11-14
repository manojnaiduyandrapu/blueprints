# agents/keyword_integration_agent.py

import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def integrate_keywords(research_data, keywords):
    """
    Integrates the provided SEO keywords into the research data to ensure SEO optimization.
    
    Parameters:
        research_data (str): The detailed research information aligned with the content outline.
        keywords (str): A comma-separated string of SEO keywords.
    
    Returns:
        str: The research data with keywords seamlessly embedded.
    """
    prompt = (
        "Integrate the following keywords into the research data to ensure SEO optimization.\n\n"
        f"Keywords:\n{keywords}\n\n"
        f"Research Data:\n{research_data}\n\n"
        "Provide the integrated research data with keywords seamlessly embedded."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an SEO content strategist."},
            {"role": "user", "content": prompt}
        ],
    )
    integrated_data = response['choices'][0]['message']['content']
    return integrated_data.strip()
