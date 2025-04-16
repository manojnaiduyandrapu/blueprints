import os
import asyncio
import json
import re
from dotenv import load_dotenv
import docx
import PyPDF2
from loguru import logger
from models import CandidateData
from agentifyme.ml.llm import (
    LanguageModelConfig,
    LanguageModelType,
    get_language_model,
)

load_dotenv(dotenv_path=".env")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not found. Please set it in the .env file.")

def extract_text_from_file(file_path: str) -> str:
    """
    Extracts text from a resume file.

    Args:
        file_path (str): The path to the resume file.

    Returns:
        str: Extracted text from the resume.
    """
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    try:
        if file_extension in ['.doc', '.docx']:
            doc = docx.Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            logger.info("Extracted text from DOC/DOCX file.")
            return text
        elif file_extension == '.pdf':
            reader = PyPDF2.PdfReader(file_path)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
            logger.info(f"Extracted text from PDF file with {len(reader.pages)} pages.")
            return text
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info("Extracted text from TXT file.")
            return text
        else:
            logger.error(f"Unsupported file format: {file_extension}")
            raise ValueError("Unsupported file format. Please provide a .doc, .docx, .pdf, or .txt file.")
    except Exception as e:
        logger.error(f"Error extracting text from file: {e}")
        raise

async def process_resume_text(resume_text: str) -> CandidateData:
    """
    Asynchronously processes resume text using the language model to extract structured data.

    Args:
        resume_text (str): The plain text content of the resume.

    Returns:
        CandidateData: Parsed resume details as a Pydantic model.
    """
    logger.info("Sending resume text to the language model for processing.")
    prompt_content = (
        "You are a resume extractor that strictly extracts candidate details from the resume text provided below. "
        "Do not invent any details. Extract and return only the fields specified in valid JSON format: "
        "{'contact': {'first_name': '', 'last_name': '', 'middle_name': '', 'phone_number': '', 'email': '', 'linkedin': ''}, "
        "'education': [{'degree': '', 'year': '', 'college': ''}], "
        "'skills': {'programming_languages': [], 'frameworks_libraries': [], 'tools_technologies': []}, "
        "'experience': [{'company_client': '', 'job_role': '', 'summary_of_responsibilities': '', 'place': '', 'start_date': '', 'end_date': ''}]}. "
        "Resume Text:\n"
        f"{resume_text}\n\n"
        "Return the valid JSON exactly matching the given schema without any additional text."
    )
    try:
        # Configure and retrieve the language model.
        config = LanguageModelConfig(
            model=LanguageModelType.OPENAI_GPT4o_MINI,
            json_mode=False
        )
        llm = get_language_model(config)
        system_prompt = "You are an expert resume parser who extracts candidate details accurately."

        response = await asyncio.to_thread(
            llm.generate_from_prompt,
            prompt=prompt_content,
            system_prompt=system_prompt,
            max_tokens=4096,
        )
        if not response.message:
            logger.error("The language model returned an empty response.")
            raise ValueError("Empty response received from language model.")

        resume_data_json = response.message.strip()
        logger.info(f"Extracted JSON string before code fence extraction: '{resume_data_json}'")
        json_match = re.search(r'```json\s*(.*?)\s*```', resume_data_json, re.DOTALL)
        if json_match:
            resume_data_json = json_match.group(1).strip()
            logger.info("Extracted JSON string from code fences.")

        resume_data_dict = json.loads(resume_data_json)

        resume_data = CandidateData(**resume_data_dict)
        logger.info("Resume text processed successfully.")
        return resume_data

    except json.JSONDecodeError as json_err:
        logger.error(f"JSON decode error: {json_err}")
        raise
    except Exception as e:
        logger.error(f"Error processing resume text with language model: {e}")
        raise

async def extract_resume_workflow(file_path: str) -> dict:
    """
    Asynchronous workflow to extract structured data from a resume file.

    Args:
        file_path (str): The path to the resume file.

    Returns:
        dict: Parsed resume details.
    """
    logger.info("Starting resume extraction workflow.")
    resume_text = await asyncio.to_thread(extract_text_from_file, file_path)
    parsed_resume_data = await process_resume_text(resume_text)
    logger.info("Resume extraction workflow completed successfully.")
    return parsed_resume_data.dict()

async def main(file_path: str):
    try:
        result = await extract_resume_workflow(file_path)
        print(json.dumps(result, indent=4)) 
    except Exception as e:
        logger.error(f"Failed to extract resume data: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    file_path = "Swetha.docx"
    asyncio.run(main(file_path))
