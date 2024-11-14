# agents/seo_optimization_agent.py

import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def optimize_seo(draft, keywords):
    """
    Optimizes the blog post for SEO by ensuring proper keyword density, including meta descriptions, and formatting the content.
    
    Parameters:
        draft (str): The fact-checked draft of the blog post.
        keywords (str): A comma-separated string of SEO keywords.
    
    Returns:
        str: The SEO-optimized blog post content.
    """
    prompt = (
        "Optimize the following blog post for SEO. "
        "Ensure proper keyword density, include meta descriptions, and format the content for better SEO performance.\n\n"
        f"Keywords:\n{keywords}\n\n"
        f"Draft:\n{draft}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an SEO specialist."},
            {"role": "user", "content": prompt}
        ],
    )
    seo_optimized_content = response['choices'][0]['message']['content']
    return seo_optimized_content.strip()
