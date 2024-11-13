import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def optimize_seo(draft, topic):
    prompt = (
        f"Optimize the following blog post for SEO on the topic '{topic}'. "
        "Include relevant keywords, meta descriptions, and ensure proper formatting for SEO:\n\n"
        f"{draft}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an SEO specialist."},
            {"role": "user", "content": prompt}
        ],
    )
    seo_optimized_content = response['choices'][0]['message']['content']
    return seo_optimized_content
