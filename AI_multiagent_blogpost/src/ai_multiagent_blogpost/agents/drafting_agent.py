# agents/drafting_agent.py

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

async def draft_blog_post(topic: str, integrated_research: str) -> str:
    """
    Creates the initial draft of the blog post using the integrated research data.
    """
    try:
        prompt = (
            f"Using the following integrated research data, draft a comprehensive blog post on the topic '{topic}':\n\n"
            f"{integrated_research}\n\n"
            "Ensure the blog post is well-structured, creative, friendly, and helpful. Aim for a length of approximately 3000 words. "
            "Note: the bullet points in each section should be fleshed more into their own mini-sections so there is greater depth of content."
        )
        
        config = LanguageModelConfig(
            model=LanguageModelType.OPENAI_GPT4o_MINI,
            json_mode=False
        )
        llm = get_language_model(config)
        
        system_prompt = "You are a skilled blog post writer."
        
        response = await llm.generate_from_prompt_async(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
        )
        
        if response.message is None:
            logger.error("Failed to draft blog post")
            return None
            
        draft = response.message.strip()
        logger.info("Blog post drafted successfully")
        return draft
        
    except Exception as e:
        logger.error(f"Error drafting blog post: {e}")
        raise