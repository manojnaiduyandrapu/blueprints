# agents/drafting_agent.py

import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def draft_blog_post(topic, integrated_research):
    """
    Creates the initial draft of the blog post using the integrated research data.
    
    Parameters:
        topic (str): The topic of the blog post.
        integrated_research (str): The research data with embedded SEO keywords.
    
    Returns:
        str: The drafted blog post content.
    """
    prompt = (
        f"Using the following integrated research data, draft a comprehensive blog post on the topic '{topic}':\n\n"
        f"{integrated_research}\n\n"
        "Ensure the blog post is well-structured, creative, friendly, and helpful. Aim for a length of approximately 3000 words."
        "Note : the bullet points in each section should be fleshed more into their own mini-sections so there is greater depth of content"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a skilled blog post writer."},
            {"role": "user", "content": prompt}
        ],
    )
    draft = response['choices'][0]['message']['content']
    return draft.strip()
