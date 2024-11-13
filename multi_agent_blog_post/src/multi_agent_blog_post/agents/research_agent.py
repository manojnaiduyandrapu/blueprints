import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

openai.api_key = os.getenv("OPENAI_API_KEY")

def research_topic(topic):
    prompt = f"Provide a comprehensive overview of the topic: {topic} with key points and references."
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a research assistant."},
            {"role": "user", "content": prompt}
        ],
    )
    research_data = response['choices'][0]['message']['content']
    return research_data
