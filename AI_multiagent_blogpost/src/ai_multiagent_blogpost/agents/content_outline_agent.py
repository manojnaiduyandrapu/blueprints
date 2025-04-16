# agents/content_outline_agent.py

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

async def generate_content_outline(keywords: str, topic: str) -> str:
    """
    Creates a detailed content outline for the blog post based on the provided keywords and topic.
    """
    try:
        prompt = (
            f"Given the following keywords: {keywords}, create a detailed content outline for an article about '{topic}'. "
            "The outline should include all headers for the blog post and bullet points of questions to answer and areas to cover for each section. "
            "Use the following guidelines:\n"
            "- The blog should be around 3000 words.\n"
            "- Tone should be creative, friendly, and helpful.\n"
            "- Audience: creators looking to build an email list and eventually use an email marketing software to grow their list.\n"
            "- Prioritize the main keywords."
        )
        
        config = LanguageModelConfig(
            model=LanguageModelType.OPENAI_GPT4o_MINI,
            json_mode=False
        )
        llm = get_language_model(config)
        
        system_prompt = "You are a skilled content strategist."
        
        response = await llm.generate_from_prompt_async(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2048,
        )
        
        if response.message is None:
            logger.error("Failed to generate content outline")
            return None
            
        outline = response.message.strip()
        logger.info("Content outline generated successfully")
        return outline
        
    except Exception as e:
        logger.error(f"Error generating content outline: {e}")
        raise