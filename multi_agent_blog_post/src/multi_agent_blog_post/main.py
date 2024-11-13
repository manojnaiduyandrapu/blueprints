# orchestrator.py

import argparse
import sys
from agents.research_agent import research_topic
from agents.drafting_agent import draft_blog_post
from agents.editing_agent import edit_draft
from agents.seo_agent import optimize_seo

def create_blog_post(topic):
    print("\nStarting blog post creation process...\n")
    
    print("1. Researching topic...")
    research_data = research_topic(topic)
    print("Research completed.\n")
    
    print("2. Drafting blog post...")
    draft = draft_blog_post(topic, research_data)
    print("Drafting completed.\n")
    
    print("3. Editing draft...")
    edited_draft = edit_draft(draft)
    print("Editing completed.\n")
    
    print("4. Optimizing for SEO...")
    seo_content = optimize_seo(edited_draft, topic)
    print("SEO Optimization completed.\n")
    
    print("Blog post creation process completed.\n")
    return seo_content

def get_topic():
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
    topic = get_topic()
    
    if not topic:
        print("Error: Blog topic cannot be empty. Please provide a valid topic.")
        sys.exit(1)
    
    final_blog_post = create_blog_post(topic)
    print("----- Final Blog Post -----\n")
    print(final_blog_post)
    print("\n----- End of Blog Post -----")

if __name__ == "__main__":
    print("Welcome to the Multi-Agent Blog Post Writer!\n")
    main()
