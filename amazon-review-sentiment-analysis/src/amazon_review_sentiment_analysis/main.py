import re
import pandas as pd
from collections import defaultdict
import os
import sys
from dotenv import load_dotenv
import json
import asyncio
from typing import Dict, List
from agentifyme.ml.llm import (
    LanguageModelConfig,
    LanguageModelType,
    get_language_model,
)
from loguru import logger

load_dotenv()

def read_reviews(file_path):
    """
    Reads the review.txt file and extracts the product name and individual reviews.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        product_match = re.search(r'Product Name:\s*(.*?)\n\n', content, re.DOTALL)
        product_name = product_match.group(1).strip() if product_match else 'Unknown Product'
        reviews = re.findall(r'\d+\)\s*(.*?)(?=\n\d+\)|$)', content, re.DOTALL)
        reviews = [review.strip().replace('\n', ' ') for review in reviews]
        logger.info(f"Successfully read {len(reviews)} reviews for product: {product_name}")
        return product_name, reviews
    except Exception as e:
        logger.error(f"Error reading reviews file: {e}")
        raise

def extract_json_from_text(text):
    """
    Extracts JSON from text, handling various formats including code fences.
    """
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        logger.info("Extracted JSON from code fences")
        return json_match.group(1).strip()
    json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
    if json_match:
        logger.info("Extracted JSON array directly")
        return json_match.group(0)
    return text

async def extract_keywords_sentiment(review: str) -> List[Dict[str, str]]:
    """
    Analyzes a review to extract keywords and their sentiment using agentifyme LLM.
    """
    try:
        prompt = f"""
        Analyze the following product review and extract the key keywords along with their sentiment (Positive, Negative, Neutral).

        Review:
        "{review}"

        Please provide the results in the following exact JSON format without any additional text or comments:

        [
            {{"keyword": "example_keyword", "sentiment": "Positive"}},
            {{"keyword": "another_keyword", "sentiment": "Negative"}}
        ]
        """
        
        config = LanguageModelConfig(
            model=LanguageModelType.OPENAI_GPT4o_MINI,
            json_mode=True
        )
        llm = get_language_model(config)
        
        system_prompt = "You are a helpful assistant that analyzes product reviews for sentiment."
        
        response = await llm.generate_from_prompt_async(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1024,
        )
        
        if response.message is None:
            logger.error("Failed to analyze review")
            return []
        
        json_text = extract_json_from_text(response.message.strip())
        try:
            keywords = json.loads(json_text)
            if isinstance(keywords, list) and all('keyword' in item and 'sentiment' in item for item in keywords):
                logger.info(f"Successfully extracted {len(keywords)} keywords from review")
                return keywords
            else:
                logger.error("Invalid JSON structure in response")
                return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response.message}")
            return []
    except Exception as e:
        logger.error(f"Error analyzing review: {e}")
        return []

def aggregate_keywords(all_keywords):
    """
    Aggregates keywords and counts their sentiment occurrences.
    """
    try:
        keyword_sentiment = defaultdict(lambda: {'Positive': 0, 'Negative': 0, 'Neutral': 0})
        for keywords in all_keywords:
            for item in keywords:
                keyword = item['keyword'].lower()
                sentiment = item['sentiment']
                if sentiment not in ['Positive', 'Negative', 'Neutral']:
                    sentiment = 'Neutral' 
                keyword_sentiment[keyword][sentiment] += 1
        logger.info(f"Successfully aggregated {len(keyword_sentiment)} unique keywords")
        return keyword_sentiment  
    except Exception as e:
        logger.error(f"Error aggregating keywords: {e}")
        raise

async def process_reviews(reviews: List[str]) -> List[List[Dict[str, str]]]:
    """
    Process reviews concurrently with a limit on concurrency.
    """
    semaphore = asyncio.Semaphore(5)
    async def process_with_semaphore(review):
        async with semaphore:
            return await extract_keywords_sentiment(review)
    tasks = [process_with_semaphore(review) for review in reviews]
    logger.info(f"Processing {len(reviews)} reviews concurrently...")
    results = await asyncio.gather(*tasks)
    
    return results

async def main_async(file_path: str = 'reviews.txt'):
    """
    Main async function to process reviews and analyze sentiment.
    """
    logger.info("Starting product review analysis")
    
    if not os.path.exists(file_path):
        logger.error(f"File {file_path} does not exist. Please check the path.")
        return
    
    try:
        # Step 1: Read and parse the reviews
        product_name, reviews = read_reviews(file_path)
        logger.info(f"Product Name: {product_name}")
        logger.info(f"Number of Reviews: {len(reviews)}")
        
        # Step 2: Process all reviews concurrently
        all_keywords = await process_reviews(reviews)
        
        # Step 3: Aggregate the results
        aggregated = aggregate_keywords(all_keywords)
        
        # Convert to DataFrame for better visualization
        df = pd.DataFrame([
            {'Keyword': keyword, 'Positive': counts['Positive'], 'Negative': counts['Negative'], 'Neutral': counts['Neutral']}
            for keyword, counts in aggregated.items()
        ])
        
        # Sort by total mentions
        df['Total'] = df['Positive'] + df['Negative'] + df['Neutral']
        df = df.sort_values(by='Total', ascending=False).drop(columns=['Total'])
        
        # Step 4: Output the results
        logger.success("Analysis completed successfully")
        print("\n=== Aggregated Keyword Sentiment Analysis ===\n")
        print(df)
        
        return {
            "product_name": product_name,
            "total_reviews": len(reviews),
            "results_df": df
        }
    
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return None

def main(file_path: str = None):
    """
    Entry point for the application.
    
    Args:
        file_path: Optional path to the reviews file.
    """
    try:
        file_path = file_path or 'reviews.txt'
        return asyncio.run(main_async(file_path))
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception("Critical error occurred")
        sys.exit(1)

if __name__ == "__main__":
    main()