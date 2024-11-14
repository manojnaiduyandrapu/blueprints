# main.py

import argparse
import sys

# Importing agent functions from the agents package
from agents.seo_agent import generate_keywords
from agents.content_outline_agent import generate_content_outline
from agents.research_agent import research_topic
from agents.keyword_integration_agent import integrate_keywords
from agents.drafting_agent import draft_blog_post
from agents.editing_agent import edit_draft
from agents.fact_checking_agent import fact_check
from agents.seo_optimization_agent import optimize_seo

def create_blog_post(topic):
    """
    Orchestrates the blog post creation process by sequentially invoking
    each agent and passing the necessary data between them.
    
    Parameters:
        topic (str): The topic of the blog post.
    
    Returns:
        tuple: Contains the final SEO-optimized blog post and the generated keywords.
    """
    print("\nStarting blog post creation process...\n")
    
    # 1. SEO Agent: Generate Keywords
    print("1. Generating SEO keywords...")
    keywords = generate_keywords(topic)
    print("SEO Keywords Generated:\n")
    
    # 2. Content Outline Agent: Build Content Outline
    print("2. Creating content outline...")
    outline = generate_content_outline(keywords, topic)
    print("Content Outline Generated:\n")
    
    # 3. Research Agent: Gather Information
    print("3. Researching topic based on outline...")
    research_data = research_topic(outline)
    print("Research completed.\n")
    
    # 4. Keyword Integration Agent: Embed Keywords into Research Data
    print("4. Integrating keywords into research data...")
    integrated_research = integrate_keywords(research_data, keywords)
    print("Keyword Integration completed.\n")
    
    # 5. Drafting Agent: Create Initial Draft
    print("5. Drafting blog post...")
    draft = draft_blog_post(topic, integrated_research)
    print("Drafting completed.\n")
    
    # 6. Editing Agent: Refine Draft
    print("6. Editing draft...")
    edited_draft = edit_draft(draft)
    print("Editing completed.\n")
    
    # 7. Fact-Checking Agent: Verify Facts
    print("7. Fact-checking draft...")
    fact_checked_draft = fact_check(edited_draft)
    print("Fact-checking completed.\n")
    
    # 8. SEO Optimization Agent: Final SEO Enhancements
    print("8. Optimizing for SEO...")
    seo_content = optimize_seo(fact_checked_draft, keywords)
    print("SEO Optimization completed.\n")
    
    print("Blog post creation process completed.\n")
    return seo_content, keywords

def get_topic():
    """
    Retrieves the blog topic either from command-line arguments or prompts the user.
    
    Returns:
        str: The blog topic.
    """
    parser = argparse.ArgumentParser(description="Multi-Agent Blog Post Writer")
    parser.add_argument(
        'topic',
        type=str,
        nargs='?',
        help='The topic for the blog post'
    )
    args = parser.parse_args()

    if args.topic:
        return args.topic.strip()
    else:
        return input("Please enter the blog topic: ").strip()

def main():
    """
    The main function that initiates the blog post creation process.
    """
    topic = get_topic()
    
    if not topic:
        print("Error: Blog topic cannot be empty. Please provide a valid topic.")
        sys.exit(1)
    
    final_blog_post, keywords = create_blog_post(topic)
    
    # Display the Final Blog Post
    print("----- Final Blog Post -----\n")
    print(final_blog_post)
    print("\n----- End of Blog Post -----\n")
    
    # Display Keywords
    #print("----- SEO Keywords -----\n")
    #print(keywords)
    #print("\n")

if __name__ == "__main__":
    print("Welcome to the Multi-Agent Blog Post Writer!\n")
    main()
