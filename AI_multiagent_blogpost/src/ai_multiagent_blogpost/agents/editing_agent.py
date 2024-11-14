# agents/editing_agent.py

import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def edit_draft(draft):
    """
    Refines the blog post draft for clarity, grammar, and style while maintaining the original meaning.
    
    Parameters:
        draft (str): The initial draft of the blog post.
    
    Returns:
        str: The edited and refined blog post content.
    """
    prompt = (
        "Improve the following blog post for clarity, grammar, and style while maintaining the original meaning:\n\n"
        "I want the content to read much punchier and to be more bold. eliminate fluff and words that waste time"
        "make it more humanized"
        f"{draft}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert editor."},
            {"role": "user", "content": prompt}
        ],
    )
    edited_draft = response['choices'][0]['message']['content']
    return edited_draft.strip()
