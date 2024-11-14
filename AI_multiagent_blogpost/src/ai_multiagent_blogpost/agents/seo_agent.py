# agents/seo_agent.py

import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_keywords(topic):
    """
    Generates a list of general and long-tail SEO keywords based on the provided topic.
    
    Parameters:
        topic (str): The topic of the blog post.
    
    Returns:
        str: A comma-separated string of generated keywords.
    """
    prompt = (
        f"Generate a list of general and long-tail keywords for the blog topic: '{topic}'. "
        "Provide them in a comma-separated format, categorizing general keywords and long-tail keywords separately."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an SEO specialist."},
            {"role": "user", "content": prompt}
        ],
    )
    keywords = response['choices'][0]['message']['content']
    return keywords.strip()
