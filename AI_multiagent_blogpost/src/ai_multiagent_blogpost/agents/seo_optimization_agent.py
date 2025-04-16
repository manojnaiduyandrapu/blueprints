# agents/seo_optimization_agent.py

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

async def optimize_seo(draft: str, keywords: str) -> str:
    """
    Optimizes the blog post for SEO by ensuring proper keyword density, including meta descriptions, and formatting the content.
    """
    try:
        prompt = (
            "Optimize the following blog post for SEO. "
            "Ensure proper keyword density, include meta descriptions, and format the content for better SEO performance.\n\n"
            f"Keywords:\n{keywords}\n\n"
            f"Draft:\n{draft}"
            "Important: Make sure there are no **, #, or other markdown formatting. make it plain text. "
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
            max_tokens=4096,
        )
        
        if response.message is None:
            logger.error("Failed to optimize SEO")
            return None
            
        seo_optimized_content = response.message.strip()
        logger.info("SEO optimization completed successfully")
        return seo_optimized_content
        
    except Exception as e:
        logger.error(f"Error optimizing SEO: {e}")
        raise