import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def draft_blog_post(topic, research_data):
    prompt = (
        f"Using the following research data, draft a comprehensive blog post on the topic '{topic}':\n\n"
        f"{research_data}\n\n"
        "Ensure the blog post is well-structured, engaging, and suitable for a general audience."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a skilled blog post writer."},
            {"role": "user", "content": prompt}
        ],
    )
    draft = response['choices'][0]['message']['content']
    return draft
