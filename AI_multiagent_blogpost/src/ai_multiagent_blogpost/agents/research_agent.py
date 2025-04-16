# agents/research_agent.py

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

async def research_topic(outline: str) -> str:
    """
    Gathers detailed information, data, and references based on the provided content outline.
    """
    try:
        prompt = (
            f"Based on the following content outline, gather detailed information, data, and references for each section. "
            "Ensure that the information is accurate, up-to-date, and relevant to the topic.\n\n"
            f"Content Outline:\n{outline}\n\n"
            "Provide the research data in a structured format aligned with the outline."
        )
        
        config = LanguageModelConfig(
            model=LanguageModelType.OPENAI_GPT4o_MINI,
            json_mode=False
        )
        llm = get_language_model(config)
        
        system_prompt = "You are a comprehensive research assistant."
        
        response = await llm.generate_from_prompt_async(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
        )
        
        if response.message is None:
            logger.error("Failed to research topic")
            return None
            
        research_data = response.message.strip()
        logger.info("Topic research completed successfully")
        return research_data
        
    except Exception as e:
        logger.error(f"Error researching topic: {e}")
        raise