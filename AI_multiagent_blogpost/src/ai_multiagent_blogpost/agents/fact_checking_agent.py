# agents/fact_checking_agent.py

import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def fact_check(draft):
    """
    Reviews the blog post draft for factual accuracy, identifying and correcting any inaccuracies.
    
    Parameters:
        draft (str): The edited draft of the blog post.
    
    Returns:
        str: The fact-checked blog post content with corrections where necessary.
    """
    prompt = (
        "Review the following blog post draft for factual accuracy. "
        "- Only use quotes or facts that you're able to verify."
        "- Do not tell lies or make up tacts"
        "Identify any statements that may be incorrect or require verification and provide corrected information where necessary.\n\n"
        f"Draft:\n{draft}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a meticulous fact-checker."},
            {"role": "user", "content": prompt}
        ],
    )
    fact_checked_draft = response['choices'][0]['message']['content']
    return fact_checked_draft.strip()
