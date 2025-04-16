# agents/seo_agent.py

import os
from dotenv import load_dotenv
from agentifyme.ml.llm import (
    LanguageModelConfig,
    LanguageModelType,
    get_language_model,
)
from loguru import logger

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not found. Please set it in the .env file.")

async def generate_keywords(topic: str) -> str:
    """
    Generates a list of general and long-tail SEO keywords based on the provided topic.
    """
    try:
        prompt = (
            f"Generate a list of general and long-tail keywords for the blog topic: '{topic}'. "
            "Provide them in a comma-separated format, categorizing general keywords and long-tail keywords separately."
        )
        
        config = LanguageModelConfig(
            model=LanguageModelType.OPENAI_GPT4o_MINI,
            json_mode=False
        )
        llm = get_language_model(config)
        
        system_prompt = "You are an SEO specialist."
        
        response = await llm.generate_from_prompt_async(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1024,
        )
        
        if response.message is None:
            logger.error("Failed to generate keywords")
            return None
            
        keywords = response.message.strip()
        logger.info("Keywords generated successfully")
        return keywords
        
    except Exception as e:
        logger.error(f"Error generating keywords: {e}")
        raise