import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def edit_draft(draft):
    prompt = (
        "Improve the following blog post for clarity, grammar, and style while maintaining the original meaning:\n\n"
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
    return edited_draft
