# agents/fact_checking_agent.py

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

async def fact_check(draft: str) -> str:
    """
    Reviews the blog post draft for factual accuracy, identifying and correcting any inaccuracies.
    """
    try:
        prompt = (
            "Review the following blog post draft for factual accuracy. "
            "- Only use quotes or facts that you're able to verify. "
            "- Do not tell lies or make up facts. "
            "Identify any statements that may be incorrect or require verification and provide corrected information where necessary.\n\n"
            f"Draft:\n{draft}"
        )
        
        config = LanguageModelConfig(
            model=LanguageModelType.OPENAI_GPT4o_MINI,
            json_mode=False
        )
        llm = get_language_model(config)
        
        system_prompt = "You are a meticulous fact-checker."
        
        response = await llm.generate_from_prompt_async(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
        )
        
        if response.message is None:
            logger.error("Failed to fact check draft")
            return None
            
        fact_checked_draft = response.message.strip()
        logger.info("Fact checking completed successfully")
        return fact_checked_draft
        
    except Exception as e:
        logger.error(f"Error fact checking draft: {e}")
        raise