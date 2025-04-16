# agents/editing_agent.py

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

async def edit_draft(draft: str) -> str:
    """
    Refines the blog post draft for clarity, grammar, and style while maintaining the original meaning.
    """
    try:
        prompt = (
            "Improve the following blog post for clarity, grammar, and style while maintaining the original meaning:\n\n"
            "I want the content to read much punchier and to be more bold. eliminate fluff and words that waste time. "
            "make it more humanized. "
            f"{draft}"
        )
        
        config = LanguageModelConfig(
            model=LanguageModelType.OPENAI_GPT4o_MINI,
            json_mode=False
        )
        llm = get_language_model(config)
        
        system_prompt = "You are an expert editor."
        
        response = await llm.generate_from_prompt_async(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
        )
        
        if response.message is None:
            logger.error("Failed to edit draft")
            return None
            
        edited_draft = response.message.strip()
        logger.info("Draft edited successfully")
        return edited_draft
        
    except Exception as e:
        logger.error(f"Error editing draft: {e}")
        raise