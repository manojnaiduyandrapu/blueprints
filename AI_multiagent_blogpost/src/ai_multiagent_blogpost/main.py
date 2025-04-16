import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

from agentifyme import workflow
from agentifyme.ml.llm import (
    LanguageModelConfig,
    LanguageModelType,
    get_language_model,
)
from agentifyme.workflows import WorkflowExecutionError
from loguru import logger

load_dotenv(dotenv_path=".env")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not found. Please set it in the .env file.")


async def construct_email_prompt(recipient: Dict[str, str], subject: str) -> str:
    """
    Asynchronously constructs the prompt for email generation.
    """
    prompt = f"""Generate a personalized professional email based on the following specifications:

RECIPIENT INFORMATION:
- Name: {recipient['name']}
- Relationship: {recipient['relationship']}
- Purpose: {recipient['purpose']}
- Tone: {recipient['tone']}

EMAIL SUBJECT: {subject}

REQUIREMENTS:
1. Begin with an appropriate greeting using the recipient's name
2. Write a concise and focused email body that directly addresses the purpose
3. Maintain a consistent {recipient['tone']} tone throughout
4. Include specific details relevant to the purpose
5. End with a clear call-to-action if appropriate
6. Add a professional closing with your name

The email should be well-structured, grammatically correct, and appropriate for professional communication.
"""
    logger.info("Email prompt constructed")
    return prompt


async def generate_email_content(prompt_text: str) -> str:
    """
    Asynchronously generates email content using a language model.
    Wraps the synchronous generate_from_prompt call into a thread.
    """
    try:
        config = LanguageModelConfig(
            model=LanguageModelType.OPENAI_GPT4o_MINI,
            json_mode=False
        )
        llm = get_language_model(config)

        system_prompt = "You are an expert email writer who specializes in creating effective professional communications."

        response = await asyncio.to_thread(
            llm.generate_from_prompt,
            prompt=prompt_text,
            system_prompt=system_prompt,
            max_tokens=4096,
        )

        if response.message is None:
            logger.error("Failed to generate email content")
            return None

        email_content = response.message.strip()
        logger.info("Email content generated successfully")
        return email_content

    except Exception as e:
        logger.error(f"Error generating email: {e}")
        raise


@workflow(name="generate_email", description="Generate a personalized email based on recipient details and subject")
async def generate_email_workflow(recipient_data: Dict[str, str], subject: str) -> Dict[str, Any]:
    """
    Asynchronous workflow to generate a personalized email.
    """
    try:
        prompt = await construct_email_prompt(recipient_data, subject)
        email_content = await generate_email_content(prompt)

        if not email_content:
            raise ValueError("Failed to generate email content")

        return {
            "email_content": email_content,
            "recipient": recipient_data["name"],
            "subject": subject,
            "status": "success"
        }

    except Exception as e:
        logger.exception(f"Email generation workflow failed: {e}")
        raise WorkflowExecutionError(f"Error in email generation workflow: {e}")


async def main(recipient: Dict[str, str], subject: str):
    try:
        result = await generate_email_workflow(recipient, subject)
        print("\n=== Generated Email ===\n")
        print(result["email_content"])

    except WorkflowExecutionError as e:
        print(f"❌ Workflow execution failed: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    recipient = {
        "name": "John Smith",
        "relationship": "colleague",
        "purpose": "project update",
        "tone": "professional"
    }
    subject = "Weekly Project Status Update"
    
    # Passing recipient and subject directly to main.
    asyncio.run(main(recipient, subject))
