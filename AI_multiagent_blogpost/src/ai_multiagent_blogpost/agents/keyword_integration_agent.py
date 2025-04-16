# agents/keyword_integration_agent.py

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

async def integrate_keywords(research_data: str, keywords: str) -> str:
    """
    Integrates the provided SEO keywords into the research data to ensure SEO optimization.
    """
    try:
        prompt = (
            "Integrate the following keywords into the research data to ensure SEO optimization.\n\n"
            f"Keywords:\n{keywords}\n\n"
            f"Research Data:\n{research_data}\n\n"
            "Provide the integrated research data with keywords seamlessly embedded."
        )
        
        config = LanguageModelConfig(
            model=LanguageModelType.OPENAI_GPT4o_MINI,
            json_mode=False
        )
        llm = get_language_model(config)
        
        system_prompt = "You are an SEO content strategist."
        
        response = await llm.generate_from_prompt_async(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
        )
        
        if response.message is None:
            logger.error("Failed to integrate keywords")
            return None
            
        integrated_data = response.message.strip()
        logger.info("Keywords integrated successfully")
        return integrated_data
        
    except Exception as e:
        logger.error(f"Error integrating keywords: {e}")
        raise