# agents/content_outline_agent.py

import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_content_outline(keywords, topic):
    """
    Creates a detailed content outline for the blog post based on the provided keywords and topic.
    
    Parameters:
        keywords (str): A comma-separated string of SEO keywords.
        topic (str): The topic of the blog post.
    
    Returns:
        str: A structured content outline with headers and bullet points.
    """
    prompt = (
        f"Given the following keywords: {keywords}, create a detailed content outline for an article about '{topic}'. "
        "The outline should include all headers for the blog post and bullet points of questions to answer and areas to cover for each section. "
        "Use the following guidelines:\n"
        "- The blog should be around 3000 words.\n"
        "- Tone should be creative, friendly, and helpful.\n"
        "- Audience: creators looking to build an email list and eventually use an email marketing software to grow their list.\n"
        "- Prioritize the main keywords."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a skilled content strategist."},
            {"role": "user", "content": prompt}
        ],
    )
    outline = response['choices'][0]['message']['content']
    return outline.strip()
